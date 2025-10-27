# ClientExt Usage Guide - v2.2.2.1

Complete guide for using the organized `ClientExt` wrapper with all 139 API operations.

## Installation

```bash
go get github.com/Jolymmiles/remnawave-api-go@v2.2.2.1
```

## Basic Setup

```go
import remapi "github.com/Jolymmiles/remnawave-api-go/api"

// Create HTTP client
httpClient := &http.Client{
    Timeout: 30 * time.Second,
}

// Create base API client
baseClient, err := remapi.NewClient(
    "https://api.remnawave.local",
    httpClient,
)
if err != nil {
    log.Fatal(err)
}

// Wrap with ClientExt for organized access
client := remapi.NewClientExt(baseClient)
ctx := context.Background()
```

## Available Sub-Clients (24 total)

### 1. Users (17 operations)
```go
client.Users().GetAllUsers(ctx)
client.Users().CreateUser(ctx, req)
client.Users().GetUserByUsername(ctx, params)
client.Users().GetUsersByEmail(ctx, params)
client.Users().GetUserByShortUuid(ctx, params)
client.Users().GetUsersByTag(ctx, params)
client.Users().GetUserByTelegramId(ctx, params)
client.Users().GetUserByUuid(ctx, params)
client.Users().GetAllTags(ctx)
client.Users().DeleteUser(ctx, params)
client.Users().UpdateUser(ctx, req)
client.Users().GetUserAccessibleNodes(ctx, params)
client.Users().DisableUser(ctx, params)
client.Users().EnableUser(ctx, params)
client.Users().ResetUserTraffic(ctx, params)
client.Users().RevokeUserSubscription(ctx, params)
client.Users().GetUserSubscriptionRequestHistory(ctx, params)
```

### 2. Nodes (10 operations)
```go
client.Nodes().GetAllNodes(ctx)
client.Nodes().CreateNode(ctx, req)
client.Nodes().GetOneNode(ctx, params)
client.Nodes().UpdateNode(ctx, req)
client.Nodes().DeleteNode(ctx, params)
client.Nodes().ReorderNodes(ctx, req)
client.Nodes().RestartAllNodes(ctx, req)
client.Nodes().DisableNode(ctx, params)
client.Nodes().EnableNode(ctx, params)
client.Nodes().RestartNode(ctx, params)
```

### 3. Hosts (7 operations)
```go
client.Hosts().GetAllHosts(ctx)
client.Hosts().GetAllHostTags(ctx)
client.Hosts().CreateHost(ctx, req)
client.Hosts().UpdateHost(ctx, req)
client.Hosts().DeleteHost(ctx, params)
client.Hosts().GetOneHost(ctx, params)
client.Hosts().ReorderHosts(ctx, req)
```

### 4. Auth (8 operations)
```go
client.Auth().GetStatus(ctx)
client.Auth().Login(ctx, req)
client.Auth().Register(ctx, req)
client.Auth().OAuth2Authorize(ctx, req)
client.Auth().OAuth2Callback(ctx, req)
client.Auth().TelegramCallback(ctx, req)
client.Auth().PasskeyAuthenticationOptions(ctx)
client.Auth().PasskeyAuthenticationVerify(ctx, req)
```

### 5. System (8 operations)
```go
client.System().GetRemnawaveHealth(ctx)
client.System().GetStats(ctx)
client.System().GetBandwidthStats(ctx)
client.System().GetNodesStatistics(ctx)
client.System().GetNodesMetrics(ctx)
client.System().DebugSrrMatcher(ctx, req)
client.System().EncryptHappCryptoLink(ctx, req)
client.System().GetX25519Keypairs(ctx)
```

### 6. ApiTokens (3 operations)
```go
client.ApiTokens().FindAll(ctx)
client.ApiTokens().Create(ctx, req)
client.ApiTokens().Delete(ctx, params)
```

### 7. ConfigProfiles (7 operations)
```go
client.ConfigProfiles().GetConfigProfiles(ctx)
client.ConfigProfiles().GetAllInbounds(ctx)
client.ConfigProfiles().CreateConfigProfile(ctx, req)
client.ConfigProfiles().UpdateConfigProfile(ctx, req)
client.ConfigProfiles().GetConfigProfileByUuid(ctx, params)
client.ConfigProfiles().GetInboundsByProfileUuid(ctx, params)
client.ConfigProfiles().DeleteConfigProfileByUuid(ctx, params)
```

### 8. ExternalSquads (7 operations)
```go
client.ExternalSquads().GetExternalSquads(ctx)
client.ExternalSquads().GetExternalSquadByUuid(ctx, params)
client.ExternalSquads().CreateExternalSquad(ctx, req)
client.ExternalSquads().UpdateExternalSquad(ctx, req)
client.ExternalSquads().DeleteExternalSquad(ctx, params)
client.ExternalSquads().AddUsersToExternalSquad(ctx, params)
client.ExternalSquads().RemoveUsersFromExternalSquad(ctx, params)
```

### 9. InternalSquads (8 operations)
```go
client.InternalSquads().GetInternalSquads(ctx)
client.InternalSquads().GetInternalSquadByUuid(ctx, params)
client.InternalSquads().GetInternalSquadAccessibleNodes(ctx, params)
client.InternalSquads().CreateInternalSquad(ctx, req)
client.InternalSquads().UpdateInternalSquad(ctx, req)
client.InternalSquads().DeleteInternalSquad(ctx, params)
client.InternalSquads().AddUsersToInternalSquad(ctx, params)
client.InternalSquads().RemoveUsersFromInternalSquad(ctx, params)
```

### 10. HwidUserDevices (6 operations)
```go
client.HwidUserDevices().GetAllUsers(ctx)
client.HwidUserDevices().GetHwidDevicesStats(ctx)
client.HwidUserDevices().GetUserHwidDevices(ctx, params)
client.HwidUserDevices().CreateUserHwidDevice(ctx, req)
client.HwidUserDevices().DeleteUserHwidDevice(ctx, req)
client.HwidUserDevices().DeleteAllUserHwidDevices(ctx, req)
```

### 11. HostsBulkActions (5 operations)
```go
client.HostsBulkActions().EnableHosts(ctx, req)
client.HostsBulkActions().DisableHosts(ctx, req)
client.HostsBulkActions().DeleteHosts(ctx, req)
client.HostsBulkActions().SetInboundToHosts(ctx, req)
client.HostsBulkActions().SetPortToHosts(ctx, req)
```

### 12. InfraBilling (12 operations)
```go
client.InfraBilling().GetInfraProviders(ctx)
client.InfraBilling().GetInfraProviderByUuid(ctx, params)
client.InfraBilling().CreateInfraProvider(ctx, req)
client.InfraBilling().UpdateInfraProvider(ctx, req)
client.InfraBilling().DeleteInfraProviderByUuid(ctx, params)
client.InfraBilling().GetBillingNodes(ctx)
client.InfraBilling().CreateInfraBillingNode(ctx, req)
client.InfraBilling().UpdateInfraBillingNode(ctx, req)
client.InfraBilling().DeleteInfraBillingNodeByUuid(ctx, params)
client.InfraBilling().GetInfraBillingHistoryRecords(ctx)
client.InfraBilling().CreateInfraBillingHistoryRecord(ctx, req)
client.InfraBilling().DeleteInfraBillingHistoryRecordByUuid(ctx, params)
```

### 13. Keygen (1 operation)
```go
client.Keygen().GenerateKey(ctx)
```

### 14. Passkeys (4 operations)
```go
client.Passkeys().GetActivePasskeys(ctx)
client.Passkeys().PasskeyRegistrationOptions(ctx)
client.Passkeys().PasskeyRegistrationVerify(ctx, req)
client.Passkeys().DeletePasskey(ctx)
```

### 15. RemnawaveSettings (2 operations)
```go
client.RemnawaveSettings().GetSettings(ctx)
client.RemnawaveSettings().UpdateSettings(ctx, req)
```

### 16. Snippets (4 operations)
```go
client.Snippets().GetSnippets(ctx)
client.Snippets().GetSnippets(ctx)
client.Snippets().CreateSnippet(ctx, req)
client.Snippets().UpdateSnippet(ctx, req)
client.Snippets().DeleteSnippetByName(ctx)
```

### 17. SubscriptionRequestHistory (2 operations)
```go
client.SubscriptionRequestHistory().GetSubscriptionRequestHistory(ctx)
client.SubscriptionRequestHistory().GetSubscriptionRequestHistoryStats(ctx)
```

### 18. SubscriptionSettings (2 operations)
```go
client.SubscriptionSettings().GetSettings(ctx)
client.SubscriptionSettings().UpdateSettings(ctx, req)
```

### 19. SubscriptionTemplate (5 operations)
```go
client.SubscriptionTemplate().GetAllTemplates(ctx)
client.SubscriptionTemplate().GetTemplateByUuid(ctx, params)
client.SubscriptionTemplate().CreateTemplate(ctx, req)
client.SubscriptionTemplate().UpdateTemplate(ctx, req)
client.SubscriptionTemplate().DeleteTemplate(ctx, params)
```

### 20. UsersBulkActions (8 operations)
```go
client.UsersBulkActions().BulkDeleteUsers(ctx, req)
client.UsersBulkActions().BulkUpdateUsers(ctx, req)
client.UsersBulkActions().BulkDeleteUsersByStatus(ctx, req)
client.UsersBulkActions().BulkResetUserTraffic(ctx, req)
client.UsersBulkActions().BulkRevokeUsersSubscription(ctx, req)
client.UsersBulkActions().BulkUpdateAllUsers(ctx, req)
client.UsersBulkActions().BulkAllResetUserTraffic(ctx, req)
client.UsersBulkActions().BulkUpdateUsersInternalSquads(ctx, req)
```

### 21. UsersStats (1 operation)
```go
client.UsersStats().GetUserUsageByRange(ctx, params)
```

### 22. BandwidthStats (3 operations)
```go
client.BandwidthStats().GetNodesUsageByRange(ctx)
client.BandwidthStats().GetNodesRealtimeUsage(ctx)
client.BandwidthStats().GetNodeUserUsage(ctx, params)
```

### 23. ProtectedSubscriptions (5 operations)
```go
client.ProtectedSubscriptions().GetAllSubscriptions(ctx)
client.ProtectedSubscriptions().GetSubscriptionByUsername(ctx, params)
client.ProtectedSubscriptions().GetSubscriptionByShortUuidProtected(ctx, params)
client.ProtectedSubscriptions().GetRawSubscriptionByShortUuid(ctx, params)
client.ProtectedSubscriptions().GetSubscriptionByUuid(ctx, params)
```

### 24. PublicSubscription (4 operations)
```go
client.PublicSubscription().GetSubscription(ctx, params)
client.PublicSubscription().GetSubscriptionByClientType(ctx, params)
client.PublicSubscription().GetSubscriptionInfoByShortUuid(ctx, params)
client.PublicSubscription().GetSubscriptionWithType(ctx, params)
```

## Common Patterns

### Get with error handling
```go
users, err := client.Users().GetAllUsers(ctx)
if err != nil {
    log.Printf("Failed to get users: %v", err)
    return
}
fmt.Printf("Found %d users\n", len(users))
```

### Context with timeout
```go
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

users, err := client.Users().GetAllUsers(ctx)
```

### Bulk operations
```go
// Delete multiple users
req := &remapi.BulkUuidsRequest{
    Uuids: []string{"uuid1", "uuid2", "uuid3"},
}
result, err := client.UsersBulkActions().BulkDeleteUsers(ctx, req)
```

### Chain operations
```go
// Get all nodes, then get specific node
nodes, err := client.Nodes().GetAllNodes(ctx)
if err != nil {
    return err
}

for _, node := range nodes {
    detail, err := client.Nodes().GetOneNode(ctx, remapi.NodesControllerGetOneNodeParams{
        Uuid: node.Uuid,
    })
    if err != nil {
        log.Printf("Failed to get node details: %v", err)
        continue
    }
    fmt.Printf("Node: %v\n", detail)
}
```

## Error Handling with Unknown Fields

The library includes UnknownFieldsHandler for safe backward compatibility:

```go
decoder := remapi.NewUnknownFieldsDecoder()
decoder.SilentMode = true  // No error on unknown fields
err := decoder.DecodeWithUnknownFields(data, &response)
```

See `UNKNOWN_FIELDS_GUIDE.md` for more details.

## Summary

✅ **24 Sub-Clients**  
✅ **139 API Operations**  
✅ **Type-Safe**  
✅ **Organized by Function**  
✅ **Easy to Use**  
✅ **Production Ready**

All 139 API operations are accessible through organized, easy-to-use sub-clients. Use autocomplete in your IDE to discover available operations.
