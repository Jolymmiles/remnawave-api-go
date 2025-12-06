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

import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Set


class SchemaStructureAnalyzer:
    """Analyzes schema structure to find duplicates based on attributes"""
    
    # Metadata fields to ignore when comparing structure
    METADATA_FIELDS = {'description', 'example', 'examples', 'title', 'default', 
                       'deprecated', 'externalDocs', 'xml', 'x-'}
    
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
        import json
        
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
    
    # Action prefixes that indicate CRUD operations
    CRUD_ACTIONS = {'Create', 'Get', 'Update', 'Delete', 'List', 'Find', 'Fetch'}
    
    # Action prefixes that indicate state changes
    STATE_ACTIONS = {'Enable', 'Disable', 'Activate', 'Deactivate', 'Reset', 'Revoke', 'Restart'}
    
    # Bulk operation prefixes
    BULK_ACTIONS = {'Bulk', 'BulkAll', 'BulkDelete', 'BulkUpdate', 'BulkReset'}
    
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
        
        stats['final_count'] = len(self.schemas) - sum(len(v) - 1 for v in duplicates.values())
        stats['reduction'] = stats['original_count'] - stats['final_count']
        
        return rename_map, stats
    
    def apply_consolidation(self, rename_map: Dict[str, str]) -> dict:
        """Apply consolidation to the spec"""
        import copy
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
