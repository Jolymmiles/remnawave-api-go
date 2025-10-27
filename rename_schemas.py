#!/usr/bin/env python3
"""
Rename consolidated schemas to more common naming conventions.

Changes patterns like:
- CreateUserResponseDto → UserResponse
- DeleteResponseDto → DeleteResponse  
- EventResponseDto → EventResponse
- BulkActionResponseDto → BulkActionResponse
- BulkUuidsRequestDto → BulkUuidsRequest
"""

import json
import sys
from pathlib import Path


def create_rename_map() -> dict:
    """Create mapping from old names to new common names."""
    return {
        # User responses (9 schemas)
        'CreateUserResponseDto': 'UserResponse',
        'DisableUserResponseDto': 'UserResponse',
        'EnableUserResponseDto': 'UserResponse',
        'GetUserByShortUuidResponseDto': 'UserResponse',
        'GetUserByUsernameResponseDto': 'UserResponse',
        'GetUserByUuidResponseDto': 'UserResponse',
        'ResetUserTrafficResponseDto': 'UserResponse',
        'RevokeUserSubscriptionResponseDto': 'UserResponse',
        'UpdateUserResponseDto': 'UserResponse',
        
        # Delete operations (8 schemas)
        'DeleteConfigProfileResponseDto': 'DeleteResponse',
        'DeleteExternalSquadResponseDto': 'DeleteResponse',
        'DeleteHostResponseDto': 'DeleteResponse',
        'DeleteInfraProviderByUuidResponseDto': 'DeleteResponse',
        'DeleteInternalSquadResponseDto': 'DeleteResponse',
        'DeleteNodeResponseDto': 'DeleteResponse',
        'DeleteSubscriptionTemplateResponseDto': 'DeleteResponse',
        'DeleteUserResponseDto': 'DeleteResponse',
        'DeletePasskeyResponseDto': 'DeleteResponse',
        
        # Event operations (8 schemas)
        'AddUsersToExternalSquadResponseDto': 'EventResponse',
        'AddUsersToInternalSquadResponseDto': 'EventResponse',
        'BulkAllResetTrafficUsersResponseDto': 'EventResponse',
        'BulkAllUpdateUsersResponseDto': 'EventResponse',
        'RemoveUsersFromExternalSquadResponseDto': 'EventResponse',
        'RemoveUsersFromInternalSquadResponseDto': 'EventResponse',
        'RestartAllNodesResponseDto': 'EventResponse',
        'RestartNodeResponseDto': 'EventResponse',
        
        # Bulk responses (6 schemas)
        'BulkDeleteUsersByStatusResponseDto': 'BulkActionResponse',
        'BulkDeleteUsersResponseDto': 'BulkActionResponse',
        'BulkResetTrafficUsersResponseDto': 'BulkActionResponse',
        'BulkRevokeUsersSubscriptionResponseDto': 'BulkActionResponse',
        'BulkUpdateUsersResponseDto': 'BulkActionResponse',
        'BulkUpdateUsersSquadsResponseDto': 'BulkActionResponse',
        
        # Bulk requests (6 schemas)
        'BulkDeleteHostsRequestDto': 'BulkUuidsRequest',
        'BulkDisableHostsRequestDto': 'BulkUuidsRequest',
        'BulkEnableHostsRequestDto': 'BulkUuidsRequest',
        'BulkResetTrafficUsersRequestDto': 'BulkUuidsRequest',
        'BulkRevokeUsersSubscriptionRequestDto': 'BulkUuidsRequest',
        'BulkUuidsRequestDto': 'BulkUuidsRequest',
        
        # Hosts (6 schemas)
        'BulkDeleteHostsResponseDto': 'HostListResponse',
        'BulkDisableHostsResponseDto': 'HostListResponse',
        'BulkEnableHostsResponseDto': 'HostListResponse',
        'GetAllHostsResponseDto': 'HostListResponse',
        'SetInboundToManyHostsResponseDto': 'HostListResponse',
        'SetPortToManyHostsResponseDto': 'HostListResponse',
        
        # Auth tokens (5 schemas)
        'LoginResponseDto': 'TokenResponse',
        'OAuth2CallbackResponseDto': 'TokenResponse',
        'RegisterResponseDto': 'TokenResponse',
        'TelegramCallbackResponseDto': 'TokenResponse',
        'VerifyPasskeyAuthenticationResponseDto': 'TokenResponse',
        
        # Node responses (5 schemas)
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
        
        # Subscriptions (4 schemas)
        'GetSubscriptionByShortUuidProtectedResponseDto': 'SubscriptionResponse',
        'GetSubscriptionByUsernameResponseDto': 'SubscriptionResponse',
        'GetSubscriptionByUuidResponseDto': 'SubscriptionResponse',
        'GetSubscriptionInfoResponseDto': 'SubscriptionResponse',
        
        # Snippets (4 schemas)
        'CreateSnippetResponseDto': 'SnippetsResponse',
        'DeleteSnippetResponseDto': 'SnippetsResponse',
        'GetSnippetsResponseDto': 'SnippetsResponse',
        'UpdateSnippetResponseDto': 'SnippetsResponse',
        
        # HWID Devices (4 schemas)
        'CreateUserHwidDeviceResponseDto': 'HwidDevicesResponse',
        'DeleteAllUserHwidDevicesResponseDto': 'HwidDevicesResponse',
        'DeleteUserHwidDeviceResponseDto': 'HwidDevicesResponse',
        'GetUserHwidDevicesResponseDto': 'HwidDevicesResponse',
        
        # Billing Nodes (4 schemas)
        'CreateInfraBillingNodeResponseDto': 'BillingNodesResponse',
        'DeleteInfraBillingNodeByUuidResponseDto': 'BillingNodesResponse',
        'GetInfraBillingNodesResponseDto': 'BillingNodesResponse',
        'UpdateInfraBillingNodeResponseDto': 'BillingNodesResponse',
        
        # Other mappings for remaining schemas
        'GetUserByEmailResponseDto': 'UsersResponse',
        'GetUserByTagResponseDto': 'UsersResponse',
        'GetUserByTelegramIdResponseDto': 'UsersResponse',
        
        'CreateSubscriptionTemplateResponseDto': 'TemplateResponse',
        'GetTemplateResponseDto': 'TemplateResponse',
        'UpdateTemplateResponseDto': 'TemplateResponse',
        
        'CreateConfigProfileResponseDto': 'ConfigProfileResponse',
        'GetConfigProfileByUuidResponseDto': 'ConfigProfileResponse',
        'UpdateConfigProfileResponseDto': 'ConfigProfileResponse',
        
        'CreateInternalSquadResponseDto': 'InternalSquadResponse',
        'GetInternalSquadByUuidResponseDto': 'InternalSquadResponse',
        'UpdateInternalSquadResponseDto': 'InternalSquadResponse',
        
        'CreateExternalSquadResponseDto': 'ExternalSquadResponse',
        'GetExternalSquadByUuidResponseDto': 'ExternalSquadResponse',
        'UpdateExternalSquadResponseDto': 'ExternalSquadResponse',
        
        'CreateHostResponseDto': 'HostResponse',
        'GetOneHostResponseDto': 'HostResponse',
        'UpdateHostResponseDto': 'HostResponse',
        
        'CreateInfraProviderResponseDto': 'InfraProviderResponse',
        'GetInfraProviderByUuidResponseDto': 'InfraProviderResponse',
        'UpdateInfraProviderResponseDto': 'InfraProviderResponse',
        
        'CreateInfraBillingHistoryRecordResponseDto': 'BillingHistoryResponse',
        'DeleteInfraBillingHistoryRecordByUuidResponseDto': 'BillingHistoryResponse',
        'GetInfraBillingHistoryRecordsResponseDto': 'BillingHistoryResponse',
        
        'GetRemnawaveSettingsResponseDto': 'SettingsResponse',
        'UpdateRemnawaveSettingsResponseDto': 'SettingsResponse',
        
        'GetAllPasskeysResponseDto': 'PasskeysResponse',
        
        'GetAllTagsResponseDto': 'TagsResponse',
        'GetAllHostTagsResponseDto': 'TagsResponse',
        
        'GetAllInboundsResponseDto': 'InboundsResponse',
        'GetInboundsByProfileUuidResponseDto': 'InboundsResponse',
        
        'CreateSnippetRequestDto': 'SnippetRequest',
        'UpdateSnippetRequestDto': 'SnippetRequest',
        
        'GetAllNodesResponseDto': 'NodesResponse',
        'ReorderNodeResponseDto': 'NodesResponse',
        
        'GetSubscriptionSettingsResponseDto': 'SubscriptionSettingsResponse',
        'UpdateSubscriptionSettingsResponseDto': 'SubscriptionSettingsResponse',
    }


def rename_schemas_in_spec(spec: dict, rename_map: dict) -> dict:
    """Rename all schemas in the OpenAPI spec."""
    schemas = spec.get('components', {}).get('schemas', {})
    
    new_schemas = {}
    for old_name, schema_def in schemas.items():
        new_name = rename_map.get(old_name, old_name)
        new_schemas[new_name] = schema_def
    
    spec['components']['schemas'] = new_schemas
    return spec


def update_schema_references(spec: dict, rename_map: dict) -> dict:
    """Update all $ref references to use new schema names."""
    
    def replace_refs(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == '$ref' and isinstance(value, str):
                    if value.startswith('#/components/schemas/'):
                        old_name = value.replace('#/components/schemas/', '')
                        new_name = rename_map.get(old_name, old_name)
                        obj[key] = f'#/components/schemas/{new_name}'
                else:
                    replace_refs(value)
        elif isinstance(obj, list):
            for item in obj:
                replace_refs(item)
    
    replace_refs(spec)
    return spec


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 rename_schemas.py <input_file> [output_file]")
        print("Example: python3 rename_schemas.py api-2-2-2-consolidated.json api-2-2-2-renamed.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '-renamed.json')
    
    print(f"📂 Loading {input_file}...")
    with open(input_file, 'r') as f:
        spec = json.load(f)
    
    rename_map = create_rename_map()
    
    print(f"🔄 Renaming {len(rename_map)} schemas to common names...")
    spec = rename_schemas_in_spec(spec, rename_map)
    
    print(f"🔗 Updating all schema references...")
    spec = update_schema_references(spec, rename_map)
    
    print(f"💾 Saving to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Done! Renamed schemas saved to {output_file}")
    print(f"\nSchema name mappings applied:")
    for old, new in sorted(rename_map.items()):
        if old != new:
            print(f"  {old} → {new}")


if __name__ == "__main__":
    main()
