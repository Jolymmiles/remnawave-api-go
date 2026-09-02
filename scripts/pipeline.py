#!/usr/bin/env python3
"""
Complete API Processing Pipeline
=================================

This script processes OpenAPI specs through the complete workflow:
1. Smart consolidate schemas (unify duplicates + error responses)
2. Generate Go client via ogen
3. Generate client_ext.go wrapper

Usage:
    cd /path/to/remnawave-api-go
    python3 scripts/pipeline.py specs/3.4.3.json
"""

import json
import re
import subprocess
import sys
from pathlib import Path

from smart_consolidate import (
    InlineSchemaExtractor,
    SmartConsolidator,
    fix_nullable_without_type,
    unify_error_responses,
)


OGEN_VERSION = "v1.24.0"
EXPECTED_API_VERSION = "3.4.3"


def _contains_key(value: object, key: str) -> bool:
    """Return whether a nested OpenAPI value contains a dictionary key."""
    if isinstance(value, dict):
        return key in value or any(_contains_key(child, key) for child in value.values())
    if isinstance(value, list):
        return any(_contains_key(child, key) for child in value)
    return False


def validate_source_spec(spec: dict) -> None:
    """Fail early when generation is pointed at a pre-v3 or wrong-version spec."""
    version = spec.get('info', {}).get('version')
    if version != EXPECTED_API_VERSION:
        raise ValueError(
            f"expected Remnawave API {EXPECTED_API_VERSION}, got {version or 'unknown'}"
        )

    paths = spec.get('paths', {})
    required_paths = {
        '/api/users/stream',
        '/api/users/{userId}/actions/extend',
        '/api/connections/drop',
        '/api/connections/geocheck/{nodeUuid}',
        '/api/node-integrations',
        '/api/node-plugins/shared-lists',
        '/api/system/stats/digest',
        '/api/system/stats/http',
    }
    missing_paths = sorted(required_paths - paths.keys())
    if missing_paths:
        raise ValueError(f"v3.4.3 spec is missing required paths: {', '.join(missing_paths)}")

    removed_paths = {
        '/api/ip-control',
        '/api/users/by-telegram-id/{telegramId}',
        '/api/users/by-email/{email}',
        '/api/users/by-tag/{tag}',
        '/api/users/by-id/{id}',
    }
    stale_paths = sorted(removed_paths & paths.keys())
    if stale_paths:
        raise ValueError(f"spec contains removed v3 paths: {', '.join(stale_paths)}")

    schemas = spec.get('components', {}).get('schemas', {})
    required_schemas = {
        'RemnawaveBadRequestErrorDto',
        'RemnawaveNotFoundErrorDto',
        'RemnawaveInternalServerErrorDto',
    }
    missing_schemas = sorted(required_schemas - schemas.keys())
    if missing_schemas:
        raise ValueError(
            f"v3.4.3 spec is missing typed error schemas: {', '.join(missing_schemas)}"
        )

    if not _contains_key(spec, 'secretKey') or _contains_key(spec, 'pubKey'):
        raise ValueError("v3.4.3 keygen contract must use secretKey and not pubKey")

    legacy_fields = {
        'profileTitle',
        'profileUpdateInterval',
        'supportLink',
        'isProfileWebpageUrlEnabled',
        'happAnnounce',
        'happRouting',
        'userUuids',
    }
    stale_fields = sorted(field for field in legacy_fields if _contains_key(spec, field))
    if stale_fields:
        raise ValueError(f"spec contains removed v3 fields: {', '.join(stale_fields)}")


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_step(step: int, total: int, title: str):
    """Print a step header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}")
    print(f"STEP {step}/{total}: {title}")
    print(f"{'='*70}{Colors.END}\n")


def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message: str):
    print(f"{Colors.BLUE}→ {message}{Colors.END}")


# ============================================================================
# STEP 1: SMART CONSOLIDATE SCHEMAS
# ============================================================================

def smart_consolidate_schemas(input_file: str, output_file: str, skip_inline_extraction: bool = False) -> tuple[int, int, dict]:
    """
    Consolidate duplicate schemas using smart analysis.
    Combines old Steps 1 (consolidate) and 2 (rename) into one step.
    """
    print_info(f"Loading {input_file}...")
    with open(input_file, 'r') as f:
        spec = json.load(f)

    flattened_count = flatten_allof_with_oneof(spec)
    if flattened_count > 0:
        print_info(f"Flattened {flattened_count} allOf+oneOf schemas for ogen compatibility")

    datetime_count = restore_datetime_formats(spec)
    if datetime_count > 0:
        print_info(f"Restored date-time formats for {datetime_count} RFC3339 fields")

    original_count = len(spec.get('components', {}).get('schemas', {}))

    print_info("Analyzing schemas with SmartConsolidator...")
    consolidator = SmartConsolidator(spec)

    # Analyze duplicates
    report = consolidator.analyze_duplicates()
    print_info(f"Found {report['exact']['count']} exact duplicate groups ({report['exact']['total_schemas']} schemas)")
    print_info(f"Found {report['structural']['count']} structural duplicate groups")

    if report['near_duplicates']['count'] > 0:
        print_warning(f"Found {report['near_duplicates']['count']} near-duplicate groups (metadata differs)")

    if report['constraint_only']['count'] > 0:
        print_warning(f"Found {report['constraint_only']['count']} constraint-only groups (validation differs)")

    # Consolidate. Keep the original document when there is nothing to merge,
    # but continue through the remaining normalization and always write the
    # derived spec. This keeps the pipeline valid for future specs without
    # duplicate schemas.
    rename_map, stats = consolidator.consolidate()

    if not rename_map:
        print_warning("No duplicates to consolidate")
        new_spec = spec
        stats = {'consolidated_names': {}}
    else:
        new_spec = consolidator.apply_consolidation(rename_map)

    # Unify error responses
    print_info("Unifying error responses...")
    new_spec, error_stats = unify_error_responses(new_spec)
    if error_stats['total_replaced'] > 0:
        print_info(f"Unified {error_stats['total_replaced']} error responses (400: {error_stats['responses_unified'].get('400', 0)}, 401: {error_stats['responses_unified'].get('401', 0)})")
        stats['unified_errors'] = error_stats['total_replaced']

    # Fix nullable properties without type (ogen requires type for nullable fields)
    print_info("Fixing nullable properties without type...")
    new_spec, nullable_fixed = fix_nullable_without_type(new_spec)
    if nullable_fixed > 0:
        print_info(f"Fixed {nullable_fixed} nullable properties without type")
        stats['nullable_fixed'] = nullable_fixed

    # Extract inline schemas for reuse (optional - can cause conflicts in some specs)
    if not skip_inline_extraction:
        print_info("Extracting inline schemas for reuse...")
        extractor = InlineSchemaExtractor(new_spec)
        new_spec, extract_stats = extractor.extract_inline_schemas()

        if extract_stats['extracted_count'] > 0:
            print_info(f"Extracted {extract_stats['extracted_count']} inline schemas")
            stats['extracted_schemas'] = extract_stats['extracted_count']
    else:
        print_info("Skipping inline schema extraction")

    print_info(f"Writing {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(new_spec, f, indent=2, ensure_ascii=False)

    # Print top consolidated groups
    print_info("Top consolidated groups:")
    for name, schemas in sorted(stats['consolidated_names'].items(), key=lambda x: -len(x[1]))[:5]:
        print(f"    {name} <- {len(schemas)} schemas")

    new_count = len(new_spec.get('components', {}).get('schemas', {}))
    stats['final_count'] = new_count
    schema_delta = new_count - original_count
    schema_delta_percent = schema_delta * 100 // original_count if original_count else 0
    print_success(f"Consolidated {original_count} → {new_count} schemas ({schema_delta:+d}, {schema_delta_percent:+d}%)")

    return original_count, new_count, stats


def _merge_schema_objects(target: dict, source: dict) -> None:
    """Merge compatible object schemas while keeping variant fields optional."""
    target_properties = target.setdefault('properties', {})
    source_properties = source.get('properties', {})

    for name, source_property in source_properties.items():
        if name not in target_properties:
            target_properties[name] = source_property
            continue

        target_property = target_properties[name]
        if not isinstance(target_property, dict) or not isinstance(source_property, dict):
            target_properties[name] = {}
            continue

        target_type = target_property.get('type')
        source_type = source_property.get('type')
        if target_type == source_type == 'object':
            _merge_schema_objects(target_property, source_property)
            required = set(target_property.get('required', [])) & set(source_property.get('required', []))
            if required:
                target_property['required'] = sorted(required)
            else:
                target_property.pop('required', None)
            continue

        if target_type == source_type == 'string':
            target_enum = target_property.get('enum')
            source_enum = source_property.get('enum')
            if target_enum is not None and source_enum is not None:
                target_property['enum'] = sorted(set(target_enum) | set(source_enum), key=str)
            else:
                target_property.pop('enum', None)
            continue

        # A heterogeneous union is represented as raw JSON so no variant data
        # is lost when decoded by the generated Go client.
        target_properties[name] = {}

    # Requirements from a oneOf branch cannot be required on the merged object:
    # each branch has a different set of required fields.
    source_required = set(source.get('required', []))
    target_required = set(target.get('required', []))
    if target_required and source_required:
        common_required = target_required & source_required
        if common_required:
            target['required'] = sorted(common_required)
        else:
            target.pop('required', None)


def flatten_allof_with_oneof(spec: dict) -> int:
    """Flatten allOf schemas containing oneOf branches for ogen compatibility.

    The Remnawave 3.4.3 raw subscription model uses this composition for
    protocol, transport and security variants. Merging the object branches
    preserves all fields and keeps heterogeneous values as jx.Raw in the
    generated client.
    """
    flattened = 0

    def walk(value):
        nonlocal flattened
        if isinstance(value, list):
            for item in value:
                walk(item)
            return
        if not isinstance(value, dict):
            return

        all_of = value.get('allOf')
        if isinstance(all_of, list) and any(
            isinstance(item, dict) and 'oneOf' in item for item in all_of
        ):
            merged = {'type': 'object', 'properties': {}}
            base_required = None
            for item in all_of:
                if not isinstance(item, dict):
                    continue
                if 'oneOf' in item:
                    for variant in item.get('oneOf', []):
                        if isinstance(variant, dict):
                            _merge_schema_objects(merged, variant)
                    continue

                _merge_schema_objects(merged, item)
                required = set(item.get('required', []))
                base_required = required if base_required is None else base_required & required

            if base_required:
                merged['required'] = sorted(base_required)
            for key in ('title', 'description', 'nullable'):
                if key in value:
                    merged[key] = value[key]
            merged['x-ogen-flattened-composition'] = 'allOf+oneOf'
            value.clear()
            value.update(merged)
            flattened += 1

        for child in list(value.values()):
            walk(child)

    walk(spec)
    return flattened


RFC3339_PATTERN_MARKERS = (r'\d{4}-', 'T')


def restore_datetime_formats(spec: dict) -> int:
    """Restore date-time formats omitted by the 3.4.3 NestJS OpenAPI output."""
    restored = 0

    def walk(value):
        nonlocal restored
        if isinstance(value, list):
            for item in value:
                walk(item)
            return
        if not isinstance(value, dict):
            return

        pattern = value.get('pattern')
        if (
            value.get('type') == 'string'
            and 'format' not in value
            and isinstance(pattern, str)
            and all(marker in pattern for marker in RFC3339_PATTERN_MARKERS)
        ):
            value['format'] = 'date-time'
            restored += 1

        for child in value.values():
            walk(child)

    walk(spec)
    return restored


# ============================================================================
# STEP 1.5: PATCH SPEC FOR TEXT/PLAIN SUBSCRIPTION ENDPOINTS
# ============================================================================

# These subscription endpoints return text/plain (subscription configs as strings),
# but the OpenAPI spec doesn't declare response content, causing ogen to skip them.
SUBSCRIPTION_TEXT_OPERATIONS = [
    'SubscriptionController_getSubscription',
    'SubscriptionController_getSubscriptionByClientType',
    'SubscriptionController_getSubscriptionWithType',
]


def patch_subscription_text_responses(spec: dict) -> int:
    """
    Patch the spec to add text/plain response content
    for subscription endpoints that return raw subscription configs.
    Modifies spec in-place. Returns the number of operations patched.
    """
    patched = 0
    for path_item in spec.get('paths', {}).values():
        for op in path_item.values():
            if not isinstance(op, dict):
                continue
            op_id = op.get('operationId', '')
            if op_id not in SUBSCRIPTION_TEXT_OPERATIONS:
                continue

            responses = op.get('responses', {})
            resp_200 = responses.get('200', {})

            # Add text/plain content if not already present
            if 'content' not in resp_200:
                resp_200['content'] = {}
            if 'text/plain' not in resp_200['content']:
                resp_200['content']['text/plain'] = {
                    'schema': {'type': 'string'}
                }
                patched += 1
                print_info(f"Patched {op_id} with text/plain response")

            responses['200'] = resp_200
            op['responses'] = responses

    return patched


# ============================================================================
# STEP 1.6: SHORTEN OPERATION IDS
# ============================================================================

def shorten_operation_ids(spec: dict) -> int:
    """
    Strip 'Controller' from all operationIds to produce shorter Go type names.
    E.g. SubscriptionController_getSubscription → Subscription_getSubscription
    Modifies spec in-place. Returns the number of operations renamed.
    """
    renamed = 0
    for path_item in spec.get('paths', {}).values():
        for op in path_item.values():
            if not isinstance(op, dict):
                continue
            op_id = op.get('operationId', '')
            if 'Controller' in op_id:
                op['operationId'] = op_id.replace('Controller', '')
                renamed += 1
    return renamed


# ============================================================================
# STEP 1.7: STRIP 'Dto' SUFFIX FROM SCHEMA NAMES
# ============================================================================

def strip_dto_suffix(spec: dict) -> int:
    """
    Remove 'Dto' suffix from all schema names and update all $ref pointers.
    E.g. CreateUserRequestDto → CreateUserRequest
    Modifies spec in-place. Returns the number of schemas renamed.
    """
    schemas = spec.get('components', {}).get('schemas', {})
    rename_map = {}

    for name in list(schemas.keys()):
        if name.endswith('Dto'):
            new_name = name[:-3]
            # Avoid collision with existing schema
            if new_name not in schemas and new_name not in rename_map.values():
                rename_map[name] = new_name

    if not rename_map:
        return 0

    # Rename schemas
    new_schemas = {}
    for name, schema in schemas.items():
        new_name = rename_map.get(name, name)
        new_schemas[new_name] = schema
    spec['components']['schemas'] = new_schemas

    # Update all $ref pointers throughout the spec
    old_prefix = '#/components/schemas/'
    ref_map = {f'{old_prefix}{old}': f'{old_prefix}{new}' for old, new in rename_map.items()}

    def _update_refs(obj):
        if isinstance(obj, dict):
            if '$ref' in obj and obj['$ref'] in ref_map:
                obj['$ref'] = ref_map[obj['$ref']]
            for v in obj.values():
                _update_refs(v)
        elif isinstance(obj, list):
            for item in obj:
                _update_refs(item)

    _update_refs(spec)
    return len(rename_map)


# ============================================================================
# STEP 1.8: FIX NUMERIC QUERY PARAMETERS THAT SHOULD BE INTEGERS
# ============================================================================

# Query parameter names that are semantically integers (pagination, limits, counts)
INTEGER_QUERY_PARAMS = {'size', 'start', 'topUsersLimit', 'topNodesLimit', 'limit', 'offset', 'page', 'count'}


def fix_number_query_params(spec: dict) -> int:
    """
    Change query parameters with type 'number' to 'integer' when they represent
    pagination or limit values. The upstream OpenAPI spec incorrectly uses 'number'
    for these, which produces float64 in Go instead of int.
    Modifies spec in-place. Returns the number of parameters fixed.
    """
    fixed = 0
    for path_item in spec.get('paths', {}).values():
        for op in path_item.values():
            if not isinstance(op, dict):
                continue
            for param in op.get('parameters', []):
                if param.get('in') != 'query':
                    continue
                schema = param.get('schema', {})
                if schema.get('type') == 'number' and param.get('name') in INTEGER_QUERY_PARAMS:
                    schema['type'] = 'integer'
                    fixed += 1
    return fixed


INTEGER_PARAMETER_NAMES = {
    'limit',
    'minTotalBytes',
    'size',
    'start',
    'topNodesLimit',
    'topUsersLimit',
    'userId',
}

OPAQUE_CURSOR_PARAMETER_NAMES = {'cursor'}

INTEGER_PROPERTY_NAMES = {
    'activeHandles',
    'arrayBuffers',
    'bandwidthUsage',
    'blockDuration',
    'completed',
    'count',
    'cores',
    'createdCount',
    'days',
    'daysLeft',
    'devicesCount',
    'distinctCountries',
    'distinctNodes',
    'distinctUsers',
    'expiredCount',
    'expiresInDays',
    'expirationNotifications',
    'external',
    'fallbackDeviceLimit',
    'heartbeatPeriod',
    'heapTotal',
    'heapUsed',
    'id',
    'inboundsCount',
    'itemsCount',
    'lastDay',
    'lastWeek',
    'membersCount',
    'memoryTotal',
    'neverOnline',
    'notConnectedAfter',
    'notConnectedAfterHours',
    'notifyPercent',
    'nodes',
    'nodesCpuCores',
    'nodeId',
    'onlineNow',
    'pid',
    'port',
    'reportsLast24Hours',
    'requestCount',
    'rss',
    'rxTotal',
    'shortUuidLength',
    'statusCode',
    'telegramId',
    'total',
    'totalAvailableBillingNodes',
    'totalBillingNodes',
    'totalBytes',
    'totalHwidDevices',
    'totalReports',
    'totalUniqueDevices',
    'totalUsers',
    'trafficLimitBytes',
    'trafficResetDay',
    'trafficUsedBytes',
    'ts',
    'txTotal',
    'uptime',
    'userId',
    'userIds',
    'users',
    'usersOnline',
    'upcomingNodesCount',
    'usedTrafficBytes',
    'userUsageIgnoreBelowBytes',
    'lifetimeUsedTrafficBytes',
    'timeout',
    'totalBills',
    'totalOnline',
    'timestamp',
    'xrayUptime',
}


def fix_integer_semantics(spec: dict) -> int:
    """Represent integral API values as Go integers instead of float64.

    The Remnawave OpenAPI document frequently declares database IDs, byte
    counters, limits, and other integral values as JSON ``number`` without an
    integer format or ``multipleOf`` constraint.  The property/parameter name
    is the only reliable semantic signal in those cases.  Restricting the
    conversion to explicit numeric constraints therefore silently regresses
    the generated client to float64 on every regeneration.
    """
    fixed = 0

    def is_integral_number(schema):
        return schema.get('type') == 'number'

    for path_item in spec.get('paths', {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            for parameter in operation.get('parameters', []):
                if parameter.get('name') not in INTEGER_PARAMETER_NAMES:
                    continue
                schema = parameter.get('schema', {})
                if is_integral_number(schema):
                    schema['type'] = 'integer'
                    fixed += 1

    def walk(value):
        nonlocal fixed
        if isinstance(value, list):
            for item in value:
                walk(item)
            return
        if not isinstance(value, dict):
            return

        properties = value.get('properties')
        if isinstance(properties, dict):
            for name, property_schema in properties.items():
                if name not in INTEGER_PROPERTY_NAMES or not isinstance(property_schema, dict):
                    continue
                if is_integral_number(property_schema):
                    property_schema['type'] = 'integer'
                    fixed += 1
                elif property_schema.get('type') == 'array':
                    items = property_schema.get('items')
                    if isinstance(items, dict) and is_integral_number(items):
                        items['type'] = 'integer'
                        fixed += 1

        for child in value.values():
            walk(child)

    walk(spec)
    return fixed


def fix_system_stats_uptime(spec: dict) -> int:
    """Keep the fractional uptime returned by ``GET /api/system/stats``.

    The API document uses the generic JSON ``number`` type for this field, but
    the name-based integral pass above also sees other, genuinely integral,
    ``uptime`` fields.  Scope this exception to the stats operation instead of
    weakening the type of unrelated schemas.
    """
    operation = spec.get('paths', {}).get('/api/system/stats', {}).get('get', {})
    response = operation.get('responses', {}).get('200', {})
    content = response.get('content', {}).get('application/json', {})
    schema_ref = content.get('schema', {}).get('$ref')
    if not isinstance(schema_ref, str) or not schema_ref.startswith('#/components/schemas/'):
        return 0

    schema_name = schema_ref.rsplit('/', 1)[-1]
    root_schema = spec.get('components', {}).get('schemas', {}).get(schema_name, {})
    response_schema = root_schema.get('properties', {}).get('response', {})
    uptime_schema = response_schema.get('properties', {}).get('uptime', {})
    if uptime_schema.get('type') != 'integer':
        return 0

    uptime_schema['type'] = 'number'
    return 1


def fix_node_stats_uptime(spec: dict) -> int:
    """Keep the fractional uptime nested in node ``system.stats`` data.

    Remnawave's ``Stat`` schema currently declares this value as an integer,
    while the nodes endpoint returns seconds with fractional precision.  Keep
    the correction scoped to this schema so other integral uptime fields are
    unaffected.
    """
    uptime_schema = (
        spec.get('components', {})
        .get('schemas', {})
        .get('Stat', {})
        .get('properties', {})
        .get('uptime', {})
    )
    if uptime_schema.get('type') != 'integer':
        return 0

    uptime_schema['type'] = 'number'
    return 1


def fix_opaque_cursor_params(spec: dict) -> int:
    """Encode cursor query parameters as opaque strings.

    The stream response returns nextCursor as a string and clients must pass it
    back unchanged. Treating it as a number risks precision loss and makes the
    generated Go API incompatible with the response model.
    """
    fixed = 0
    for path_item in spec.get('paths', {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            for parameter in operation.get('parameters', []):
                if parameter.get('in') != 'query' or parameter.get('name') not in OPAQUE_CURSOR_PARAMETER_NAMES:
                    continue
                schema = parameter.get('schema', {})
                if schema.get('type') != 'string':
                    parameter['schema'] = {
                        'type': 'string',
                        'description': 'Opaque cursor returned by the previous page.',
                    }
                    parameter.pop('style', None)
                    parameter.pop('explode', None)
                    fixed += 1
    return fixed


# The Remnawave backend parses these query parameters from JSON strings. Its
# OpenAPI document describes them as nested structures, which ogen cannot
# encode as query parameters.
JSON_STRING_QUERY_PARAMS = {'filters', 'filterModes', 'sorting'}


def stringify_complex_query_params(spec: dict) -> int:
    """Represent JSON-encoded query parameters as strings for ogen."""
    fixed = 0
    for path_item in spec.get('paths', {}).values():
        for op in path_item.values():
            if not isinstance(op, dict):
                continue
            for param in op.get('parameters', []):
                if param.get('in') != 'query' or param.get('name') not in JSON_STRING_QUERY_PARAMS:
                    continue

                schema = param.get('schema', {})
                if schema.get('type') not in {'array', 'object'}:
                    continue

                param['schema'] = {
                    'type': 'string',
                    'format': 'json',
                    'description': 'JSON-encoded query value.',
                }
                param.pop('style', None)
                param.pop('explode', None)
                fixed += 1
    return fixed


def simplify_any_of_schemas(spec: dict) -> int:
    """Replace unsupported anyOf schemas with their safe common representation."""
    simplified = 0
    schema_metadata_keys = {
        '$ref',
        'title',
        'description',
        'markdownDescription',
        'nullable',
        'required',
        'default',
        'deprecated',
        'readOnly',
        'writeOnly',
        'example',
        'externalDocs',
        'format',
        'discriminator',
        'xml',
    }

    def resolve_variant_schema(variant):
        if not isinstance(variant, dict):
            return None

        current = variant
        seen_refs = set()
        while isinstance(current, dict):
            ref = current.get('$ref')
            if not ref:
                return current
            if not isinstance(ref, str) or not ref.startswith('#/') or ref in seen_refs:
                return None
            seen_refs.add(ref)

            target = spec
            for token in ref[2:].split('/'):
                token = token.replace('~1', '/').replace('~0', '~')
                if not isinstance(target, dict) or token not in target:
                    return None
                target = target[token]
            current = target

        return None

    def simplify(value):
        nonlocal simplified
        if isinstance(value, list):
            for item in value:
                simplify(item)
            return

        if not isinstance(value, dict):
            return

        if 'anyOf' in value:
            variants = value.pop('anyOf')
            variant_types = set()
            unresolved_variant = False
            resolved_variants = []
            for variant in variants:
                resolved_variant = resolve_variant_schema(variant)
                variant_type = (
                    resolved_variant.get('type')
                    if isinstance(resolved_variant, dict)
                    else None
                )
                resolved_variants.append(resolved_variant)
                if variant_type is None:
                    unresolved_variant = True
                else:
                    variant_types.add(variant_type)

            if len(variant_types) == 1 and not unresolved_variant:
                variant_type = variant_types.pop()
                if variant_type == 'object':
                    value['type'] = 'object'
                    for variant in resolved_variants:
                        if isinstance(variant, dict):
                            _merge_schema_objects(value, variant)
                else:
                    value['type'] = variant_type
            else:
                metadata = {
                    key: metadata_value
                    for key, metadata_value in value.items()
                    if key in schema_metadata_keys or key.startswith('x-')
                }
                value.clear()
                value.update(metadata)
                reason = 'unresolved' if unresolved_variant else 'mixed'
                print_warning(
                    f"Simplified {reason} anyOf to an unconstrained schema"
                )
            simplified += 1

        for child in value.values():
            simplify(child)

    simplify(spec)
    return simplified


# ============================================================================
# STEP 2: GENERATE GO CLIENT WITH OGEN
# ============================================================================

def generate_ogen_client(spec_file: str) -> bool:
    """Generate Go client using ogen"""
    print_info(f"Running ogen with {spec_file}...")

    try:
        result = subprocess.run(
            [
                'go', 'run', f'github.com/ogen-go/ogen/cmd/ogen@{OGEN_VERSION}',
                '--config', '.ogen.yml',
                '--target', 'api',
                '--package', 'api',
                '--clean',
                spec_file
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print_success(f"Go client generated from {spec_file}")
            return True
        else:
            print_error(f"ogen generation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print_error("ogen generation timed out")
        return False
    except (OSError, subprocess.SubprocessError) as e:
        print_error(f"Error running ogen: {e}")
        return False


# ============================================================================
# STEP 3: GENERATE CLIENT_EXT.GO
# ============================================================================

def parse_oas_client_methods(client_file: str) -> dict:
    """Parse method signatures from oas_client_gen.go"""
    with open(client_file, 'r') as f:
        content = f.read()

    methods = {}
    pattern = r'func \(c \*Client\) (\w+)\((ctx context\.Context(?:,\s*[^)]+)?)\)\s*\(([^)]+)\)'

    for match in re.finditer(pattern, content, re.MULTILINE):
        method_name = match.group(1)
        if method_name in ['requestURL'] or method_name.startswith('send'):
            continue

        full_params = match.group(2)
        returns = match.group(3)

        # Parse params (skip ctx and variadic options)
        params_list = []
        has_options = False
        if ', ' in full_params:
            params_str = full_params.split(', ', 1)[1]
            # Detect variadic ...RequestOption
            if '...RequestOption' in params_str:
                has_options = True
                # Remove variadic param before parsing regular params
                params_str = re.sub(r',?\s*options\s+\.\.\.RequestOption', '', params_str).strip()
            for param in re.findall(r'(\w+)\s+([\*\w\.]+)', params_str):
                params_list.append((param[0], param[1]))

        returns_list = [r.strip() for r in returns.split(',')]

        methods[method_name] = {
            'params': params_list,
            'returns': returns_list,
            'has_options': has_options,
        }

    return methods


def parse_params_structs(params_file: str) -> dict:
    """Parse Params struct fields from oas_parameters_gen.go"""
    with open(params_file, 'r') as f:
        content = f.read()

    params_structs = {}

    # Match struct definitions with their fields
    # Pattern: type XXXParams struct {\n\tField Type\n}
    pattern = r'type (\w+Params) struct \{([^}]*)\}'

    for match in re.finditer(pattern, content, re.DOTALL):
        struct_name = match.group(1)
        fields_block = match.group(2)

        fields = []
        # Parse fields: Name Type or Name Type `json:"..."`
        for line in fields_block.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            # Match field: UUID string or Size OptFloat64
            field_match = re.match(r'^(\w+)\s+([\w\.\*\[\]]+)', line)
            if field_match:
                field_name = field_match.group(1)
                field_type = field_match.group(2)
                fields.append((field_name, field_type))

        params_structs[struct_name] = fields

    return params_structs


def simplify_param_type(param_type: str) -> str:
    """Convert ogen types to simpler Go types for method signatures"""
    # OptString -> string, OptFloat64 -> float64, etc.
    type_map = {
        'OptString': 'string',
        'OptInt': 'int',
        'OptFloat64': 'float64',
        'OptBool': 'bool',
        'uuid.UUID': 'string',
    }
    if param_type in type_map:
        return type_map[param_type]
    if param_type.startswith('Opt'):
        return param_type[3:]
    return param_type


# Go reserved keywords that cannot be used as identifiers
GO_KEYWORDS = {
    'break', 'case', 'chan', 'const', 'continue', 'default', 'defer', 'else',
    'fallthrough', 'for', 'func', 'go', 'goto', 'if', 'import', 'interface',
    'map', 'package', 'range', 'return', 'select', 'struct', 'switch', 'type',
    'var',
}


def safe_param_name(name: str) -> str:
    """Convert a field name to a safe Go parameter name, avoiding reserved keywords."""
    lower = name.lower()
    if lower == 'uuid':
        return 'uuidValue'
    if lower in GO_KEYWORDS:
        return lower + 'Val'
    return lower


def _to_pascal(s: str) -> str:
    """Convert first letter to uppercase, preserving camelCase."""
    if not s:
        return s
    return s[0].upper() + s[1:]


def parse_operations(spec_file: str) -> dict:
    """Parse operations from OpenAPI spec"""
    with open(spec_file, 'r') as f:
        spec = json.load(f)

    operations_by_controller = {}

    for path_item in spec.get('paths', {}).values():
        for http_method, op_spec in path_item.items():
            if http_method not in ['get', 'post', 'put', 'patch', 'delete']:
                continue

            op_id = op_spec.get('operationId')
            if not op_id or '_' not in op_id:
                continue

            parts = op_id.split('_', 1)
            controller_full = parts[0]
            method_snake = parts[1]

            controller = controller_full.replace('Controller', '')

            method_parts = method_snake.split('_')
            method_pascal = ''.join(_to_pascal(p) for p in method_parts)

            go_method = controller_full + method_pascal

            if controller not in operations_by_controller:
                operations_by_controller[controller] = []

            operations_by_controller[controller].append({
                'operationId': op_id,
                'goMethod': go_method,
                'displayMethod': method_pascal
            })

    return operations_by_controller


def generate_client_ext(spec_file: str, client_file: str, output_file: str) -> tuple[int, int, set[str]]:
    """Generate client_ext.go wrapper with simplified method signatures"""
    print_info("Parsing oas_client_gen.go...")
    methods = parse_oas_client_methods(client_file)
    print_success(f"Found {len(methods)} client methods")

    # Parse params structs for simplification
    params_file = client_file.replace('oas_client_gen.go', 'oas_parameters_gen.go')
    print_info("Parsing oas_parameters_gen.go...")
    params_structs = parse_params_structs(params_file)
    print_success(f"Found {len(params_structs)} param structs")

    print_info("Parsing operations from spec...")
    operations_by_controller = parse_operations(spec_file)
    total_ops = sum(len(ops) for ops in operations_by_controller.values())
    print_success(f"Found {total_ops} operations in {len(operations_by_controller)} controllers")

    def to_camel(s):
        return s[0].lower() + s[1:] if s else s

    def can_simplify_params(params_type: str) -> tuple:
        """
        Check if Params struct can be simplified to individual arguments.
        Returns (can_simplify, [(field_name, field_type, simple_type), ...])
        """
        struct_name = params_type.lstrip('*')
        if struct_name not in params_structs:
            return False, []

        fields = params_structs[struct_name]
        if not fields:
            return False, []

        # Keep optional fields in their generated Params struct so callers can
        # distinguish an omitted query parameter from its zero value.
        simple_types = {'string', 'int', 'int64', 'float64', 'bool', 'uuid.UUID'}

        simplified = []
        for field_name, field_type in fields:
            if field_type in simple_types:
                simple = simplify_param_type(field_type)
                simplified.append((field_name, field_type, simple))
            else:
                # Complex type, don't simplify
                return False, []

        return True, simplified

    def is_filter_pagination_params(params_type: str) -> bool:
        """Check whether Params contains optional JSON filters and pagination."""
        fields = params_structs.get(params_type.lstrip('*'), [])
        field_names = {field_name for field_name, _ in fields}
        return {
            'Start',
            'Size',
            'Filters',
            'FilterModes',
            'GlobalFilterMode',
            'Sorting',
        }.issubset(field_names)

    def uuid_parse_error_return(returns: list[str]) -> str:
        """Generate a compile-safe return for a failed UUID parse."""
        if not returns:
            return '\t\treturn\n'

        zero_returns = []
        zero_declarations = []
        for return_index, return_type in enumerate(returns):
            if return_type == 'error':
                zero_returns.append('err')
                continue
            zero_name = f'zero{return_index}'
            zero_declarations.append(f'\t\tvar {zero_name} {return_type}\n')
            zero_returns.append(zero_name)

        return ''.join(zero_declarations) + f"\t\treturn {', '.join(zero_returns)}\n"

    # Generate code
    body = '''// ClientExt wraps the base Client with organized sub-client access.
// Use controller methods (e.g., client.Users().GetUserById()) to call API operations.
type ClientExt struct {
\tclient *Client
'''

    for controller in sorted(operations_by_controller.keys()):
        field_name = to_camel(controller)
        body += f'\t{field_name} *{controller}Client\n'

    body += '''}

// NewClientExt creates a new ClientExt wrapper.
func NewClientExt(client *Client) *ClientExt {
\treturn &ClientExt{
\t\tclient: client,
'''

    for controller in sorted(operations_by_controller.keys()):
        field_name = to_camel(controller)
        body += f'\t\t{field_name}: New{controller}Client(client),\n'

    body += '''\t}
}

// Client returns the underlying ogen Client.
func (ce *ClientExt) Client() *Client {
\treturn ce.client
}

'''

    for controller in sorted(operations_by_controller.keys()):
        field_name = to_camel(controller)
        body += f'''// {controller} returns the {controller}Client.
func (ce *ClientExt) {controller}() *{controller}Client {{
\treturn ce.{field_name}
}}

'''

    matched_methods = 0
    wrapped_operation_ids = set()

    for controller in sorted(operations_by_controller.keys()):
        body += f'''// {controller}Client provides {controller} operations.
type {controller}Client struct {{
\tclient *Client
}}

// New{controller}Client creates a new {controller}Client.
func New{controller}Client(client *Client) *{controller}Client {{
\treturn &{controller}Client{{client: client}}
}}

'''

        for op in sorted(operations_by_controller[controller], key=lambda x: x['goMethod']):
            go_method = op['goMethod']
            display_method = op['displayMethod']
            op_id = op['operationId']

            if go_method not in methods:
                continue

            matched_methods += 1
            wrapped_operation_ids.add(op_id)
            method_info = methods[go_method]
            params = method_info['params']
            returns = method_info['returns']
            has_options = method_info.get('has_options', False)

            # options suffix for signature and call
            opts_sig = ', options ...RequestOption' if has_options else ''
            opts_call = ', options...' if has_options else ''

            # Check if we can simplify Params struct to individual args
            simplified_params = None
            params_index = None
            filter_pagination_params_type = None
            for i, (pname, ptype) in enumerate(params):
                if ptype.endswith('Params'):
                    can_simplify, simplified = can_simplify_params(ptype)
                    if can_simplify:
                        simplified_params = simplified
                        params_index = i
                    if len(params) == 1 and is_filter_pagination_params(ptype):
                        filter_pagination_params_type = ptype
                    break

            if returns:
                ret_type = ', '.join(returns)
                if len(returns) > 1:
                    ret_type = f'({ret_type})'
            else:
                ret_type = ''

            wrapped_display_method = display_method
            if filter_pagination_params_type:
                wrapped_display_method += 'WithParams'

            # Generate method with simplified params or original
            if simplified_params and params_index is not None:
                params_type = params[params_index][1]

                sig_parts = []
                for i, (pname, ptype) in enumerate(params):
                    if i == params_index:
                        for field_name, field_type, simple_type in simplified_params:
                            sig_parts.append(f'{safe_param_name(field_name)} {simple_type}')
                    else:
                        sig_parts.append(f'{pname} {ptype}')

                simple_args = ', '.join(sig_parts)

                uuid_args = {}
                uuid_parse_code = ''
                for field_name, field_type, _ in simplified_params:
                    if field_type != 'uuid.UUID':
                        continue
                    arg_name = safe_param_name(field_name)
                    parsed_name = f'parsed{field_name}'
                    uuid_args[field_name] = parsed_name
                    parse_error_return = uuid_parse_error_return(returns)
                    uuid_parse_code += f'''\t{parsed_name}, err := uuid.Parse({arg_name})
\tif err != nil {{
{parse_error_return}\t}}
'''

                params_init = f'{params_type}{{\n'
                for field_name, field_type, simple_type in simplified_params:
                    arg_name = safe_param_name(field_name)
                    if field_type.startswith('Opt'):
                        params_init += f'\t\t{field_name}: New{field_type}({arg_name}),\n'
                    else:
                        params_init += f'\t\t{field_name}: {uuid_args.get(field_name, arg_name)},\n'
                params_init += '\t}'

                call_args = []
                for i, (pname, ptype) in enumerate(params):
                    if i == params_index:
                        call_args.append(params_init)
                    else:
                        call_args.append(pname)

                body += f'''// {wrapped_display_method} calls {op_id}.
func (sc *{controller}Client) {wrapped_display_method}(ctx context.Context, {simple_args}{opts_sig}) {ret_type} {{
{uuid_parse_code}
\treturn sc.client.{go_method}(ctx, {', '.join(call_args)}{opts_call})
}}

'''
            else:
                # Original params
                if params:
                    params_sig = ', '.join([f'{p[0]} {p[1]}' for p in params])
                    params_call = ', '.join([p[0] for p in params])
                else:
                    params_sig = ''
                    params_call = ''

                body += f'''// {wrapped_display_method} calls {op_id}.
func (sc *{controller}Client) {wrapped_display_method}(ctx context.Context'''

                if params_sig:
                    body += f', {params_sig}'

                body += opts_sig + ')'

                if ret_type:
                    body += f' {ret_type}'

                body += ' {\n'

                if returns:
                    body += f'\treturn sc.client.{go_method}(ctx'
                else:
                    body += f'\tsc.client.{go_method}(ctx'

                if params_call:
                    body += f', {params_call}'

                body += opts_call + ')\n}\n\n'

            if filter_pagination_params_type:
                body += f'''// {display_method} lists results with simple offset pagination.
func (sc *{controller}Client) {display_method}(ctx context.Context, start int, size int{opts_sig}) {ret_type} {{
\treturn sc.{wrapped_display_method}(ctx, {filter_pagination_params_type}{{
\t\tStart: NewOptInt(start),
\t\tSize:  NewOptInt(size),
\t}}{opts_call})
}}

'''

    imports = 'import "context"'
    if 'uuid.Parse(' in body:
        imports = '''import (
\t"context"

\t"github.com/google/uuid"
)'''

    code = f'''// Code generated by pipeline.py. DO NOT EDIT manually.

package api

{imports}

{body}'''

    print_info(f"Writing {output_file}...")
    with open(output_file, 'w') as f:
        f.write(code)
    try:
        subprocess.run(['gofmt', '-w', output_file], check=True)
    except (OSError, subprocess.SubprocessError) as e:
        raise ValueError(f"Error running gofmt: {e}") from e

    print_success(f"Generated {matched_methods}/{total_ops} methods")

    return len(operations_by_controller), matched_methods, wrapped_operation_ids


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print_error("Usage: python3 pipeline.py <input_spec.json>")
        sys.exit(1)

    input_spec = sys.argv[1]

    if not Path(input_spec).exists():
        print_error(f"File not found: {input_spec}")
        sys.exit(1)

    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("="*70)
    print(" API PROCESSING PIPELINE")
    print("="*70)
    print(f"{Colors.END}")
    print(f"Input: {input_spec}")

    # File paths - now we only need one output file since smart_consolidate does both steps
    final_file = input_spec.replace('.json', '-final.json')
    client_gen_file = 'api/oas_client_gen.go'
    client_ext_file = 'api/client_ext.go'

    try:
        with open(input_spec, 'r') as f:
            source_spec = json.load(f)
        validate_source_spec(source_spec)
        print_success(f"Validated Remnawave API {EXPECTED_API_VERSION} source contract")

        # Step 1: Smart consolidate (combines old Steps 1 & 2)
        print_step(1, 3, "SMART CONSOLIDATE SCHEMAS")
        orig_count, new_count, stats = smart_consolidate_schemas(input_spec, final_file)

        # Step 1.5: Post-process the consolidated spec (in-memory)
        print_info("Post-processing consolidated spec...")
        with open(final_file, 'r') as f:
            final_spec = json.load(f)

        patched_count = patch_subscription_text_responses(final_spec)
        if patched_count > 0:
            print_success(f"Patched {patched_count} subscription endpoints with text/plain response")

        renamed_count = shorten_operation_ids(final_spec)
        if renamed_count > 0:
            print_success(f"Shortened {renamed_count} operationIds (removed 'Controller')")

        dto_count = strip_dto_suffix(final_spec)
        if dto_count > 0:
            print_success(f"Stripped 'Dto' suffix from {dto_count} schema names")

        int_count = fix_number_query_params(final_spec)
        if int_count > 0:
            print_success(f"Fixed {int_count} query parameters: number → integer")

        integer_semantics_count = fix_integer_semantics(final_spec)
        if integer_semantics_count > 0:
            print_success(
                f"Fixed {integer_semantics_count} integral values: number → integer"
            )

        fractional_stats_count = fix_system_stats_uptime(final_spec)
        if fractional_stats_count > 0:
            print_success(
                f"Preserved {fractional_stats_count} fractional system stats field: uptime"
            )

        fractional_node_count = fix_node_stats_uptime(final_spec)
        if fractional_node_count > 0:
            print_success(
                f"Preserved {fractional_node_count} fractional node stats field: uptime"
            )

        cursor_count = fix_opaque_cursor_params(final_spec)
        if cursor_count > 0:
            print_success(f"Fixed {cursor_count} cursor parameters: number → opaque string")

        json_query_count = stringify_complex_query_params(final_spec)
        if json_query_count > 0:
            print_success(f"Stringified {json_query_count} JSON query parameters for ogen")

        any_of_count = simplify_any_of_schemas(final_spec)
        if any_of_count > 0:
            print_success(f"Simplified {any_of_count} anyOf schemas for ogen")

        with open(final_file, 'w') as f:
            json.dump(final_spec, f, indent=2, ensure_ascii=False)

        # Step 2: Generate with ogen
        print_step(2, 3, "GENERATE GO CLIENT WITH OGEN")
        if not generate_ogen_client(final_file):
            print_error("Failed to generate Go client")
            sys.exit(1)

        # Step 3: Generate client_ext
        print_step(3, 3, "GENERATE CLIENT_EXT.GO WRAPPER")
        ctrl_count, method_count, wrapped_operation_ids = generate_client_ext(
            final_file, client_gen_file, client_ext_file
        )
        operation_ids = {
            operation.get('operationId')
            for path_item in final_spec.get('paths', {}).values()
            for http_method, operation in path_item.items()
            if http_method in ['get', 'post', 'put', 'patch', 'delete']
            and isinstance(operation, dict)
            and operation.get('operationId')
        }
        total_operations = len(operation_ids)
        missing_operation_ids = sorted(operation_ids - wrapped_operation_ids)
        if missing_operation_ids:
            print_error(
                f"Generated client covers {method_count}/{total_operations} operations"
            )
            print_error(
                "Missing operations: " + ", ".join(missing_operation_ids)
            )
            sys.exit(1)

        # Summary
        print(f"\n{Colors.BOLD}{Colors.GREEN}")
        print("="*70)
        print(" PIPELINE COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"{Colors.END}")
        print(f"\n{Colors.BOLD}Results:{Colors.END}")
        schema_delta = new_count - orig_count
        schema_delta_percent = schema_delta * 100 // orig_count if orig_count else 0
        print(f"  • Schemas:     {orig_count} → {new_count} ({schema_delta:+d}, {schema_delta_percent:+d}%)")
        print(f"  • Groups:      {stats.get('duplicate_groups', 0)} consolidated")
        print(f"  • Controllers: {ctrl_count}")
        print(f"  • Methods:     {method_count}")
        print(f"\n{Colors.BOLD}Generated files:{Colors.END}")
        print(f"  • {final_file}")
        print(f"  • {client_gen_file}")
        print(f"  • {client_ext_file}")
        print()

    except (OSError, ValueError) as e:
        print_error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
