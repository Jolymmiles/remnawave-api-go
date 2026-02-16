#!/usr/bin/env python3
"""
Smart Schema Consolidation
==========================

Intelligent consolidation of duplicate OpenAPI schemas with smart naming.

Key improvements over basic consolidation:
1. Semantic analysis of schema names to find common entity
2. Priority-based canonical name selection
3. Automatic detection of Response/Request/List types
4. No manual rename_map needed
"""

import copy
import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional


class SchemaStructureAnalyzer:
    """Analyzes schema structure to find duplicates based on attributes"""
    
    @classmethod
    def get_structural_signature(cls, schema: dict, depth: int = 0, include_constraints: bool = True) -> str:
        """
        Generate a structural signature for a schema, ignoring metadata.
        This allows finding schemas with identical structure but different descriptions.
        
        Args:
            schema: The schema to analyze
            depth: Current recursion depth
            include_constraints: If True, include validation constraints (minLength, pattern, etc.)
                               If False, only compare type structure
        """
        if not isinstance(schema, dict):
            return str(schema)
        
        sig_parts = []
        
        # Type
        if 'type' in schema:
            sig_parts.append(f"type={schema['type']}")
        
        # Format
        if 'format' in schema:
            sig_parts.append(f"format={schema['format']}")
        
        # $ref
        if '$ref' in schema:
            sig_parts.append(f"ref={schema['$ref']}")
        
        # Validation constraints (if enabled)
        if include_constraints:
            for constraint in ['minLength', 'maxLength', 'minimum', 'maximum', 
                             'pattern', 'minItems', 'maxItems', 'uniqueItems']:
                if constraint in schema:
                    sig_parts.append(f"{constraint}={schema[constraint]}")
        
        # Properties (sorted by name, recursive)
        if 'properties' in schema:
            props = []
            for prop_name, prop_def in sorted(schema['properties'].items()):
                prop_sig = cls.get_structural_signature(prop_def, depth + 1, include_constraints)
                nullable = prop_def.get('nullable', False)
                props.append(f"{prop_name}:{prop_sig}:n={nullable}")
            sig_parts.append(f"props=[{';'.join(props)}]")
        
        # Required fields
        if 'required' in schema:
            sig_parts.append(f"req={sorted(schema['required'])}")
        
        # Enum values
        if 'enum' in schema:
            sig_parts.append(f"enum={sorted(str(e) for e in schema['enum'])}")
        
        # Array items
        if 'items' in schema:
            sig_parts.append(f"items={cls.get_structural_signature(schema['items'], depth + 1, include_constraints)}")
        
        # AllOf/OneOf/AnyOf
        for key in ['allOf', 'oneOf', 'anyOf']:
            if key in schema:
                sigs = sorted(cls.get_structural_signature(s, depth + 1, include_constraints) for s in schema[key])
                sig_parts.append(f"{key}=[{';'.join(sigs)}]")
        
        # AdditionalProperties
        if 'additionalProperties' in schema:
            ap = schema['additionalProperties']
            if isinstance(ap, dict):
                sig_parts.append(f"addProps={cls.get_structural_signature(ap, depth + 1, include_constraints)}")
            else:
                sig_parts.append(f"addProps={ap}")
        
        return '|'.join(sig_parts)
    
    @classmethod
    def get_attribute_set(cls, schema: dict) -> frozenset:
        """
        Get the set of attribute names in a schema (for quick comparison).
        """
        if not isinstance(schema, dict):
            return frozenset()
        
        attrs = set()
        if 'properties' in schema:
            for prop_name, prop_def in schema['properties'].items():
                prop_type = prop_def.get('type', 'ref' if '$ref' in prop_def else 'unknown')
                attrs.add((prop_name, prop_type))
        
        return frozenset(attrs)
    
    @classmethod
    def compare_schemas(cls, schema1: dict, schema2: dict) -> dict:
        """
        Compare two schemas and return similarity metrics.
        
        Returns:
            dict with keys:
                - exact_match: bool - identical JSON
                - structural_match: bool - same structure ignoring metadata
                - attribute_match: float - Jaccard similarity of attributes (0-1)
                - missing_in_1: set - attributes in schema2 but not schema1
                - missing_in_2: set - attributes in schema1 but not schema2
        """
        exact = json.dumps(schema1, sort_keys=True) == json.dumps(schema2, sort_keys=True)
        structural = cls.get_structural_signature(schema1) == cls.get_structural_signature(schema2)
        
        attrs1 = cls.get_attribute_set(schema1)
        attrs2 = cls.get_attribute_set(schema2)
        
        if attrs1 or attrs2:
            intersection = attrs1 & attrs2
            union = attrs1 | attrs2
            jaccard = len(intersection) / len(union) if union else 1.0
        else:
            jaccard = 1.0 if exact else 0.0
        
        return {
            'exact_match': exact,
            'structural_match': structural,
            'attribute_match': jaccard,
            'missing_in_1': attrs2 - attrs1,
            'missing_in_2': attrs1 - attrs2,
        }


class SchemaNameAnalyzer:
    """Analyzes schema names to extract semantic information"""

    # Operations that return lists
    LIST_INDICATORS = {'GetAll', 'FindAll', 'List', 'Bulk'}
    
    @staticmethod
    def remove_dto_suffix(name: str) -> str:
        """Remove Dto suffix but keep Response/Request"""
        return re.sub(r'Dto$', '', name)
    
    @staticmethod
    def extract_type_suffix(name: str) -> str:
        """Extract Response/Request type"""
        if 'Response' in name:
            return 'Response'
        elif 'Request' in name:
            return 'Request'
        elif 'Body' in name:
            return 'Request'  # Body is usually a request
        return ''
    
    @classmethod
    def extract_entity(cls, name: str) -> Tuple[str, str, bool]:
        """
        Extract entity name, action type, and whether it's a list operation.
        
        Returns: (entity, action_type, is_list)
        """
        clean = cls.remove_dto_suffix(name)
        type_suffix = cls.extract_type_suffix(name)
        
        # Check if it's a list operation
        is_list = any(indicator in clean for indicator in cls.LIST_INDICATORS)
        
        # Patterns to extract entity (ordered by specificity)
        patterns = [
            # GetUserByXxx -> User
            (r'^Get(\w+?)By\w+$', 1),
            # GetOneUser -> User
            (r'^GetOne(\w+)$', 1),
            # GetAllUsers -> User (remove trailing 's')
            (r'^GetAll(\w+?)s?$', 1),
            # CreateUser -> User
            (r'^Create(\w+)$', 1),
            # UpdateUser -> User
            (r'^Update(\w+)$', 1),
            # DeleteUser -> User
            (r'^Delete(\w+)$', 1),
            # DisableUser -> User
            (r'^Disable(\w+)$', 1),
            # EnableUser -> User
            (r'^Enable(\w+)$', 1),
            # ResetUserTraffic -> User
            (r'^Reset(\w+?)(?:Traffic|Data|State)$', 1),
            # RevokeUserSubscription -> User
            (r'^Revoke(\w+?)Subscription$', 1),
            # RestartNode -> Node
            (r'^Restart(\w+)$', 1),
            # BulkDeleteUsers -> User
            (r'^Bulk(?:All)?(?:Delete|Update|Reset|Revoke|Enable|Disable)(\w+?)s?$', 1),
            # AddUsersToSquad -> Squad (operation on squad)
            (r'^(?:Add|Remove)\w+To(\w+)$', 1),
            (r'^(?:Add|Remove)\w+From(\w+)$', 1),
            # ReorderNodes -> Node
            (r'^Reorder(\w+?)s?$', 1),
            # SetInboundToManyHosts -> Host
            (r'^Set\w+ToMany(\w+?)s?$', 1),
            # VerifyPasskeyAuthentication -> Passkey
            (r'^Verify(\w+?)(?:Authentication|Registration)$', 1),
            # GetPasskeyAuthenticationOptions -> Passkey
            (r'^Get(\w+?)(?:Authentication|Registration)Options$', 1),
            # LoginResponse -> Auth
            (r'^(Login|Register|OAuth2Callback|TelegramCallback)$', 0),
        ]
        
        for pattern, group in patterns:
            match = re.match(pattern, clean)
            if match:
                if group == 0:
                    # Special case: Auth-related
                    return 'Token', 'auth', is_list
                entity = match.group(group)
                # Remove trailing 's' for plural
                if entity.endswith('s') and len(entity) > 3:
                    entity = entity[:-1]
                return entity, 'crud', is_list
        
        # Fallback: try to extract meaningful name
        # Remove common prefixes
        for prefix in ['Get', 'Create', 'Update', 'Delete', 'Find', 'Fetch']:
            if clean.startswith(prefix):
                clean = clean[len(prefix):]
                break
        
        return clean, 'unknown', is_list
    
    @classmethod
    def analyze_group(cls, names: List[str]) -> Dict:
        """Analyze a group of duplicate schema names"""
        entities = []
        types = set()
        is_list_group = False
        actions = set()
        
        for name in names:
            entity, action, is_list = cls.extract_entity(name)
            entities.append(entity)
            types.add(cls.extract_type_suffix(name))
            is_list_group = is_list_group or is_list
            actions.add(action)
        
        # Find most common entity
        entity_counts = defaultdict(int)
        for e in entities:
            entity_counts[e] += 1
        
        primary_entity = max(entity_counts.keys(), key=lambda x: (entity_counts[x], -len(x)))
        
        # Determine response type
        has_response = 'Response' in types
        has_request = 'Request' in types
        
        return {
            'entity': primary_entity,
            'is_response': has_response and not has_request,
            'is_request': has_request and not has_response,
            'is_mixed': has_response and has_request,
            'is_list': is_list_group,
            'actions': actions,
            'all_entities': list(set(entities)),
        }


class SmartConsolidator:
    """Smart schema consolidation with intelligent naming"""

    # Schema name pairs that must NEVER be consolidated, even if structurally identical.
    # Each entry is a frozenset of schema names that should remain separate.
    DO_NOT_MERGE = [
        frozenset({'CreateExternalSquadRequestDto', 'CreateSubscriptionPageConfigRequestDto'}),
    ]

    # Known entity groupings (for disambiguation)
    ENTITY_GROUPS = {
        # Auth-related
        'Token': {'Login', 'Register', 'OAuth2Callback', 'TelegramCallback', 'VerifyPasskeyAuthentication'},
        # Settings
        'Settings': {'RemnawaveSettings', 'SubscriptionSettings'},
    }
    
    # Special naming rules - ordered by specificity (most specific first)
    # Check if MAJORITY of names in group match the pattern
    SPECIAL_PATTERNS = {
        # === HIGH PRIORITY: Specific patterns ===
        
        # Event responses (async operations) - very specific pattern
        'EventResponse': [
            r'^BulkAll\w+Response',
            r'^(Add|Remove)UsersTo\w+Response',
            r'^(Add|Remove)UsersFrom\w+Response', 
            r'^Restart(All)?Node\w*Response',
            r'^ResetNodeTrafficResponse',
        ],
        # Delete responses (simple success) - only Delete* prefix
        'DeleteResponse': [
            r'^Delete\w+Response',
        ],
        # Bulk action results (user operations)
        'BulkActionResponse': [
            r'^Bulk(Delete|Reset|Revoke|Update)Users\w*Response',
        ],
        # Bulk UUID requests
        'BulkUuidsRequest': [
            r'^Bulk(Delete|Disable|Enable|Reset|Revoke)\w+Request',
        ],
        # Reorder requests
        'ReorderRequest': [
            r'^Reorder\w+Request',
        ],
        # Token/Auth responses
        'TokenResponse': [
            r'^(Login|Register|OAuth2Callback|TelegramCallback|VerifyPasskeyAuthentication)Response',
        ],
        # Passkey options (mixed request/response with same structure)
        'PasskeyOptions': [
            r'^(Get|Verify)Passkey(Authentication|Registration)(Options)?(Response)?$',
            r'^VerifyPasskey(Authentication|Registration)Request',
        ],
        # Tags list response
        'TagsResponse': [
            r'^GetAll\w*Tags\w*Response',
        ],
        # Inbounds list
        'InboundsResponse': [
            r'^(GetAllInbounds|GetInboundsBy\w+)Response',
        ],
        # Subscription response (single)
        'SubscriptionResponse': [
            r'^GetSubscription(By\w+|Info)\w*Response',
        ],
        # Settings responses
        'SettingsResponse': [
            r'^(Get|Update)RemnawaveSettings\w*Response',
        ],
        'SubscriptionSettingsResponse': [
            r'^(Get|Update)SubscriptionSettings\w*Response',
        ],
        # Passkeys list
        'PasskeysResponse': [
            r'^(GetAllPasskeys|DeletePasskey|UpdatePasskey)\w*Response',
        ],
        # Snippet request
        'SnippetRequest': [
            r'^(Create|Update)Snippet\w*Request',
        ],
        # Snippets response  
        'SnippetsResponse': [
            r'^(Create|Update|Delete|Get)Snippets?\w*Response',
        ],
        
        # === MEDIUM PRIORITY: Entity-specific patterns ===
        
        # Users list response (multiple users) - MUST BE BEFORE UserResponse!
        'UsersResponse': [
            r'^GetUserBy(Email|Tag|TelegramId)\w*Response',
        ],
        # User single responses (CRUD on single user)
        'UserResponse': [
            r'^(Create|Update|Disable|Enable)UserResponse',
            r'^GetUserBy(Uuid|Username|ShortUuid)\w*Response',
            r'^(Reset|Revoke)User\w+Response',
        ],
        # Host list responses  
        'HostListResponse': [
            r'^GetAllHostsResponse',
            r'^Bulk(Delete|Disable|Enable)HostsResponse',
            r'^Set\w+ToManyHostsResponse',
        ],
        # Host single response
        'HostResponse': [
            r'^(Create|Update|GetOne)HostResponse',
        ],
        # Node responses (single)
        'NodeResponse': [
            r'^(Create|Update|GetOne|Disable|Enable)NodeResponse',
        ],
        # Nodes list
        'NodesResponse': [
            r'^(GetAllNodes|ReorderNode)Response',
        ],
        # Template single response
        'TemplateResponse': [
            r'^(Create|Update|Get)(?:Subscription)?TemplateResponse',
        ],
        # Templates list response
        'TemplatesResponse': [
            r'^(GetTemplates|Reorder\w+Templates)Response',
        ],
        # Config profile single
        'ConfigProfileResponse': [
            r'^(Create|Update|Get(Computed)?ConfigProfileBy\w+)Response',
        ],
        # Config profiles list
        'ConfigProfilesResponse': [
            r'^(GetConfigProfiles|ReorderConfigProfiles)Response',
        ],
        # Internal squad single
        'InternalSquadResponse': [
            r'^(Create|Update|GetInternalSquadBy\w+)Response',
        ],
        # Internal squads list
        'InternalSquadsResponse': [
            r'^(GetInternalSquads|ReorderInternalSquads)Response',
        ],
        # External squad single
        'ExternalSquadResponse': [
            r'^(Create|Update|GetExternalSquadBy\w+)Response',
        ],
        # External squads list
        'ExternalSquadsResponse': [
            r'^(GetExternalSquads|ReorderExternalSquads)Response',
        ],
        # Infra provider
        'InfraProviderResponse': [
            r'^(Create|Update|GetInfraProviderBy\w+)Response',
        ],
        # Billing nodes
        'BillingNodesResponse': [
            r'^(Create|Update|Delete|Get)InfraBillingNode\w*Response',
        ],
        # Billing history
        'BillingHistoryResponse': [
            r'^(Create|Delete|Get)InfraBillingHistoryRecord\w*Response',
        ],
        # HWID devices
        'HwidDevicesResponse': [
            r'^(Create|Delete(All)?|Get)UserHwidDevice\w*Response',
        ],
    }
    
    def __init__(self, spec: dict):
        self.spec = spec
        self.schemas = spec.get('components', {}).get('schemas', {})
        self.name_analyzer = SchemaNameAnalyzer()
        self.structure_analyzer = SchemaStructureAnalyzer()
    
    def find_duplicates(self, mode: str = 'exact') -> Dict[str, List[str]]:
        """
        Find duplicate schemas.
        
        Args:
            mode: 'exact' - identical JSON content (default)
                  'structural' - same structure ignoring metadata (description, example)
                  'attributes' - same attribute names and types
        """
        if mode == 'exact':
            return self._find_exact_duplicates()
        elif mode == 'structural':
            return self._find_structural_duplicates()
        elif mode == 'attributes':
            return self._find_attribute_duplicates()
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def _find_exact_duplicates(self) -> Dict[str, List[str]]:
        """Find duplicate schemas by exact JSON content"""
        content_to_names = defaultdict(list)
        
        for name, schema_def in self.schemas.items():
            content = json.dumps(schema_def, sort_keys=True)
            content_to_names[content].append(name)
        
        return {k: v for k, v in content_to_names.items() if len(v) > 1}
    
    def _find_structural_duplicates(self, include_constraints: bool = True) -> Dict[str, List[str]]:
        """Find duplicate schemas by structure (ignoring metadata like descriptions)"""
        sig_to_names = defaultdict(list)
        
        for name, schema_def in self.schemas.items():
            sig = self.structure_analyzer.get_structural_signature(
                schema_def, include_constraints=include_constraints
            )
            sig_to_names[sig].append(name)
        
        return {k: v for k, v in sig_to_names.items() if len(v) > 1}
    
    def _find_attribute_duplicates(self) -> Dict[str, List[str]]:
        """Find duplicate schemas by attribute set (name + type pairs)"""
        attrs_to_names = defaultdict(list)
        
        for name, schema_def in self.schemas.items():
            attrs = self.structure_analyzer.get_attribute_set(schema_def)
            attrs_to_names[attrs].append(name)
        
        return {k: v for k, v in attrs_to_names.items() if len(v) > 1}
    
    def analyze_duplicates(self) -> Dict:
        """
        Analyze duplicates at all levels and return comprehensive report.
        
        Returns dict with:
            - exact: Identical JSON content
            - structural: Same structure with constraints (safe to consolidate)
            - structural_loose: Same structure without constraints (may have different validation)
            - attribute: Same attribute names/types (different structure possible)
            - near_duplicates: Structural matches that aren't exact (metadata differs)
            - constraint_only: Schemas that differ only in validation constraints
        """
        exact = self._find_exact_duplicates()
        structural = self._find_structural_duplicates(include_constraints=True)
        structural_loose = self._find_structural_duplicates(include_constraints=False)
        attribute = self._find_attribute_duplicates()
        
        # Find near-duplicates (structural but not exact)
        exact_groups = set(frozenset(v) for v in exact.values())
        near_duplicates = {}
        for sig, names in structural.items():
            names_set = frozenset(names)
            if names_set not in exact_groups:
                near_duplicates[sig] = names
        
        # Find constraint-only differences (structural_loose but not structural)
        structural_groups = set(frozenset(v) for v in structural.values())
        constraint_only = {}
        for sig, names in structural_loose.items():
            names_set = frozenset(names)
            if names_set not in structural_groups and len(names) > 1:
                constraint_only[sig] = names
        
        return {
            'exact': {
                'count': len(exact),
                'total_schemas': sum(len(v) for v in exact.values()),
                'groups': exact,
            },
            'structural': {
                'count': len(structural),
                'total_schemas': sum(len(v) for v in structural.values()),
                'groups': structural,
            },
            'structural_loose': {
                'count': len(structural_loose),
                'total_schemas': sum(len(v) for v in structural_loose.values()),
                'groups': structural_loose,
            },
            'attribute': {
                'count': len(attribute),
                'total_schemas': sum(len(v) for v in attribute.values()),
                'groups': attribute,
            },
            'near_duplicates': {
                'count': len(near_duplicates),
                'total_schemas': sum(len(v) for v in near_duplicates.values()),
                'groups': near_duplicates,
            },
            'constraint_only': {
                'count': len(constraint_only),
                'total_schemas': sum(len(v) for v in constraint_only.values()),
                'groups': constraint_only,
            },
        }
    
    def generate_canonical_name(self, names: List[str]) -> str:
        """Generate best canonical name for a group of duplicates"""
        
        clean_names = [self.name_analyzer.remove_dto_suffix(n) for n in names]
        
        # Count how many names match each pattern
        pattern_scores = {}
        for canonical_name, patterns in self.SPECIAL_PATTERNS.items():
            matches = 0
            for pattern in patterns:
                for clean_name in clean_names:
                    if re.match(pattern, clean_name):
                        matches += 1
            if matches > 0:
                # Score = percentage of names that match
                pattern_scores[canonical_name] = matches / len(names)
        
        # Choose pattern with highest coverage (if > 50% match)
        if pattern_scores:
            best_pattern = max(pattern_scores.keys(), key=lambda x: pattern_scores[x])
            if pattern_scores[best_pattern] >= 0.5:
                return best_pattern
        
        # Fallback: analyze the group semantically
        analysis = self.name_analyzer.analyze_group(names)
        entity = analysis['entity']
        
        # Build canonical name
        if analysis['is_request']:
            if analysis['is_list'] or 'Bulk' in str(names):
                return f'{entity}BulkRequest'
            return f'{entity}Request'
        elif analysis['is_response']:
            if analysis['is_list']:
                return f'{entity}ListResponse'
            return f'{entity}Response'
        else:
            # Mixed or unclear
            return entity
    
    def consolidate(self) -> Tuple[Dict[str, str], Dict]:
        """
        Consolidate duplicate schemas.
        
        Returns: (rename_map, stats)
        """
        duplicates = self.find_duplicates()
        rename_map = {}
        used_canonical_names = set()
        stats = {
            'original_count': len(self.schemas),
            'duplicate_groups': len(duplicates),
            'consolidated_names': {},
        }
        
        for content, names in duplicates.items():
            # Check DO_NOT_MERGE: split the group if it contains schemas that must stay separate
            names_set = set(names)
            must_split = False
            for exclusion in self.DO_NOT_MERGE:
                if exclusion.issubset(names_set):
                    must_split = True
                    break

            if must_split:
                # Exclude the protected schemas from this group
                excluded = set()
                for exclusion in self.DO_NOT_MERGE:
                    if exclusion.issubset(names_set):
                        excluded.update(exclusion)
                remaining = [n for n in names if n not in excluded]
                # Only consolidate the remaining names (if 2+)
                if len(remaining) < 2:
                    continue
                names = remaining

            canonical = self.generate_canonical_name(names)

            # Ensure unique canonical names - if already used, make unique
            base_canonical = canonical
            counter = 2
            while canonical in used_canonical_names:
                canonical = f"{base_canonical}{counter}"
                counter += 1
            
            used_canonical_names.add(canonical)
            stats['consolidated_names'][canonical] = names
            
            for name in names:
                rename_map[name] = canonical
        
        # Calculate actual reduction from rename_map (accounts for DO_NOT_MERGE splits)
        renamed_count = len(rename_map)
        canonical_count = len(set(rename_map.values()))
        stats['final_count'] = len(self.schemas) - renamed_count + canonical_count
        stats['reduction'] = stats['original_count'] - stats['final_count']
        
        return rename_map, stats
    
    def apply_consolidation(self, rename_map: Dict[str, str]) -> dict:
        """Apply consolidation to the spec"""
        new_spec = copy.deepcopy(self.spec)
        
        # Update schemas
        new_schemas = {}
        for name, schema_def in new_spec['components']['schemas'].items():
            canonical = rename_map.get(name, name)
            if canonical not in new_schemas:
                new_schemas[canonical] = schema_def
        
        new_spec['components']['schemas'] = new_schemas
        
        # Update all $ref references
        def update_refs(obj):
            if isinstance(obj, dict):
                for key, value in list(obj.items()):
                    if key == '$ref' and isinstance(value, str):
                        if value.startswith('#/components/schemas/'):
                            old_name = value.replace('#/components/schemas/', '')
                            new_name = rename_map.get(old_name, old_name)
                            obj[key] = f'#/components/schemas/{new_name}'
                    else:
                        update_refs(value)
            elif isinstance(obj, list):
                for item in obj:
                    update_refs(item)
        
        update_refs(new_spec)
        
        return new_spec


class InlineSchemaExtractor:
    """
    Extracts inline schemas into $ref definitions to enable ogen reuse.
    
    For example, if UserResponse.response and UsersResponse.response[].item
    have the same structure, extract it as a shared schema.
    
    Also handles deeply nested inline schemas like:
    - GetExternalSquadsResponseDto.response.externalSquads[].subscriptionSettings
    - CreateUserResponseDto.response.activeInternalSquads[]
    """
    
    def __init__(self, spec: dict):
        self.spec = copy.deepcopy(spec)
        self.schemas = self.spec.get('components', {}).get('schemas', {})
        self.structure_analyzer = SchemaStructureAnalyzer()
    
    def get_inline_schema_signature(self, schema: dict) -> Optional[str]:
        """Get structural signature for an inline object schema"""
        if not isinstance(schema, dict):
            return None
        if schema.get('type') != 'object' or 'properties' not in schema:
            return None
        return self.structure_analyzer.get_structural_signature(schema)
    
    def find_all_inline_schemas(self) -> Dict[str, List[Tuple[str, str, dict]]]:
        """
        Find ALL inline object schemas across all schema definitions at any depth.
        
        Returns: {signature: [(parent_schema, property_path, inline_schema), ...]}
        """
        inline_schemas = defaultdict(list)
        
        def extract_recursive(parent_name: str, obj: dict, path: str = ""):
            """Recursively extract all inline object schemas"""
            if not isinstance(obj, dict):
                return
            
            # Check properties
            if 'properties' in obj:
                for prop_name, prop_schema in obj['properties'].items():
                    prop_path = f"{path}.{prop_name}" if path else prop_name
                    
                    # Direct inline object
                    if prop_schema.get('type') == 'object' and 'properties' in prop_schema:
                        # Skip empty objects (no meaningful properties to share)
                        if not prop_schema['properties']:
                            continue
                        sig = self.get_inline_schema_signature(prop_schema)
                        if sig:
                            inline_schemas[sig].append((parent_name, prop_path, prop_schema))
                        # Recurse into nested properties
                        extract_recursive(parent_name, prop_schema, prop_path)
                    
                    # Array of inline objects
                    elif prop_schema.get('type') == 'array':
                        items = prop_schema.get('items', {})
                        if items.get('type') == 'object' and 'properties' in items:
                            # Skip empty objects
                            if not items['properties']:
                                continue
                            sig = self.get_inline_schema_signature(items)
                            if sig:
                                inline_schemas[sig].append((parent_name, f"{prop_path}[]", items))
                            # Recurse into array item properties
                            extract_recursive(parent_name, items, f"{prop_path}[]")
        
        for schema_name, schema_def in self.schemas.items():
            extract_recursive(schema_name, schema_def)
        
        # Return only groups with duplicates (2+ occurrences)
        return {k: v for k, v in inline_schemas.items() if len(v) >= 2}
    
    def generate_extracted_name(self, locations: List[Tuple[str, str, dict]]) -> str:
        """Generate a name for extracted schema based on usage locations"""
        
        parent_names = [loc[0] for loc in locations]
        paths = [loc[1] for loc in locations]
        
        # If all paths are "response" or "response[]", use parent entity
        if all(p in ('response', 'response[]') for p in paths):
            entities = []
            for name in parent_names:
                clean = name.replace('Response', '').replace('Request', '').replace('Dto', '')
                for prefix in ['Create', 'Update', 'Get', 'Delete', 'Bulk', 'GetAll', 'GetOne']:
                    if clean.startswith(prefix):
                        clean = clean[len(prefix):]
                        break
                if clean:
                    entities.append(clean)
            
            if entities:
                common = Counter(entities).most_common(1)[0][0]
                is_array = any('[]' in p for p in paths)
                if is_array:
                    return f"{common}Item"
                return common
        
        # Extract last property name from paths
        last_props = []
        for path in paths:
            parts = path.replace('[]', '').split('.')
            last_prop = parts[-1] if parts else ''
            if last_prop and last_prop != 'response':
                last_props.append(last_prop)
        
        if last_props:
            common_prop = Counter(last_props).most_common(1)[0][0]
            # Capitalize first letter
            name = common_prop[0].upper() + common_prop[1:] if common_prop else common_prop
            
            # Generic names need context from parent entity
            generic_names = {'Config', 'Items', 'Data', 'Info', 'Details', 'Settings', 
                           'Options', 'Params', 'Json', 'Object', 'Value', 'Item'}
            if name in generic_names or name.endswith('Item'):
                # Extract entity context from parent schemas
                entities = []
                for parent in parent_names:
                    clean = parent.replace('ResponseDto', '').replace('RequestDto', '').replace('Dto', '')
                    for prefix in ['Create', 'Update', 'Get', 'Delete', 'Bulk', 'GetAll', 'GetOne', 
                                  'GetRaw', 'Subscription', 'By', 'All']:
                        if clean.startswith(prefix):
                            clean = clean[len(prefix):]
                    # Take first meaningful word
                    if clean:
                        entities.append(clean[:20])  # Limit length
                
                if entities:
                    common_entity = Counter(entities).most_common(1)[0][0]
                    # Extract just the entity name (e.g., "SubscriptionByShortUuid" -> "Subscription")
                    for suffix in ['ByShortUuid', 'ByUuid', 'ByUsername', 'ByEmail', 'ById']:
                        common_entity = common_entity.replace(suffix, '')
                    name = f"{common_entity}{name}"
            
            # Check if array item
            is_array = any('[]' in p for p in paths)
            if is_array and not name.endswith('Item') and not name.endswith('s'):
                name = f"{name}Item"
            
            # Remove trailing 's' for arrays (users[] -> User)
            if is_array and name.endswith('s') and len(name) > 3 and not name.endswith('Settings'):
                name = name[:-1]
            
            return name
        
        # Fallback: use first parent + path
        first_parent = parent_names[0].replace('ResponseDto', '').replace('RequestDto', '').replace('Dto', '')
        first_path = paths[0].replace('[]', '').split('.')[-1]
        return f"{first_parent}{first_path[0].upper() + first_path[1:] if first_path else ''}"
    
    def _resolve_conflict_suffix(self, base_name: str, locations: List[Tuple[str, str, dict]], 
                                   all_groups: List[Tuple[str, List]]) -> str:
        """
        Generate a unique suffix for a conflicting schema name based on context.
        """
        paths = [loc[1] for loc in locations]
        parents = [loc[0] for loc in locations]
        
        # Helper to check patterns
        def has_pattern(pattern, in_paths=True, in_parents=False):
            if in_paths:
                return any(pattern in p for p in paths)
            if in_parents:
                return any(pattern in p for p in parents)
            return False
        
        # Context-based suffix rules
        rules = [
            # Request types (CreateNodeRequestDto.configProfile -> ConfigProfileRef)
            (lambda: any('Request' in p for p in parents) and not any('Response' in p for p in parents), 'Ref'),
            
            # Delete response (simple object with isDeleted field)
            (lambda: any('Delete' in p for p in parents) and base_name == 'User', 'Deleted'),
            
            # Subscription user info (nested .user field)
            (lambda: any('.user' in p for p in paths), 'Info'),
            
            # Subscription settings in squads vs global settings
            (lambda: base_name == 'SubscriptionSettings' and has_pattern('Squad', in_parents=True), 'Squad'),
            
            # Templates in squads vs standalone templates
            (lambda: base_name == 'Template' and has_pattern('Squad', in_parents=True), 'Ref'),
            
            # Billing records vs subscription request history records
            (lambda: base_name == 'Record' and has_pattern('Billing', in_parents=True), 'Billing'),
            
            # Snippets response vs snippet items
            (lambda: base_name == 'Snippet' and has_pattern('snippets[]', in_paths=True), 'Item'),
            
            # Inbounds in config profiles vs standalone inbounds
            (lambda: base_name == 'Inbound' and has_pattern('GetAllInbounds', in_parents=True), 'Full'),
            (lambda: base_name == 'Inbound' and has_pattern('.inbound', in_paths=True) and not has_pattern('inbounds[]', in_paths=True), 'Embed'),
            
            # Nodes in reorder requests
            (lambda: base_name == 'Node' and has_pattern('Reorder', in_parents=True), 'Order'),
            
            # Billing nodes in providers vs standalone
            (lambda: base_name == 'BillingNode' and has_pattern('Provider', in_parents=True), 'Ref'),
            
            # Provider in different contexts
            (lambda: base_name == 'ProviderItem' and has_pattern('BillingHistory', in_parents=True), 'HistoryRef'),
            (lambda: base_name == 'ProviderItem' and has_pattern('BillingNode', in_parents=True), 'BillingRef'),
        ]
        
        for condition, suffix in rules:
            try:
                if condition():
                    return suffix
            except Exception:
                pass
        
        return ""
    
    def extract_inline_schemas(self) -> Tuple[dict, Dict]:
        """
        Extract duplicate inline schemas into shared definitions.
        Processes from deepest to shallowest to avoid conflicts.
        Handles name conflicts by adding context-based suffixes.
        
        Returns: (new_spec, stats)
        """
        duplicates = self.find_all_inline_schemas()
        
        if not duplicates:
            return self.spec, {'extracted_count': 0, 'extracted_schemas': {}}
        
        # First pass: group by generated name to detect conflicts
        name_to_groups = defaultdict(list)
        for sig, locations in duplicates.items():
            base_name = self.generate_extracted_name(locations)
            name_to_groups[base_name].append((sig, locations))
        
        # Sort by path depth (deepest first) to avoid replacing parent before child
        sorted_duplicates = sorted(
            duplicates.items(),
            key=lambda x: -max(loc[1].count('.') + loc[1].count('[]') for loc in x[1])
        )
        
        extracted_schemas = {}
        extraction_log = {}
        sig_to_name = {}  # Map signature to final name for conflict resolution
        
        # Resolve name conflicts
        for base_name, groups in name_to_groups.items():
            if len(groups) == 1:
                # No conflict
                sig, locations = groups[0]
                sig_to_name[sig] = base_name
            else:
                # Conflict: need unique names for each structure
                used_suffixes = set()
                for i, (sig, locations) in enumerate(groups):
                    suffix = self._resolve_conflict_suffix(base_name, locations, groups)
                    
                    # If suffix already used or empty, use index
                    if not suffix or suffix in used_suffixes:
                        suffix = str(i + 1) if i > 0 else ""
                    
                    used_suffixes.add(suffix)
                    final_name = f"{base_name}{suffix}" if suffix else base_name
                    sig_to_name[sig] = final_name
        
        for sig, locations in sorted_duplicates:
            # Get resolved name
            extracted_name = sig_to_name.get(sig, self.generate_extracted_name(locations))
            
            # Ensure unique name (safety check for edge cases)
            base_name = extracted_name
            counter = 2
            while extracted_name in self.schemas or extracted_name in extracted_schemas:
                extracted_name = f"{base_name}{counter}"
                counter += 1
            
            # Use first schema as the definition
            schema_def = copy.deepcopy(locations[0][2])
            extracted_schemas[extracted_name] = schema_def
            extraction_log[extracted_name] = [f"{loc[0]}.{loc[1]}" for loc in locations]
            
            # Replace all occurrences with $ref
            for parent_name, prop_path, _ in locations:
                self._replace_with_ref(parent_name, prop_path, extracted_name)
        
        # Add extracted schemas to spec
        self.spec['components']['schemas'].update(extracted_schemas)
        
        return self.spec, {
            'extracted_count': len(extracted_schemas),
            'extracted_schemas': extraction_log
        }
    
    def _replace_with_ref(self, schema_name: str, prop_path: str, ref_name: str):
        """Replace inline schema at path with $ref"""
        schema = self.schemas.get(schema_name)
        if not schema:
            return
        
        parts = prop_path.replace('[]', '.[]').split('.')
        parts = [p for p in parts if p]  # Remove empty strings
        
        current = schema
        for i, part in enumerate(parts[:-1]):
            if part == '[]':
                current = current.get('items', {})
            elif 'properties' in current:
                current = current['properties'].get(part, {})
            else:
                return
        
        last_part = parts[-1]
        if last_part == '[]':
            # Replace array items
            current['items'] = {'$ref': f'#/components/schemas/{ref_name}'}
        elif 'properties' in current and last_part in current['properties']:
            # Replace property
            current['properties'][last_part] = {'$ref': f'#/components/schemas/{ref_name}'}


def fix_nullable_without_type(spec: dict) -> Tuple[dict, int]:
    """
    Fix schema properties that have 'nullable: true' but no 'type' field.
    Ogen generates invalid code for such properties.
    
    For empty objects with nullable: true, we use x-ogen-name with {} to make ogen
    generate jx.Raw type which properly handles null values.
    
    Returns: (spec, count_of_fixed_properties)
    """
    spec = copy.deepcopy(spec)
    fixed_count = 0
    
    def is_empty_object(schema: dict) -> bool:
        """Check if schema is an empty object (type: object with no/empty properties)"""
        if schema.get('type') != 'object':
            return False
        props = schema.get('properties', {})
        return len(props) == 0
    
    def fix_schema(schema: dict, path: str = "") -> int:
        """Recursively fix nullable properties without type"""
        count = 0
        
        if not isinstance(schema, dict):
            return 0
        
        # For nullable empty objects (or nullable without type), convert to {} (any JSON)
        # This makes ogen generate jx.Raw which properly handles null
        if schema.get('nullable') is True and 'type' not in schema and '$ref' not in schema:
            # No type → treat as empty object, strip to bare {nullable: true}
            schema.pop('properties', None)
            count += 1
        elif schema.get('nullable') is True and is_empty_object(schema):
            # Has type: object but no properties → strip to bare {nullable: true}
            schema.pop('properties', None)
            schema.pop('type', None)
            count += 1
        
        # Recurse into properties
        if 'properties' in schema:
            for prop_name, prop_def in schema['properties'].items():
                if isinstance(prop_def, dict):
                    count += fix_schema(prop_def, f"{path}.properties.{prop_name}")
        
        # Recurse into items
        if 'items' in schema and isinstance(schema['items'], dict):
            count += fix_schema(schema['items'], f"{path}.items")
        
        # Recurse into allOf/oneOf/anyOf
        for key in ['allOf', 'oneOf', 'anyOf']:
            if key in schema:
                for i, sub_schema in enumerate(schema[key]):
                    if isinstance(sub_schema, dict):
                        count += fix_schema(sub_schema, f"{path}.{key}[{i}]")
        
        # Recurse into additionalProperties
        if 'additionalProperties' in schema and isinstance(schema['additionalProperties'], dict):
            count += fix_schema(schema['additionalProperties'], f"{path}.additionalProperties")
        
        return count
    
    # Fix schemas in components
    for schema_name, schema_def in spec.get('components', {}).get('schemas', {}).items():
        fixed_count += fix_schema(schema_def, f"#/components/schemas/{schema_name}")
    
    # Fix inline schemas in paths
    for path, methods in spec.get('paths', {}).items():
        for method, op in methods.items():
            if not isinstance(op, dict):
                continue
            
            # Fix request body
            if 'requestBody' in op:
                for content_type, content in op['requestBody'].get('content', {}).items():
                    if 'schema' in content:
                        fixed_count += fix_schema(content['schema'], f"paths.{path}.{method}.requestBody")
            
            # Fix responses
            for status, response in op.get('responses', {}).items():
                if isinstance(response, dict):
                    for content_type, content in response.get('content', {}).items():
                        if 'schema' in content:
                            fixed_count += fix_schema(content['schema'], f"paths.{path}.{method}.responses.{status}")
    
    return spec, fixed_count


def unify_error_responses(spec: dict) -> Tuple[dict, Dict]:
    """
    Unify duplicate error response schemas (400 BadRequest, 401 Unauthorized, etc.)
    by extracting common inline schemas into shared definitions.
    
    Returns: (new_spec, stats)
    """
    spec = copy.deepcopy(spec)
    
    # Define common error schemas to extract
    ERROR_SCHEMAS = {
        'BadRequestError': {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'statusCode': {'type': 'number', 'example': 400},
                'errors': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/components/schemas/ValidationError'
                    }
                }
            },
            'required': ['message', 'statusCode', 'errors']
        },
        'ValidationError': {
            'type': 'object',
            'properties': {
                'validation': {'type': 'string', 'example': 'uuid'},
                'code': {'type': 'string', 'example': 'invalid_string'},
                'message': {'type': 'string', 'example': 'Invalid uuid'},
                'path': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'example': ['uuid']
                }
            },
            'required': ['validation', 'code', 'message', 'path']
        },
        'UnauthorizedError': {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'example': 'Unauthorized'},
                'statusCode': {'type': 'number', 'example': 401}
            },
            'required': ['message', 'statusCode']
        },
        'ForbiddenError': {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'example': 'Forbidden'},
                'statusCode': {'type': 'number', 'example': 403}
            },
            'required': ['message', 'statusCode']
        },
        'NotFoundError': {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'example': 'Not Found'},
                'statusCode': {'type': 'number', 'example': 404}
            },
            'required': ['message', 'statusCode']
        },
        'InternalServerError': {
            'type': 'object',
            'properties': {
                'timestamp': {'type': 'string'},
                'path': {'type': 'string'},
                'message': {'type': 'string'},
                'errorCode': {'type': 'string'}
            }
        }
    }
    
    # Add schemas to spec
    if 'components' not in spec:
        spec['components'] = {}
    if 'schemas' not in spec['components']:
        spec['components']['schemas'] = {}
    
    spec['components']['schemas'].update(ERROR_SCHEMAS)
    
    # Map status codes to schema names
    STATUS_TO_SCHEMA = {
        '400': 'BadRequestError',
        '401': 'UnauthorizedError',
        '403': 'ForbiddenError',
        '404': 'NotFoundError',
        '500': 'InternalServerError',
    }
    
    # Replace inline error schemas with $ref
    replaced_count = {status: 0 for status in STATUS_TO_SCHEMA}
    
    for path, methods in spec.get('paths', {}).items():
        for method, op in methods.items():
            if not isinstance(op, dict) or 'responses' not in op:
                continue
            
            for status_code, schema_name in STATUS_TO_SCHEMA.items():
                if status_code in op['responses']:
                    response = op['responses'][status_code]
                    
                    # For 404 responses without content, add content with NotFoundError schema
                    # This prevents ogen from generating empty per-operation NotFound structs
                    if status_code == '404' and 'content' not in response:
                        response['content'] = {
                            'application/json': {
                                'schema': {
                                    '$ref': f'#/components/schemas/{schema_name}'
                                }
                            }
                        }
                        replaced_count[status_code] += 1
                    elif 'content' in response and 'application/json' in response['content']:
                        # Replace inline schema with $ref
                        response['content']['application/json']['schema'] = {
                            '$ref': f'#/components/schemas/{schema_name}'
                        }
                        replaced_count[status_code] += 1
    
    total_replaced = sum(replaced_count.values())
    
    return spec, {
        'schemas_added': len(ERROR_SCHEMAS),
        'responses_unified': replaced_count,
        'total_replaced': total_replaced
    }


def analyze_spec(spec_file: str):
    """Analyze a spec file and show consolidation suggestions"""
    with open(spec_file, 'r') as f:
        spec = json.load(f)
    
    consolidator = SmartConsolidator(spec)
    rename_map, stats = consolidator.consolidate()
    
    print(f"=== SMART CONSOLIDATION ANALYSIS ===\n")
    print(f"Original schemas: {stats['original_count']}")
    print(f"Duplicate groups: {stats['duplicate_groups']}")
    print(f"After consolidation: {stats['final_count']}")
    print(f"Reduction: {stats['reduction']} ({stats['reduction']*100//stats['original_count']}%)")
    
    print(f"\n=== CONSOLIDATED NAMES ===\n")
    for canonical, names in sorted(stats['consolidated_names'].items()):
        print(f"\n{canonical} ({len(names)} merged):")
        for n in sorted(names):
            print(f"  <- {n}")
    
    return consolidator, rename_map, stats


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python smart_consolidate.py <spec.json>")
        sys.exit(1)
    
    analyze_spec(sys.argv[1])
