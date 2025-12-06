#!/usr/bin/env python3
"""
Create consolidated OpenAPI schema by extracting schemas section
and applying consolidation mappings based on detected duplicate patterns.

This tool works with potentially malformed JSON files by extracting only
the schemas section and rebuilding a clean OpenAPI spec.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def extract_schemas_section(filepath: str) -> dict:
    """Extract only the schemas section from a potentially malformed OpenAPI file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    schemas_start = content.find('"schemas": {')
    if schemas_start < 0:
        raise ValueError('Could not find "schemas" section')
    
    schemas_part = content[schemas_start + len('"schemas": '):]
    
    # Count braces to find the end
    brace_count = 0
    in_string = False
    escape = False
    end_pos = 0
    
    for i, char in enumerate(schemas_part):
        if escape:
            escape = False
            continue
        if char == '\\':
            escape = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break
    
    schemas_json = schemas_part[:end_pos]
    wrapped = '{"schemas": ' + schemas_json + '}'
    data = json.loads(wrapped)
    return data['schemas']


def create_consolidation_map() -> dict:
    """
    Create consolidation map based on analyzed duplicate patterns.
    Maps: old_schema_name -> canonical_schema_name
    """
    return {
        # Group 1: User Responses (9 duplicates)
        'DisableUserResponseDto': 'CreateUserResponseDto',
        'EnableUserResponseDto': 'CreateUserResponseDto',
        'GetUserByShortUuidResponseDto': 'CreateUserResponseDto',
        'GetUserByUsernameResponseDto': 'CreateUserResponseDto',
        'GetUserByUuidResponseDto': 'CreateUserResponseDto',
        'ResetUserTrafficResponseDto': 'CreateUserResponseDto',
        'RevokeUserSubscriptionResponseDto': 'CreateUserResponseDto',
        'UpdateUserResponseDto': 'CreateUserResponseDto',
        
        # Group 2: Delete Operations (8 duplicates)
        'DeleteConfigProfileResponseDto': 'DeleteResponseDto',
        'DeleteExternalSquadResponseDto': 'DeleteResponseDto',
        'DeleteHostResponseDto': 'DeleteResponseDto',
        'DeleteInfraProviderByUuidResponseDto': 'DeleteResponseDto',
        'DeleteInternalSquadResponseDto': 'DeleteResponseDto',
        'DeleteNodeResponseDto': 'DeleteResponseDto',
        'DeleteSubscriptionTemplateResponseDto': 'DeleteResponseDto',
        'DeleteUserResponseDto': 'DeleteResponseDto',
        
        # Group 3: Event Operations (8 duplicates)
        'AddUsersToExternalSquadResponseDto': 'EventResponseDto',
        'AddUsersToInternalSquadResponseDto': 'EventResponseDto',
        'BulkAllResetTrafficUsersResponseDto': 'EventResponseDto',
        'BulkAllUpdateUsersResponseDto': 'EventResponseDto',
        'RemoveUsersFromExternalSquadResponseDto': 'EventResponseDto',
        'RemoveUsersFromInternalSquadResponseDto': 'EventResponseDto',
        'RestartAllNodesResponseDto': 'EventResponseDto',
        'RestartNodeResponseDto': 'EventResponseDto',
        
        # Group 4: Bulk Operations Response (6 duplicates)
        'BulkDeleteUsersByStatusResponseDto': 'BulkActionResponseDto',
        'BulkDeleteUsersResponseDto': 'BulkActionResponseDto',
        'BulkResetTrafficUsersResponseDto': 'BulkActionResponseDto',
        'BulkRevokeUsersSubscriptionResponseDto': 'BulkActionResponseDto',
        'BulkUpdateUsersResponseDto': 'BulkActionResponseDto',
        'BulkUpdateUsersSquadsResponseDto': 'BulkActionResponseDto',
        
        # Group 5: Bulk Request (6 duplicates)
        'BulkDeleteHostsRequestDto': 'BulkUuidsRequestDto',
        'BulkDisableHostsRequestDto': 'BulkUuidsRequestDto',
        'BulkEnableHostsRequestDto': 'BulkUuidsRequestDto',
        'BulkResetTrafficUsersRequestDto': 'BulkUuidsRequestDto',
        'BulkRevokeUsersSubscriptionRequestDto': 'BulkUuidsRequestDto',
        
        # Group 6: Hosts Response (6 duplicates)
        'BulkDeleteHostsResponseDto': 'GetAllHostsResponseDto',
        'BulkDisableHostsResponseDto': 'GetAllHostsResponseDto',
        'BulkEnableHostsResponseDto': 'GetAllHostsResponseDto',
        'SetInboundToManyHostsResponseDto': 'GetAllHostsResponseDto',
        'SetPortToManyHostsResponseDto': 'GetAllHostsResponseDto',
        
        # Group 7: Token Responses (5 duplicates)
        'OAuth2CallbackResponseDto': 'LoginResponseDto',
        'RegisterResponseDto': 'LoginResponseDto',
        'TelegramCallbackResponseDto': 'LoginResponseDto',
        'VerifyPasskeyAuthenticationResponseDto': 'LoginResponseDto',
        
        # Group 8: Node Responses (5 duplicates)
        'DisableNodeResponseDto': 'CreateNodeResponseDto',
        'EnableNodeResponseDto': 'CreateNodeResponseDto',
        'GetOneNodeResponseDto': 'CreateNodeResponseDto',
        'UpdateNodeResponseDto': 'CreateNodeResponseDto',
        
        # Group 9: Empty Wrapper (4 duplicates)
        'GetPasskeyAuthenticationOptionsResponseDto': 'GetPasskeyRegistrationOptionsResponseDto',
        'VerifyPasskeyAuthenticationRequestDto': 'GetPasskeyRegistrationOptionsResponseDto',
        'VerifyPasskeyRegistrationRequestDto': 'GetPasskeyRegistrationOptionsResponseDto',
        
        # Group 10: Subscription Info (4 duplicates)
        'GetSubscriptionByShortUuidProtectedResponseDto': 'GetSubscriptionInfoResponseDto',
        'GetSubscriptionByUsernameResponseDto': 'GetSubscriptionInfoResponseDto',
        'GetSubscriptionByUuidResponseDto': 'GetSubscriptionInfoResponseDto',
        
        # Group 11: Snippet Operations (4 duplicates)
        'CreateSnippetResponseDto': 'GetSnippetsResponseDto',
        'DeleteSnippetResponseDto': 'GetSnippetsResponseDto',
        'UpdateSnippetResponseDto': 'GetSnippetsResponseDto',
        
        # Group 12: HWID Devices (4 duplicates)
        'CreateUserHwidDeviceResponseDto': 'GetUserHwidDevicesResponseDto',
        'DeleteAllUserHwidDevicesResponseDto': 'GetUserHwidDevicesResponseDto',
        'DeleteUserHwidDeviceResponseDto': 'GetUserHwidDevicesResponseDto',
        
        # Group 13: Billing Nodes (4 duplicates)
        'CreateInfraBillingNodeResponseDto': 'GetInfraBillingNodesResponseDto',
        'DeleteInfraBillingNodeByUuidResponseDto': 'GetInfraBillingNodesResponseDto',
        'UpdateInfraBillingNodeResponseDto': 'GetInfraBillingNodesResponseDto',
        
        # Group 14: User Search (3 duplicates)
        'GetUserByEmailResponseDto': 'GetUserByTelegramIdResponseDto',
        'GetUserByTagResponseDto': 'GetUserByTelegramIdResponseDto',
        
        # Group 15: Templates (3 duplicates)
        'CreateSubscriptionTemplateResponseDto': 'GetTemplateResponseDto',
        'UpdateTemplateResponseDto': 'GetTemplateResponseDto',
        
        # Group 16: Config Profiles (3 duplicates)
        'CreateConfigProfileResponseDto': 'GetConfigProfileByUuidResponseDto',
        'UpdateConfigProfileResponseDto': 'GetConfigProfileByUuidResponseDto',
        
        # Group 17: Internal Squads (3 duplicates)
        'CreateInternalSquadResponseDto': 'GetInternalSquadByUuidResponseDto',
        'UpdateInternalSquadResponseDto': 'GetInternalSquadByUuidResponseDto',
        
        # Group 18: External Squads (3 duplicates)
        'CreateExternalSquadResponseDto': 'GetExternalSquadByUuidResponseDto',
        'UpdateExternalSquadResponseDto': 'GetExternalSquadByUuidResponseDto',
        
        # Group 19: Hosts (3 duplicates)
        'CreateHostResponseDto': 'GetOneHostResponseDto',
        'UpdateHostResponseDto': 'GetOneHostResponseDto',
        
        # Group 20: Infrastructure Providers (3 duplicates)
        'CreateInfraProviderResponseDto': 'GetInfraProviderByUuidResponseDto',
        'UpdateInfraProviderResponseDto': 'GetInfraProviderByUuidResponseDto',
        
        # Group 21: Billing History (3 duplicates)
        'CreateInfraBillingHistoryRecordResponseDto': 'GetInfraBillingHistoryRecordsResponseDto',
        'DeleteInfraBillingHistoryRecordByUuidResponseDto': 'GetInfraBillingHistoryRecordsResponseDto',
        
        # Group 22: Settings (2 duplicates)
        'UpdateRemnawaveSettingsResponseDto': 'GetRemnawaveSettingsResponseDto',
        
        # Group 23: Passkeys (2 duplicates)
        'DeletePasskeyResponseDto': 'GetAllPasskeysResponseDto',
        
        # Group 24: Tags (2 duplicates)
        'GetAllHostTagsResponseDto': 'GetAllTagsResponseDto',
        
        # Group 25: Inbounds (2 duplicates)
        'GetInboundsByProfileUuidResponseDto': 'GetAllInboundsResponseDto',
        
        # Group 26: Snippet Requests (2 duplicates)
        'UpdateSnippetRequestDto': 'CreateSnippetRequestDto',
        
        # Group 27: Nodes (2 duplicates)
        'ReorderNodeResponseDto': 'GetAllNodesResponseDto',
        
        # Group 28: Subscription Settings (2 duplicates)
        'UpdateSubscriptionSettingsResponseDto': 'GetSubscriptionSettingsResponseDto',
    }


def create_canonical_schemas(original_schemas: dict, consolidation_map: dict) -> dict:
    """
    Create new schemas dict with canonical names and new generic schemas.
    """
    # Get all canonical names from mapping
    canonical_names = set(consolidation_map.values())
    duplicates_to_remove = set(consolidation_map.keys())
    
    # Keep only canonical schemas
    new_schemas = {}
    for name, schema_def in original_schemas.items():
        if name not in duplicates_to_remove:
            new_schemas[name] = schema_def
    
    # Add new generic schemas based on patterns found
    new_schemas['DeleteResponseDto'] = {
        "properties": {
            "response": {
                "properties": {
                    "isDeleted": {"type": "boolean"}
                },
                "required": ["isDeleted"],
                "type": "object"
            }
        },
        "required": ["response"],
        "type": "object"
    }
    
    new_schemas['EventResponseDto'] = {
        "properties": {
            "response": {
                "properties": {
                    "eventSent": {"type": "boolean"}
                },
                "required": ["eventSent"],
                "type": "object"
            }
        },
        "required": ["response"],
        "type": "object"
    }
    
    new_schemas['BulkActionResponseDto'] = {
        "properties": {
            "response": {
                "properties": {
                    "affectedRows": {"type": "number"}
                },
                "required": ["affectedRows"],
                "type": "object"
            }
        },
        "required": ["response"],
        "type": "object"
    }
    
    new_schemas['BulkUuidsRequestDto'] = {
        "properties": {
            "uuids": {
                "items": {
                    "format": "uuid",
                    "type": "string"
                },
                "type": "array"
            }
        },
        "required": ["uuids"],
        "type": "object"
    }
    
    return new_schemas


def replace_refs_in_spec(spec: dict, consolidation_map: dict) -> dict:
    """Replace all $ref references to consolidated schemas throughout the spec."""
    
    def replace_in_value(value):
        if isinstance(value, dict):
            if '$ref' in value:
                ref = value['$ref']
                if ref.startswith('#/components/schemas/'):
                    schema_name = ref.replace('#/components/schemas/', '')
                    if schema_name in consolidation_map:
                        value['$ref'] = f"#/components/schemas/{consolidation_map[schema_name]}"
            else:
                for k, v in value.items():
                    value[k] = replace_in_value(v)
        elif isinstance(value, list):
            return [replace_in_value(item) for item in value]
        
        return value
    
    replace_in_value(spec)
    return spec


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 create_consolidated_schema.py <input_file> [output_file]", file=sys.stderr)
        print("Example: python3 create_consolidated_schema.py api-2-2-0.json api-2-2-0-consolidated.json", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '-consolidated.json')
    
    try:
        print(f"📂 Extracting schemas from: {input_file}")
        original_schemas = extract_schemas_section(input_file)
        print(f"✓ Found {len(original_schemas)} schemas")
        
        print("\n🔍 Creating consolidation mapping...")
        consolidation_map = create_consolidation_map()
        
        # Count consolidations
        consolidations = len(consolidation_map)
        canonical_count = len(set(consolidation_map.values()))
        
        print(f"✓ Will consolidate {consolidations} schemas into {canonical_count} canonical schemas")
        
        print("\n📝 Creating consolidated schemas...")
        new_schemas = create_canonical_schemas(original_schemas, consolidation_map)
        print(f"✓ New schema count: {len(new_schemas)}")
        
        print("\n📖 Loading full OpenAPI spec...")
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find last valid JSON brace
        brace_count = 0
        in_string = False
        escape = False
        last_valid = 0
        
        for i, char in enumerate(content):
            if escape:
                escape = False
                continue
            if char == '\\':
                escape = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        last_valid = i + 1
        
        # Load truncated JSON
        full_spec = json.loads(content[:last_valid])
        
        print("🔄 Replacing all schema references...")
        full_spec = replace_refs_in_spec(full_spec, consolidation_map)
        
        print("📝 Updating schemas in spec...")
        full_spec['components']['schemas'] = new_schemas
        
        print(f"\n💾 Writing consolidated spec to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(full_spec, f, indent=2, ensure_ascii=False)
        
        # Print summary
        schemas_removed = len(original_schemas) - len(new_schemas)
        reduction_pct = (schemas_removed / len(original_schemas)) * 100
        
        print(f"\n✅ CONSOLIDATION COMPLETE")
        print(f"   Original schemas:     {len(original_schemas)}")
        print(f"   Consolidated schemas: {len(new_schemas)}")
        print(f"   Schemas removed:      {schemas_removed}")
        print(f"   Reduction:            {reduction_pct:.1f}%")
        print(f"   Generic schemas:      {canonical_count}")
        
        # Print mapping summary
        print(f"\n📋 CONSOLIDATION MAPPING:")
        grouped = defaultdict(list)
        for old, new in sorted(consolidation_map.items()):
            grouped[new].append(old)
        
        for canonical, duplicates in sorted(grouped.items()):
            print(f"   ✓ {canonical} (← {len(duplicates)} schemas)")
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
