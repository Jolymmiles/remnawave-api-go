#!/usr/bin/env python3
"""
Complete API Processing Pipeline
=================================

This script processes OpenAPI specs through the complete workflow:
1. Consolidate duplicate schemas
2. Rename schemas to common names
3. Generate Go client via ogen
4. Generate client_ext.go wrapper

Usage:
    python3 pipeline.py api-2-2-2.json
"""

import json
import subprocess
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple


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
# STEP 1: CONSOLIDATE SCHEMAS
# ============================================================================

def find_duplicate_schemas(spec: dict) -> Dict[str, List[str]]:
    """Find duplicate schemas by comparing their JSON representations"""
    schemas = spec.get('components', {}).get('schemas', {})
    
    # Group by content hash
    content_to_names = {}
    for name, schema_def in schemas.items():
        content = json.dumps(schema_def, sort_keys=True)
        if content not in content_to_names:
            content_to_names[content] = []
        content_to_names[content].append(name)
    
    # Return only groups with duplicates
    duplicates = {
        names[0]: names for names in content_to_names.values() if len(names) > 1
    }
    
    return duplicates


def consolidate_schemas(input_file: str, output_file: str) -> Tuple[int, int]:
    """Consolidate duplicate schemas"""
    print_info(f"Loading {input_file}...")
    with open(input_file, 'r') as f:
        spec = json.load(f)
    
    original_count = len(spec.get('components', {}).get('schemas', {}))
    
    print_info("Finding duplicate schemas...")
    duplicates = find_duplicate_schemas(spec)
    
    if not duplicates:
        print_warning("No duplicates found")
        return original_count, original_count
    
    print_info(f"Found {len(duplicates)} duplicate groups")
    
    # Create mapping from old names to canonical names
    rename_map = {}
    for canonical, group in duplicates.items():
        for name in group:
            rename_map[name] = canonical
    
    # Remove duplicate schemas, keep canonical ones
    schemas = spec['components']['schemas']
    new_schemas = {}
    for name, schema_def in schemas.items():
        canonical = rename_map.get(name, name)
        if canonical == name or canonical not in new_schemas:
            new_schemas[canonical] = schema_def
    
    spec['components']['schemas'] = new_schemas
    
    # Update all $ref references
    def update_refs(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
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
    
    update_refs(spec)
    
    print_info(f"Writing {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    
    new_count = len(new_schemas)
    print_success(f"Consolidated {original_count} → {new_count} schemas (-{original_count - new_count})")
    
    return original_count, new_count


# ============================================================================
# STEP 2: RENAME SCHEMAS
# ============================================================================

def create_rename_map() -> dict:
    """Create mapping from verbose names to common names"""
    return {
        # User responses
        'CreateUserResponseDto': 'UserResponse',
        'DisableUserResponseDto': 'UserResponse',
        'EnableUserResponseDto': 'UserResponse',
        'GetUserByShortUuidResponseDto': 'UserResponse',
        'GetUserByUsernameResponseDto': 'UserResponse',
        'GetUserByUuidResponseDto': 'UserResponse',
        'ResetUserTrafficResponseDto': 'UserResponse',
        'RevokeUserSubscriptionResponseDto': 'UserResponse',
        'UpdateUserResponseDto': 'UserResponse',
        
        # Delete operations
        'DeleteConfigProfileResponseDto': 'DeleteResponse',
        'DeleteExternalSquadResponseDto': 'DeleteResponse',
        'DeleteHostResponseDto': 'DeleteResponse',
        'DeleteInfraProviderByUuidResponseDto': 'DeleteResponse',
        'DeleteInternalSquadResponseDto': 'DeleteResponse',
        'DeleteNodeResponseDto': 'DeleteResponse',
        'DeleteSubscriptionTemplateResponseDto': 'DeleteResponse',
        'DeleteUserResponseDto': 'DeleteResponse',
        'DeletePasskeyResponseDto': 'DeleteResponse',
        
        # Event operations
        'AddUsersToExternalSquadResponseDto': 'EventResponse',
        'AddUsersToInternalSquadResponseDto': 'EventResponse',
        'BulkAllResetTrafficUsersResponseDto': 'EventResponse',
        'BulkAllUpdateUsersResponseDto': 'EventResponse',
        'RemoveUsersFromExternalSquadResponseDto': 'EventResponse',
        'RemoveUsersFromInternalSquadResponseDto': 'EventResponse',
        'RestartAllNodesResponseDto': 'EventResponse',
        'RestartNodeResponseDto': 'EventResponse',
        
        # Bulk responses
        'BulkDeleteUsersByStatusResponseDto': 'BulkActionResponse',
        'BulkDeleteUsersResponseDto': 'BulkActionResponse',
        'BulkResetTrafficUsersResponseDto': 'BulkActionResponse',
        'BulkRevokeUsersSubscriptionResponseDto': 'BulkActionResponse',
        'BulkUpdateUsersResponseDto': 'BulkActionResponse',
        'BulkUpdateUsersSquadsResponseDto': 'BulkActionResponse',
        
        # Bulk requests
        'BulkDeleteHostsRequestDto': 'BulkUuidsRequest',
        'BulkDisableHostsRequestDto': 'BulkUuidsRequest',
        'BulkEnableHostsRequestDto': 'BulkUuidsRequest',
        'BulkResetTrafficUsersRequestDto': 'BulkUuidsRequest',
        'BulkRevokeUsersSubscriptionRequestDto': 'BulkUuidsRequest',
        'BulkUuidsRequestDto': 'BulkUuidsRequest',
        'BulkDeleteUsersRequestDto': 'BulkUuidsRequest',
        
        # Hosts
        'BulkDeleteHostsResponseDto': 'HostListResponse',
        'BulkDisableHostsResponseDto': 'HostListResponse',
        'BulkEnableHostsResponseDto': 'HostListResponse',
        'GetAllHostsResponseDto': 'HostListResponse',
        'SetInboundToManyHostsResponseDto': 'HostListResponse',
        'SetPortToManyHostsResponseDto': 'HostListResponse',
        
        # Auth tokens
        'LoginResponseDto': 'TokenResponse',
        'OAuth2CallbackResponseDto': 'TokenResponse',
        'RegisterResponseDto': 'TokenResponse',
        'TelegramCallbackResponseDto': 'TokenResponse',
        'VerifyPasskeyAuthenticationResponseDto': 'TokenResponse',
        
        # Node responses
        'CreateNodeResponseDto': 'NodeResponse',
        'DisableNodeResponseDto': 'NodeResponse',
        'EnableNodeResponseDto': 'NodeResponse',
        'GetOneNodeResponseDto': 'NodeResponse',
        'UpdateNodeResponseDto': 'NodeResponse',
        
        # Passkey/Auth
        'GetPasskeyRegistrationOptionsResponseDto': 'PasskeyOptionsResponse',
        'GetPasskeyAuthenticationOptionsResponseDto': 'PasskeyOptionsResponse',
        'VerifyPasskeyAuthenticationRequestDto': 'PasskeyOptionsResponse',
        'VerifyPasskeyRegistrationRequestDto': 'PasskeyOptionsResponse',
        
        # Settings
        'GetRemnawaveSettingsResponseDto': 'SettingsResponse',
        'UpdateRemnawaveSettingsResponseDto': 'SettingsResponse',
        
        # Passkeys
        'GetAllPasskeysResponseDto': 'PasskeysResponse',
        
        # Tags
        'GetAllTagsResponseDto': 'TagsResponse',
        'GetAllHostTagsResponseDto': 'TagsResponse',
        
        # Inbounds
        'GetAllInboundsResponseDto': 'InboundsResponse',
        'GetInboundsByProfileUuidResponseDto': 'InboundsResponse',
        
        # Snippets
        'CreateSnippetRequestDto': 'SnippetRequest',
        'UpdateSnippetRequestDto': 'SnippetRequest',
        'CreateSnippetResponseDto': 'SnippetsResponse',
        'DeleteSnippetResponseDto': 'SnippetsResponse',
        'GetSnippetsResponseDto': 'SnippetsResponse',
        'UpdateSnippetResponseDto': 'SnippetsResponse',
        
        # Nodes
        'GetAllNodesResponseDto': 'NodesResponse',
        'ReorderNodeResponseDto': 'NodesResponse',
        
        # Subscription Settings
        'GetSubscriptionSettingsResponseDto': 'SubscriptionSettingsResponse',
        'UpdateSubscriptionSettingsResponseDto': 'SubscriptionSettingsResponse',
        
        # HWID Devices
        'CreateUserHwidDeviceResponseDto': 'HwidDevicesResponse',
        'DeleteAllUserHwidDevicesResponseDto': 'HwidDevicesResponse',
        'DeleteUserHwidDeviceResponseDto': 'HwidDevicesResponse',
        'GetUserHwidDevicesResponseDto': 'HwidDevicesResponse',
        
        # Templates
        'CreateSubscriptionTemplateResponseDto': 'TemplateResponse',
        'GetTemplateResponseDto': 'TemplateResponse',
        'UpdateTemplateResponseDto': 'TemplateResponse',
        
        # Config Profiles
        'CreateConfigProfileResponseDto': 'ConfigProfileResponse',
        'GetConfigProfileByUuidResponseDto': 'ConfigProfileResponse',
        'UpdateConfigProfileResponseDto': 'ConfigProfileResponse',
        
        # Internal Squads
        'CreateInternalSquadResponseDto': 'InternalSquadResponse',
        'GetInternalSquadByUuidResponseDto': 'InternalSquadResponse',
        'UpdateInternalSquadResponseDto': 'InternalSquadResponse',
        
        # External Squads
        'CreateExternalSquadResponseDto': 'ExternalSquadResponse',
        'GetExternalSquadByUuidResponseDto': 'ExternalSquadResponse',
        'UpdateExternalSquadResponseDto': 'ExternalSquadResponse',
        
        # Hosts
        'CreateHostResponseDto': 'HostResponse',
        'GetOneHostResponseDto': 'HostResponse',
        'UpdateHostResponseDto': 'HostResponse',
        
        # Infra Providers
        'CreateInfraProviderResponseDto': 'InfraProviderResponse',
        'GetInfraProviderByUuidResponseDto': 'InfraProviderResponse',
        'UpdateInfraProviderResponseDto': 'InfraProviderResponse',
        
        # Billing
        'CreateInfraBillingNodeResponseDto': 'BillingNodesResponse',
        'DeleteInfraBillingNodeByUuidResponseDto': 'BillingNodesResponse',
        'GetInfraBillingNodesResponseDto': 'BillingNodesResponse',
        'UpdateInfraBillingNodeResponseDto': 'BillingNodesResponse',
        'CreateInfraBillingHistoryRecordResponseDto': 'BillingHistoryResponse',
        'DeleteInfraBillingHistoryRecordByUuidResponseDto': 'BillingHistoryResponse',
        'GetInfraBillingHistoryRecordsResponseDto': 'BillingHistoryResponse',
        
        # Subscriptions
        'GetSubscriptionByShortUuidProtectedResponseDto': 'SubscriptionResponse',
        'GetSubscriptionByUsernameResponseDto': 'SubscriptionResponse',
        'GetSubscriptionByUuidResponseDto': 'SubscriptionResponse',
        'GetSubscriptionInfoResponseDto': 'SubscriptionResponse',
        
        # Users
        'GetUserByEmailResponseDto': 'UsersResponse',
        'GetUserByTagResponseDto': 'UsersResponse',
        'GetUserByTelegramIdResponseDto': 'UsersResponse',
    }


def rename_schemas(input_file: str, output_file: str) -> int:
    """Rename schemas to common names"""
    print_info(f"Loading {input_file}...")
    with open(input_file, 'r') as f:
        spec = json.load(f)
    
    rename_map = create_rename_map()
    
    # Rename schemas
    schemas = spec.get('components', {}).get('schemas', {})
    new_schemas = {}
    renamed_count = 0
    
    for old_name, schema_def in schemas.items():
        new_name = rename_map.get(old_name, old_name)
        if new_name != old_name:
            renamed_count += 1
        new_schemas[new_name] = schema_def
    
    spec['components']['schemas'] = new_schemas
    
    # Update all $ref references
    def update_refs(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
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
    
    update_refs(spec)
    
    print_info(f"Writing {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    
    print_success(f"Renamed {renamed_count} schemas to common names")
    
    return renamed_count


# ============================================================================
# STEP 3: GENERATE GO CLIENT WITH OGEN
# ============================================================================

def generate_ogen_client(spec_file: str) -> bool:
    """Generate Go client using ogen"""
    print_info("Running go generate...")
    
    try:
        result = subprocess.run(
            ['go', 'generate', './...'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print_success("Go client generated successfully")
            return True
        else:
            print_error(f"ogen generation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print_error("ogen generation timed out")
        return False
    except Exception as e:
        print_error(f"Error running go generate: {e}")
        return False


# ============================================================================
# STEP 4: GENERATE CLIENT_EXT.GO
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
        
        # Parse params (skip ctx)
        params_list = []
        if ', ' in full_params:
            params_str = full_params.split(', ', 1)[1]
            for param in re.findall(r'(\w+)\s+([\*\w\.]+)', params_str):
                params_list.append((param[0], param[1]))
        
        returns_list = [r.strip() for r in returns.split(',')]
        
        methods[method_name] = {
            'params': params_list,
            'returns': returns_list
        }
    
    return methods


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
            
            # Convert to PascalCase preserving camelCase
            def to_pascal(s):
                if not s:
                    return s
                return s[0].upper() + s[1:]
            
            parts = method_snake.split('_')
            method_pascal = ''.join(to_pascal(p) for p in parts)
            
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
    """Generate client_ext.go wrapper"""
    print_info("Parsing oas_client_gen.go...")
    methods = parse_oas_client_methods(client_file)
    print_success(f"Found {len(methods)} client methods")
    
    print_info("Parsing operations from spec...")
    operations_by_controller = parse_operations(spec_file)
    total_ops = sum(len(ops) for ops in operations_by_controller.values())
    print_success(f"Found {total_ops} operations in {len(operations_by_controller)} controllers")
    
    def to_camel(s):
        return s[0].lower() + s[1:] if s else s
    
    # Generate code
    code = '''// Code generated by pipeline.py. DO NOT EDIT manually.

package api

import "context"

// ClientExt wraps the base Client with organized sub-client access.
type ClientExt struct {
\t*Client
'''
    
    for controller in sorted(operations_by_controller.keys()):
        field_name = to_camel(controller)
        code += f'\t{field_name} *{controller}Client\n'
    
    code += '''}

// NewClientExt creates a new ClientExt wrapper.
func NewClientExt(client *Client) *ClientExt {
\treturn &ClientExt{
\t\tClient: client,
'''
    
    for controller in sorted(operations_by_controller.keys()):
        field_name = to_camel(controller)
        code += f'\t\t{field_name}: New{controller}Client(client),\n'
    
    code += '''\t}
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
            
            if params:
                params_sig = ', '.join([f'{p[0]} {p[1]}' for p in params])
                params_call = ', '.join([p[0] for p in params])
            else:
                params_sig = ''
                params_call = ''
            
            if returns:
                ret_type = ', '.join(returns)
                if len(returns) > 1:
                    ret_type = f'({ret_type})'
            else:
                ret_type = ''
            
            code += f'''// {display_method} calls {op_id}.
func (sc *{controller}Client) {display_method}(ctx context.Context'''
            
            if params_sig:
                code += f', {params_sig}'
            
            code += ')'
            
            if ret_type:
                code += f' {ret_type}'
            
            code += ' {\n'
            
            if returns:
                code += f'\treturn sc.client.{go_method}(ctx'
            else:
                code += f'\tsc.client.{go_method}(ctx'
            
            if params_call:
                code += f', {params_call}'
            
            code += ')\n}\n\n'
    
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
    
    # File paths
    consolidated_file = input_spec.replace('.json', '-consolidated.json')
    renamed_file = input_spec.replace('.json', '-final.json')
    client_gen_file = 'api/oas_client_gen.go'
    client_ext_file = 'api/client_ext.go'
    
    try:
        # Step 1: Consolidate
        print_step(1, 4, "CONSOLIDATE DUPLICATE SCHEMAS")
        orig_count, new_count = consolidate_schemas(input_spec, consolidated_file)
        
        # Step 2: Rename
        print_step(2, 4, "RENAME SCHEMAS TO COMMON NAMES")
        renamed_count = rename_schemas(consolidated_file, renamed_file)
        
        # Step 3: Generate with ogen
        print_step(3, 4, "GENERATE GO CLIENT WITH OGEN")
        if not generate_ogen_client(renamed_file):
            print_error("Failed to generate Go client")
            sys.exit(1)
        
        # Step 4: Generate client_ext
        print_step(4, 4, "GENERATE CLIENT_EXT.GO WRAPPER")
        ctrl_count, method_count = generate_client_ext(renamed_file, client_gen_file, client_ext_file)
        
        # Summary
        print(f"\n{Colors.BOLD}{Colors.GREEN}")
        print("="*70)
        print(" PIPELINE COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"{Colors.END}")
        print(f"\n{Colors.BOLD}Results:{Colors.END}")
        print(f"  • Schemas:     {orig_count} → {new_count} (-{orig_count - new_count}, -{(orig_count-new_count)*100//orig_count}%)")
        print(f"  • Renamed:     {renamed_count} schemas")
        print(f"  • Controllers: {ctrl_count}")
        print(f"  • Methods:     {method_count}")
        print(f"\n{Colors.BOLD}Generated files:{Colors.END}")
        print(f"  • {consolidated_file}")
        print(f"  • {renamed_file}")
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
