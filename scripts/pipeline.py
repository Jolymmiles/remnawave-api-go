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
    python3 scripts/pipeline.py specs/api-2-3-0.json
"""

import json
import subprocess
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

from smart_consolidate import SmartConsolidator, InlineSchemaExtractor, unify_error_responses, fix_nullable_without_type


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

def smart_consolidate_schemas(input_file: str, output_file: str, skip_inline_extraction: bool = False) -> Tuple[int, int, dict]:
    """
    Consolidate duplicate schemas using smart analysis.
    Combines old Steps 1 (consolidate) and 2 (rename) into one step.
    """
    print_info(f"Loading {input_file}...")
    with open(input_file, 'r') as f:
        spec = json.load(f)
    
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
    
    # Consolidate
    rename_map, stats = consolidator.consolidate()
    
    if not rename_map:
        print_warning("No duplicates to consolidate")
        return original_count, original_count, {}
    
    # Apply consolidation
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
    print_success(f"Consolidated {original_count} → {new_count} schemas (-{original_count - new_count}, -{(original_count-new_count)*100//original_count}%)")
    
    return original_count, new_count, stats


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
    for path, path_item in spec.get('paths', {}).items():
        for http_method, op in path_item.items():
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
    for path, path_item in spec.get('paths', {}).items():
        for http_method, op in path_item.items():
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
    for path, path_item in spec.get('paths', {}).items():
        for http_method, op in path_item.items():
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


# ============================================================================
# STEP 2: GENERATE GO CLIENT WITH OGEN
# ============================================================================

def generate_ogen_client(spec_file: str) -> bool:
    """Generate Go client using ogen"""
    print_info(f"Running ogen with {spec_file}...")
    
    try:
        result = subprocess.run(
            [
                'go', 'run', 'github.com/ogen-go/ogen/cmd/ogen@v1.19.0',
                '--config', '.ogen.yml',
                '--target', 'api',
                '--package', 'api',
                '--clean',
                spec_file
            ],
            capture_output=True,
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
    except Exception as e:
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
    }
    return type_map.get(param_type, param_type)


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

    for path, path_item in spec.get('paths', {}).items():
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


def generate_client_ext(spec_file: str, client_file: str, output_file: str) -> Tuple[int, int]:
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
        
        # Only simplify if all fields are simple types
        simple_types = {'string', 'int', 'int64', 'float64', 'bool', 
                       'OptString', 'OptInt', 'OptInt64', 'OptFloat64', 'OptBool'}
        
        simplified = []
        for field_name, field_type in fields:
            if field_type in simple_types or field_type.startswith('Opt'):
                simple = simplify_param_type(field_type)
                simplified.append((field_name, field_type, simple))
            else:
                # Complex type, don't simplify
                return False, []
        
        return True, simplified
    
    # Generate code
    code = '''// Code generated by pipeline.py. DO NOT EDIT manually.

package api

import "context"

// ClientExt wraps the base Client with organized sub-client access.
// Use controller methods (e.g., client.Users().GetByUuid()) to call API operations.
type ClientExt struct {
\tclient *Client
'''
    
    for controller in sorted(operations_by_controller.keys()):
        field_name = to_camel(controller)
        code += f'\t{field_name} *{controller}Client\n'
    
    code += '''}

// NewClientExt creates a new ClientExt wrapper.
func NewClientExt(client *Client) *ClientExt {
\treturn &ClientExt{
\t\tclient: client,
'''
    
    for controller in sorted(operations_by_controller.keys()):
        field_name = to_camel(controller)
        code += f'\t\t{field_name}: New{controller}Client(client),\n'
    
    code += '''\t}
}

// Client returns the underlying ogen Client.
func (ce *ClientExt) Client() *Client {
\treturn ce.client
}

'''
    
    for controller in sorted(operations_by_controller.keys()):
        field_name = to_camel(controller)
        code += f'''// {controller} returns the {controller}Client.
func (ce *ClientExt) {controller}() *{controller}Client {{
\treturn ce.{field_name}
}}

'''
    
    matched_methods = 0
    
    for controller in sorted(operations_by_controller.keys()):
        code += f'''// {controller}Client provides {controller} operations.
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
            for i, (pname, ptype) in enumerate(params):
                if ptype.endswith('Params'):
                    can_simplify, simplified = can_simplify_params(ptype)
                    if can_simplify:
                        simplified_params = simplified
                        params_index = i
                    break

            if returns:
                ret_type = ', '.join(returns)
                if len(returns) > 1:
                    ret_type = f'({ret_type})'
            else:
                ret_type = ''

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

                params_init = f'{params_type}{{\n'
                for field_name, field_type, simple_type in simplified_params:
                    arg_name = safe_param_name(field_name)
                    if field_type.startswith('Opt'):
                        params_init += f'\t\t{field_name}: NewOpt{simple_type.title()}({arg_name}),\n'
                    else:
                        params_init += f'\t\t{field_name}: {arg_name},\n'
                params_init += '\t}'

                call_args = []
                for i, (pname, ptype) in enumerate(params):
                    if i == params_index:
                        call_args.append(params_init)
                    else:
                        call_args.append(pname)

                code += f'''// {display_method} calls {op_id}.
func (sc *{controller}Client) {display_method}(ctx context.Context, {simple_args}{opts_sig}) {ret_type} {{
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

                code += f'''// {display_method} calls {op_id}.
func (sc *{controller}Client) {display_method}(ctx context.Context'''

                if params_sig:
                    code += f', {params_sig}'

                code += opts_sig + ')'

                if ret_type:
                    code += f' {ret_type}'

                code += ' {\n'

                if returns:
                    code += f'\treturn sc.client.{go_method}(ctx'
                else:
                    code += f'\tsc.client.{go_method}(ctx'

                if params_call:
                    code += f', {params_call}'

                code += opts_call + ')\n}\n\n'
    
    print_info(f"Writing {output_file}...")
    with open(output_file, 'w') as f:
        f.write(code)
    
    print_success(f"Generated {matched_methods}/{total_ops} methods")
    
    return len(operations_by_controller), matched_methods


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

        with open(final_file, 'w') as f:
            json.dump(final_spec, f, indent=2, ensure_ascii=False)

        # Step 2: Generate with ogen
        print_step(2, 3, "GENERATE GO CLIENT WITH OGEN")
        if not generate_ogen_client(final_file):
            print_error("Failed to generate Go client")
            sys.exit(1)
        
        # Step 3: Generate client_ext
        print_step(3, 3, "GENERATE CLIENT_EXT.GO WRAPPER")
        ctrl_count, method_count = generate_client_ext(final_file, client_gen_file, client_ext_file)
        
        # Summary
        print(f"\n{Colors.BOLD}{Colors.GREEN}")
        print("="*70)
        print(" PIPELINE COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"{Colors.END}")
        print(f"\n{Colors.BOLD}Results:{Colors.END}")
        print(f"  • Schemas:     {orig_count} → {new_count} (-{orig_count - new_count}, -{(orig_count-new_count)*100//orig_count}%)")
        print(f"  • Groups:      {stats.get('duplicate_groups', 0)} consolidated")
        print(f"  • Controllers: {ctrl_count}")
        print(f"  • Methods:     {method_count}")
        print(f"\n{Colors.BOLD}Generated files:{Colors.END}")
        print(f"  • {final_file}")
        print(f"  • {client_gen_file}")
        print(f"  • {client_ext_file}")
        print()
        
    except Exception as e:
        print_error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
