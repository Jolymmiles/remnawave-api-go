# API Operations Coverage - v2.2.2.1

**Total Controllers:** 24  
**Total Operations:** 139

| Method | Count |
|--------|-------|
| GET | 63 |
| POST | 49 |
| DELETE | 15 |
| PATCH | 12 |

---

## 1. API Tokens Controller (3 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `ApiTokensController_findAll` | `/api/tokens` |
| 2 | 🔵 POST | `ApiTokensController_create` | `/api/tokens` |
| 3 | 🔴 DELETE | `ApiTokensController_delete` | `/api/tokens/{uuid}` |

---

## 2. Auth Controller (8 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🔵 POST | `AuthController_login` | `/api/auth/login` |
| 2 | 🔵 POST | `AuthController_oauth2Authorize` | `/api/auth/oauth2/authorize` |
| 3 | 🔵 POST | `AuthController_oauth2Callback` | `/api/auth/oauth2/callback` |
| 4 | 🔵 POST | `AuthController_telegramCallback` | `/api/auth/oauth2/tg/callback` |
| 5 | 🟢 GET | `AuthController_passkeyAuthenticationOptions` | `/api/auth/passkey/authentication/options` |
| 6 | 🔵 POST | `AuthController_passkeyAuthenticationVerify` | `/api/auth/passkey/authentication/verify` |
| 7 | 🔵 POST | `AuthController_register` | `/api/auth/register` |
| 8 | 🟢 GET | `AuthController_getStatus` | `/api/auth/status` |

---

## 3. Bandwidth Stats Controller (3 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `NodesUsageHistoryController_getNodesUsageByRange` | `/api/nodes/usage/range` |
| 2 | 🟢 GET | `NodesUserUsageHistoryController_getNodesRealtimeUsage` | `/api/nodes/usage/realtime` |
| 3 | 🟢 GET | `NodesUserUsageHistoryController_getNodeUserUsage` | `/api/nodes/usage/{uuid}/users/range` |

---

## 4. Config Profiles Controller (7 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `ConfigProfileController_getConfigProfiles` | `/api/config-profiles` |
| 2 | 🟡 PATCH | `ConfigProfileController_updateConfigProfile` | `/api/config-profiles` |
| 3 | 🔵 POST | `ConfigProfileController_createConfigProfile` | `/api/config-profiles` |
| 4 | 🟢 GET | `ConfigProfileController_getAllInbounds` | `/api/config-profiles/inbounds` |
| 5 | 🔴 DELETE | `ConfigProfileController_deleteConfigProfileByUuid` | `/api/config-profiles/{uuid}` |
| 6 | 🟢 GET | `ConfigProfileController_getConfigProfileByUuid` | `/api/config-profiles/{uuid}` |
| 7 | 🟢 GET | `ConfigProfileController_getInboundsByProfileUuid` | `/api/config-profiles/{uuid}/inbounds` |

---

## 5. External Squads Controller (7 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `ExternalSquadController_getExternalSquads` | `/api/external-squads` |
| 2 | 🟡 PATCH | `ExternalSquadController_updateExternalSquad` | `/api/external-squads` |
| 3 | 🔵 POST | `ExternalSquadController_createExternalSquad` | `/api/external-squads` |
| 4 | 🔴 DELETE | `ExternalSquadController_deleteExternalSquad` | `/api/external-squads/{uuid}` |
| 5 | 🟢 GET | `ExternalSquadController_getExternalSquadByUuid` | `/api/external-squads/{uuid}` |
| 6 | 🔵 POST | `ExternalSquadController_addUsersToExternalSquad` | `/api/external-squads/{uuid}/bulk-actions/add-users` |
| 7 | 🔴 DELETE | `ExternalSquadController_removeUsersFromExternalSquad` | `/api/external-squads/{uuid}/bulk-actions/remove-users` |

---

## 6. HWID User Devices Controller (6 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `HwidUserDevicesController_getAllUsers` | `/api/hwid/devices` |
| 2 | 🔵 POST | `HwidUserDevicesController_createUserHwidDevice` | `/api/hwid/devices` |
| 3 | 🔵 POST | `HwidUserDevicesController_deleteUserHwidDevice` | `/api/hwid/devices/delete` |
| 4 | 🔵 POST | `HwidUserDevicesController_deleteAllUserHwidDevices` | `/api/hwid/devices/delete-all` |
| 5 | 🟢 GET | `HwidUserDevicesController_getHwidDevicesStats` | `/api/hwid/devices/stats` |
| 6 | 🟢 GET | `HwidUserDevicesController_getUserHwidDevices` | `/api/hwid/devices/{userUuid}` |

---

## 7. Hosts Bulk Actions Controller (5 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🔵 POST | `HostsBulkActionsController_deleteHosts` | `/api/hosts/bulk/delete` |
| 2 | 🔵 POST | `HostsBulkActionsController_disableHosts` | `/api/hosts/bulk/disable` |
| 3 | 🔵 POST | `HostsBulkActionsController_enableHosts` | `/api/hosts/bulk/enable` |
| 4 | 🔵 POST | `HostsBulkActionsController_setInboundToHosts` | `/api/hosts/bulk/set-inbound` |
| 5 | 🔵 POST | `HostsBulkActionsController_setPortToHosts` | `/api/hosts/bulk/set-port` |

---

## 8. Hosts Controller (7 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `HostsController_getAllHosts` | `/api/hosts` |
| 2 | 🟡 PATCH | `HostsController_updateHost` | `/api/hosts` |
| 3 | 🔵 POST | `HostsController_createHost` | `/api/hosts` |
| 4 | 🔵 POST | `HostsController_reorderHosts` | `/api/hosts/actions/reorder` |
| 5 | 🟢 GET | `HostsController_getAllHostTags` | `/api/hosts/tags` |
| 6 | 🔴 DELETE | `HostsController_deleteHost` | `/api/hosts/{uuid}` |
| 7 | 🟢 GET | `HostsController_getOneHost` | `/api/hosts/{uuid}` |

---

## 9. Infra Billing Controller (12 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `InfraBillingController_getInfraBillingHistoryRecords` | `/api/infra-billing/history` |
| 2 | 🔵 POST | `InfraBillingController_createInfraBillingHistoryRecord` | `/api/infra-billing/history` |
| 3 | 🔴 DELETE | `InfraBillingController_deleteInfraBillingHistoryRecordByUuid` | `/api/infra-billing/history/{uuid}` |
| 4 | 🟢 GET | `InfraBillingController_getBillingNodes` | `/api/infra-billing/nodes` |
| 5 | 🟡 PATCH | `InfraBillingController_updateInfraBillingNode` | `/api/infra-billing/nodes` |
| 6 | 🔵 POST | `InfraBillingController_createInfraBillingNode` | `/api/infra-billing/nodes` |
| 7 | 🔴 DELETE | `InfraBillingController_deleteInfraBillingNodeByUuid` | `/api/infra-billing/nodes/{uuid}` |
| 8 | 🟢 GET | `InfraBillingController_getInfraProviders` | `/api/infra-billing/providers` |
| 9 | 🟡 PATCH | `InfraBillingController_updateInfraProvider` | `/api/infra-billing/providers` |
| 10 | 🔵 POST | `InfraBillingController_createInfraProvider` | `/api/infra-billing/providers` |
| 11 | 🔴 DELETE | `InfraBillingController_deleteInfraProviderByUuid` | `/api/infra-billing/providers/{uuid}` |
| 12 | 🟢 GET | `InfraBillingController_getInfraProviderByUuid` | `/api/infra-billing/providers/{uuid}` |

---

## 10. Internal Squads Controller (8 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `InternalSquadController_getInternalSquads` | `/api/internal-squads` |
| 2 | 🟡 PATCH | `InternalSquadController_updateInternalSquad` | `/api/internal-squads` |
| 3 | 🔵 POST | `InternalSquadController_createInternalSquad` | `/api/internal-squads` |
| 4 | 🔴 DELETE | `InternalSquadController_deleteInternalSquad` | `/api/internal-squads/{uuid}` |
| 5 | 🟢 GET | `InternalSquadController_getInternalSquadByUuid` | `/api/internal-squads/{uuid}` |
| 6 | 🟢 GET | `InternalSquadController_getInternalSquadAccessibleNodes` | `/api/internal-squads/{uuid}/accessible-nodes` |
| 7 | 🔵 POST | `InternalSquadController_addUsersToInternalSquad` | `/api/internal-squads/{uuid}/bulk-actions/add-users` |
| 8 | 🔴 DELETE | `InternalSquadController_removeUsersFromInternalSquad` | `/api/internal-squads/{uuid}/bulk-actions/remove-users` |

---

## 11. Keygen Controller (1 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `KeygenController_generateKey` | `/api/keygen` |

---

## 12. Nodes Controller (10 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `NodesController_getAllNodes` | `/api/nodes` |
| 2 | 🟡 PATCH | `NodesController_updateNode` | `/api/nodes` |
| 3 | 🔵 POST | `NodesController_createNode` | `/api/nodes` |
| 4 | 🔵 POST | `NodesController_reorderNodes` | `/api/nodes/actions/reorder` |
| 5 | 🔵 POST | `NodesController_restartAllNodes` | `/api/nodes/actions/restart-all` |
| 6 | 🔴 DELETE | `NodesController_deleteNode` | `/api/nodes/{uuid}` |
| 7 | 🟢 GET | `NodesController_getOneNode` | `/api/nodes/{uuid}` |
| 8 | 🔵 POST | `NodesController_disableNode` | `/api/nodes/{uuid}/actions/disable` |
| 9 | 🔵 POST | `NodesController_enableNode` | `/api/nodes/{uuid}/actions/enable` |
| 10 | 🔵 POST | `NodesController_restartNode` | `/api/nodes/{uuid}/actions/restart` |

---

## 13. Passkeys Controller (4 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🔴 DELETE | `PasskeyController_deletePasskey` | `/api/passkeys` |
| 2 | 🟢 GET | `PasskeyController_getActivePasskeys` | `/api/passkeys` |
| 3 | 🟢 GET | `PasskeyController_passkeyRegistrationOptions` | `/api/passkeys/registration/options` |
| 4 | 🔵 POST | `PasskeyController_passkeyRegistrationVerify` | `/api/passkeys/registration/verify` |

---

## 14. Remnawave Settings Controller (2 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `RemnawaveSettingsController_getSettings` | `/api/remnawave-settings` |
| 2 | 🟡 PATCH | `RemnawaveSettingsController_updateSettings` | `/api/remnawave-settings` |

---

## 15. Snippets Controller (4 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🔴 DELETE | `SnippetsController_deleteSnippetByName` | `/api/snippets` |
| 2 | 🟢 GET | `SnippetsController_getSnippets` | `/api/snippets` |
| 3 | 🟡 PATCH | `SnippetsController_updateSnippet` | `/api/snippets` |
| 4 | 🔵 POST | `SnippetsController_createSnippet` | `/api/snippets` |

---

## 16. Subscription Request History Controller (2 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `UserSubscriptionRequestHistoryController_getSubscriptionRequestHistory` | `/api/subscription-request-history` |
| 2 | 🟢 GET | `UserSubscriptionRequestHistoryController_getSubscriptionRequestHistoryStats` | `/api/subscription-request-history/stats` |

---

## 17. Subscription Settings Controller (2 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `SubscriptionSettingsController_getSettings` | `/api/subscription-settings` |
| 2 | 🟡 PATCH | `SubscriptionSettingsController_updateSettings` | `/api/subscription-settings` |

---

## 18. Subscription Template Controller (5 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `SubscriptionTemplateController_getAllTemplates` | `/api/subscription-templates` |
| 2 | 🟡 PATCH | `SubscriptionTemplateController_updateTemplate` | `/api/subscription-templates` |
| 3 | 🔵 POST | `SubscriptionTemplateController_createTemplate` | `/api/subscription-templates` |
| 4 | 🔴 DELETE | `SubscriptionTemplateController_deleteTemplate` | `/api/subscription-templates/{uuid}` |
| 5 | 🟢 GET | `SubscriptionTemplateController_getTemplateByUuid` | `/api/subscription-templates/{uuid}` |

---

## 19. System Controller (8 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `SystemController_getRemnawaveHealth` | `/api/system/health` |
| 2 | 🟢 GET | `SystemController_getNodesMetrics` | `/api/system/nodes/metrics` |
| 3 | 🟢 GET | `SystemController_getStats` | `/api/system/stats` |
| 4 | 🟢 GET | `SystemController_getBandwidthStats` | `/api/system/stats/bandwidth` |
| 5 | 🟢 GET | `SystemController_getNodesStatistics` | `/api/system/stats/nodes` |
| 6 | 🔵 POST | `SystemController_debugSrrMatcher` | `/api/system/testers/srr-matcher` |
| 7 | 🔵 POST | `SystemController_encryptHappCryptoLink` | `/api/system/tools/happ/encrypt` |
| 8 | 🟢 GET | `SystemController_getX25519Keypairs` | `/api/system/tools/x25519/generate` |

---

## 20. Users Bulk Actions Controller (8 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🔵 POST | `UsersBulkActionsController_bulkAllResetUserTraffic` | `/api/users/bulk/all/reset-traffic` |
| 2 | 🔵 POST | `UsersBulkActionsController_bulkUpdateAllUsers` | `/api/users/bulk/all/update` |
| 3 | 🔵 POST | `UsersBulkActionsController_bulkDeleteUsers` | `/api/users/bulk/delete` |
| 4 | 🔵 POST | `UsersBulkActionsController_bulkDeleteUsersByStatus` | `/api/users/bulk/delete-by-status` |
| 5 | 🔵 POST | `UsersBulkActionsController_bulkResetUserTraffic` | `/api/users/bulk/reset-traffic` |
| 6 | 🔵 POST | `UsersBulkActionsController_bulkRevokeUsersSubscription` | `/api/users/bulk/revoke-subscription` |
| 7 | 🔵 POST | `UsersBulkActionsController_bulkUpdateUsers` | `/api/users/bulk/update` |
| 8 | 🔵 POST | `UsersBulkActionsController_bulkUpdateUsersInternalSquads` | `/api/users/bulk/update-squads` |

---

## 21. Users Controller (17 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `UsersController_getAllUsers` | `/api/users` |
| 2 | 🟡 PATCH | `UsersController_updateUser` | `/api/users` |
| 3 | 🔵 POST | `UsersController_createUser` | `/api/users` |
| 4 | 🟢 GET | `UsersController_getUsersByEmail` | `/api/users/by-email/{email}` |
| 5 | 🟢 GET | `UsersController_getUserByShortUuid` | `/api/users/by-short-uuid/{shortUuid}` |
| 6 | 🟢 GET | `UsersController_getUsersByTag` | `/api/users/by-tag/{tag}` |
| 7 | 🟢 GET | `UsersController_getUserByTelegramId` | `/api/users/by-telegram-id/{telegramId}` |
| 8 | 🟢 GET | `UsersController_getUserByUsername` | `/api/users/by-username/{username}` |
| 9 | 🟢 GET | `UsersController_getAllTags` | `/api/users/tags` |
| 10 | 🔴 DELETE | `UsersController_deleteUser` | `/api/users/{uuid}` |
| 11 | 🟢 GET | `UsersController_getUserByUuid` | `/api/users/{uuid}` |
| 12 | 🟢 GET | `UsersController_getUserAccessibleNodes` | `/api/users/{uuid}/accessible-nodes` |
| 13 | 🔵 POST | `UsersController_disableUser` | `/api/users/{uuid}/actions/disable` |
| 14 | 🔵 POST | `UsersController_enableUser` | `/api/users/{uuid}/actions/enable` |
| 15 | 🔵 POST | `UsersController_resetUserTraffic` | `/api/users/{uuid}/actions/reset-traffic` |
| 16 | 🔵 POST | `UsersController_revokeUserSubscription` | `/api/users/{uuid}/actions/revoke` |
| 17 | 🟢 GET | `UsersController_getUserSubscriptionRequestHistory` | `/api/users/{uuid}/subscription-request-history` |

---

## 22. Users Stats Controller (1 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `UsersStatsController_getUserUsageByRange` | `/api/users/stats/usage/{uuid}/range` |

---

## 23. [Protected] Subscriptions Controller (5 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `SubscriptionsController_getAllSubscriptions` | `/api/subscriptions` |
| 2 | 🟢 GET | `SubscriptionsController_getSubscriptionByShortUuidProtected` | `/api/subscriptions/by-short-uuid/{shortUuid}` |
| 3 | 🟢 GET | `SubscriptionsController_getRawSubscriptionByShortUuid` | `/api/subscriptions/by-short-uuid/{shortUuid}/raw` |
| 4 | 🟢 GET | `SubscriptionsController_getSubscriptionByUsername` | `/api/subscriptions/by-username/{username}` |
| 5 | 🟢 GET | `SubscriptionsController_getSubscriptionByUuid` | `/api/subscriptions/by-uuid/{uuid}` |

---

## 24. [Public] Subscription Controller (4 operations)

| # | Method | Operation ID | Path |
|----|--------|-------------|------|
| 1 | 🟢 GET | `SubscriptionController_getSubscriptionWithType` | `/api/sub/outline/{shortUuid}/{type}/{encodedTag}` |
| 2 | 🟢 GET | `SubscriptionController_getSubscription` | `/api/sub/{shortUuid}` |
| 3 | 🟢 GET | `SubscriptionController_getSubscriptionInfoByShortUuid` | `/api/sub/{shortUuid}/info` |
| 4 | 🟢 GET | `SubscriptionController_getSubscriptionByClientType` | `/api/sub/{shortUuid}/{clientType}` |

---

## Summary

✅ **24 Controllers** with complete operation coverage  
✅ **139 Total API Operations**  
✅ **100% Implementation** - Each operation mapped to Go method calls
