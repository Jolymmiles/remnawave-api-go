// Code generated from consolidated swagger. DO NOT EDIT manually.

package api

import "context"

// ClientExt wraps the base Client with organized sub-client access.
type ClientExt struct {
	*Client
	apiTokens *ApiTokensClient
	auth *AuthClient
	configProfile *ConfigProfileClient
	externalSquad *ExternalSquadClient
	hosts *HostsClient
	hostsBulkActions *HostsBulkActionsClient
	hwidUserDevices *HwidUserDevicesClient
	infraBilling *InfraBillingClient
	internalSquad *InternalSquadClient
	keygen *KeygenClient
	nodes *NodesClient
	nodesUsageHistory *NodesUsageHistoryClient
	nodesUserUsageHistory *NodesUserUsageHistoryClient
	passkey *PasskeyClient
	remnawaveSettings *RemnawaveSettingsClient
	snippets *SnippetsClient
	subscription *SubscriptionClient
	subscriptionSettings *SubscriptionSettingsClient
	subscriptionTemplate *SubscriptionTemplateClient
	subscriptions *SubscriptionsClient
	system *SystemClient
	userSubscriptionRequestHistory *UserSubscriptionRequestHistoryClient
	users *UsersClient
	usersBulkActions *UsersBulkActionsClient
	usersStats *UsersStatsClient
}

// NewClientExt creates a new ClientExt wrapper.
func NewClientExt(client *Client) *ClientExt {
	return &ClientExt{
		Client: client,
		apiTokens: NewApiTokensClient(client),
		auth: NewAuthClient(client),
		configProfile: NewConfigProfileClient(client),
		externalSquad: NewExternalSquadClient(client),
		hosts: NewHostsClient(client),
		hostsBulkActions: NewHostsBulkActionsClient(client),
		hwidUserDevices: NewHwidUserDevicesClient(client),
		infraBilling: NewInfraBillingClient(client),
		internalSquad: NewInternalSquadClient(client),
		keygen: NewKeygenClient(client),
		nodes: NewNodesClient(client),
		nodesUsageHistory: NewNodesUsageHistoryClient(client),
		nodesUserUsageHistory: NewNodesUserUsageHistoryClient(client),
		passkey: NewPasskeyClient(client),
		remnawaveSettings: NewRemnawaveSettingsClient(client),
		snippets: NewSnippetsClient(client),
		subscription: NewSubscriptionClient(client),
		subscriptionSettings: NewSubscriptionSettingsClient(client),
		subscriptionTemplate: NewSubscriptionTemplateClient(client),
		subscriptions: NewSubscriptionsClient(client),
		system: NewSystemClient(client),
		userSubscriptionRequestHistory: NewUserSubscriptionRequestHistoryClient(client),
		users: NewUsersClient(client),
		usersBulkActions: NewUsersBulkActionsClient(client),
		usersStats: NewUsersStatsClient(client),
	}
}

// ApiTokens returns the ApiTokensClient.
func (ce *ClientExt) ApiTokens() *ApiTokensClient {
	return ce.apiTokens
}

// Auth returns the AuthClient.
func (ce *ClientExt) Auth() *AuthClient {
	return ce.auth
}

// ConfigProfile returns the ConfigProfileClient.
func (ce *ClientExt) ConfigProfile() *ConfigProfileClient {
	return ce.configProfile
}

// ExternalSquad returns the ExternalSquadClient.
func (ce *ClientExt) ExternalSquad() *ExternalSquadClient {
	return ce.externalSquad
}

// Hosts returns the HostsClient.
func (ce *ClientExt) Hosts() *HostsClient {
	return ce.hosts
}

// HostsBulkActions returns the HostsBulkActionsClient.
func (ce *ClientExt) HostsBulkActions() *HostsBulkActionsClient {
	return ce.hostsBulkActions
}

// HwidUserDevices returns the HwidUserDevicesClient.
func (ce *ClientExt) HwidUserDevices() *HwidUserDevicesClient {
	return ce.hwidUserDevices
}

// InfraBilling returns the InfraBillingClient.
func (ce *ClientExt) InfraBilling() *InfraBillingClient {
	return ce.infraBilling
}

// InternalSquad returns the InternalSquadClient.
func (ce *ClientExt) InternalSquad() *InternalSquadClient {
	return ce.internalSquad
}

// Keygen returns the KeygenClient.
func (ce *ClientExt) Keygen() *KeygenClient {
	return ce.keygen
}

// Nodes returns the NodesClient.
func (ce *ClientExt) Nodes() *NodesClient {
	return ce.nodes
}

// NodesUsageHistory returns the NodesUsageHistoryClient.
func (ce *ClientExt) NodesUsageHistory() *NodesUsageHistoryClient {
	return ce.nodesUsageHistory
}

// NodesUserUsageHistory returns the NodesUserUsageHistoryClient.
func (ce *ClientExt) NodesUserUsageHistory() *NodesUserUsageHistoryClient {
	return ce.nodesUserUsageHistory
}

// Passkey returns the PasskeyClient.
func (ce *ClientExt) Passkey() *PasskeyClient {
	return ce.passkey
}

// RemnawaveSettings returns the RemnawaveSettingsClient.
func (ce *ClientExt) RemnawaveSettings() *RemnawaveSettingsClient {
	return ce.remnawaveSettings
}

// Snippets returns the SnippetsClient.
func (ce *ClientExt) Snippets() *SnippetsClient {
	return ce.snippets
}

// Subscription returns the SubscriptionClient.
func (ce *ClientExt) Subscription() *SubscriptionClient {
	return ce.subscription
}

// SubscriptionSettings returns the SubscriptionSettingsClient.
func (ce *ClientExt) SubscriptionSettings() *SubscriptionSettingsClient {
	return ce.subscriptionSettings
}

// SubscriptionTemplate returns the SubscriptionTemplateClient.
func (ce *ClientExt) SubscriptionTemplate() *SubscriptionTemplateClient {
	return ce.subscriptionTemplate
}

// Subscriptions returns the SubscriptionsClient.
func (ce *ClientExt) Subscriptions() *SubscriptionsClient {
	return ce.subscriptions
}

// System returns the SystemClient.
func (ce *ClientExt) System() *SystemClient {
	return ce.system
}

// UserSubscriptionRequestHistory returns the UserSubscriptionRequestHistoryClient.
func (ce *ClientExt) UserSubscriptionRequestHistory() *UserSubscriptionRequestHistoryClient {
	return ce.userSubscriptionRequestHistory
}

// Users returns the UsersClient.
func (ce *ClientExt) Users() *UsersClient {
	return ce.users
}

// UsersBulkActions returns the UsersBulkActionsClient.
func (ce *ClientExt) UsersBulkActions() *UsersBulkActionsClient {
	return ce.usersBulkActions
}

// UsersStats returns the UsersStatsClient.
func (ce *ClientExt) UsersStats() *UsersStatsClient {
	return ce.usersStats
}

// ApiTokensClient provides ApiTokens operations.
type ApiTokensClient struct {
	client *Client
}

// NewApiTokensClient creates a new ApiTokensClient.
func NewApiTokensClient(client *Client) *ApiTokensClient {
	return &ApiTokensClient{client: client}
}

// Create calls ApiTokensController_create.
func (sc *ApiTokensClient) Create(ctx context.Context, request *CreateApiTokenRequestDto) (ApiTokensControllerCreateRes, error) {
	return sc.client.ApiTokensControllerCreate(ctx, request)
}

// Delete calls ApiTokensController_delete.
func (sc *ApiTokensClient) Delete(ctx context.Context, params ApiTokensControllerDeleteParams) (ApiTokensControllerDeleteRes, error) {
	return sc.client.ApiTokensControllerDelete(ctx, params)
}

// AuthClient provides Auth operations.
type AuthClient struct {
	client *Client
}

// NewAuthClient creates a new AuthClient.
func NewAuthClient(client *Client) *AuthClient {
	return &AuthClient{client: client}
}

// Login calls AuthController_login.
func (sc *AuthClient) Login(ctx context.Context, request *LoginRequestDto) (AuthControllerLoginRes, error) {
	return sc.client.AuthControllerLogin(ctx, request)
}

// Register calls AuthController_register.
func (sc *AuthClient) Register(ctx context.Context, request *RegisterRequestDto) (AuthControllerRegisterRes, error) {
	return sc.client.AuthControllerRegister(ctx, request)
}

// ConfigProfileClient provides ConfigProfile operations.
type ConfigProfileClient struct {
	client *Client
}

// NewConfigProfileClient creates a new ConfigProfileClient.
func NewConfigProfileClient(client *Client) *ConfigProfileClient {
	return &ConfigProfileClient{client: client}
}

// ExternalSquadClient provides ExternalSquad operations.
type ExternalSquadClient struct {
	client *Client
}

// NewExternalSquadClient creates a new ExternalSquadClient.
func NewExternalSquadClient(client *Client) *ExternalSquadClient {
	return &ExternalSquadClient{client: client}
}

// HostsClient provides Hosts operations.
type HostsClient struct {
	client *Client
}

// NewHostsClient creates a new HostsClient.
func NewHostsClient(client *Client) *HostsClient {
	return &HostsClient{client: client}
}

// HostsBulkActionsClient provides HostsBulkActions operations.
type HostsBulkActionsClient struct {
	client *Client
}

// NewHostsBulkActionsClient creates a new HostsBulkActionsClient.
func NewHostsBulkActionsClient(client *Client) *HostsBulkActionsClient {
	return &HostsBulkActionsClient{client: client}
}

// HwidUserDevicesClient provides HwidUserDevices operations.
type HwidUserDevicesClient struct {
	client *Client
}

// NewHwidUserDevicesClient creates a new HwidUserDevicesClient.
func NewHwidUserDevicesClient(client *Client) *HwidUserDevicesClient {
	return &HwidUserDevicesClient{client: client}
}

// InfraBillingClient provides InfraBilling operations.
type InfraBillingClient struct {
	client *Client
}

// NewInfraBillingClient creates a new InfraBillingClient.
func NewInfraBillingClient(client *Client) *InfraBillingClient {
	return &InfraBillingClient{client: client}
}

// InternalSquadClient provides InternalSquad operations.
type InternalSquadClient struct {
	client *Client
}

// NewInternalSquadClient creates a new InternalSquadClient.
func NewInternalSquadClient(client *Client) *InternalSquadClient {
	return &InternalSquadClient{client: client}
}

// KeygenClient provides Keygen operations.
type KeygenClient struct {
	client *Client
}

// NewKeygenClient creates a new KeygenClient.
func NewKeygenClient(client *Client) *KeygenClient {
	return &KeygenClient{client: client}
}

// NodesClient provides Nodes operations.
type NodesClient struct {
	client *Client
}

// NewNodesClient creates a new NodesClient.
func NewNodesClient(client *Client) *NodesClient {
	return &NodesClient{client: client}
}

// NodesUsageHistoryClient provides NodesUsageHistory operations.
type NodesUsageHistoryClient struct {
	client *Client
}

// NewNodesUsageHistoryClient creates a new NodesUsageHistoryClient.
func NewNodesUsageHistoryClient(client *Client) *NodesUsageHistoryClient {
	return &NodesUsageHistoryClient{client: client}
}

// NodesUserUsageHistoryClient provides NodesUserUsageHistory operations.
type NodesUserUsageHistoryClient struct {
	client *Client
}

// NewNodesUserUsageHistoryClient creates a new NodesUserUsageHistoryClient.
func NewNodesUserUsageHistoryClient(client *Client) *NodesUserUsageHistoryClient {
	return &NodesUserUsageHistoryClient{client: client}
}

// PasskeyClient provides Passkey operations.
type PasskeyClient struct {
	client *Client
}

// NewPasskeyClient creates a new PasskeyClient.
func NewPasskeyClient(client *Client) *PasskeyClient {
	return &PasskeyClient{client: client}
}

// RemnawaveSettingsClient provides RemnawaveSettings operations.
type RemnawaveSettingsClient struct {
	client *Client
}

// NewRemnawaveSettingsClient creates a new RemnawaveSettingsClient.
func NewRemnawaveSettingsClient(client *Client) *RemnawaveSettingsClient {
	return &RemnawaveSettingsClient{client: client}
}

// SnippetsClient provides Snippets operations.
type SnippetsClient struct {
	client *Client
}

// NewSnippetsClient creates a new SnippetsClient.
func NewSnippetsClient(client *Client) *SnippetsClient {
	return &SnippetsClient{client: client}
}

// SubscriptionClient provides Subscription operations.
type SubscriptionClient struct {
	client *Client
}

// NewSubscriptionClient creates a new SubscriptionClient.
func NewSubscriptionClient(client *Client) *SubscriptionClient {
	return &SubscriptionClient{client: client}
}

// SubscriptionSettingsClient provides SubscriptionSettings operations.
type SubscriptionSettingsClient struct {
	client *Client
}

// NewSubscriptionSettingsClient creates a new SubscriptionSettingsClient.
func NewSubscriptionSettingsClient(client *Client) *SubscriptionSettingsClient {
	return &SubscriptionSettingsClient{client: client}
}

// SubscriptionTemplateClient provides SubscriptionTemplate operations.
type SubscriptionTemplateClient struct {
	client *Client
}

// NewSubscriptionTemplateClient creates a new SubscriptionTemplateClient.
func NewSubscriptionTemplateClient(client *Client) *SubscriptionTemplateClient {
	return &SubscriptionTemplateClient{client: client}
}

// SubscriptionsClient provides Subscriptions operations.
type SubscriptionsClient struct {
	client *Client
}

// NewSubscriptionsClient creates a new SubscriptionsClient.
func NewSubscriptionsClient(client *Client) *SubscriptionsClient {
	return &SubscriptionsClient{client: client}
}

// SystemClient provides System operations.
type SystemClient struct {
	client *Client
}

// NewSystemClient creates a new SystemClient.
func NewSystemClient(client *Client) *SystemClient {
	return &SystemClient{client: client}
}

// UserSubscriptionRequestHistoryClient provides UserSubscriptionRequestHistory operations.
type UserSubscriptionRequestHistoryClient struct {
	client *Client
}

// NewUserSubscriptionRequestHistoryClient creates a new UserSubscriptionRequestHistoryClient.
func NewUserSubscriptionRequestHistoryClient(client *Client) *UserSubscriptionRequestHistoryClient {
	return &UserSubscriptionRequestHistoryClient{client: client}
}

// UsersClient provides Users operations.
type UsersClient struct {
	client *Client
}

// NewUsersClient creates a new UsersClient.
func NewUsersClient(client *Client) *UsersClient {
	return &UsersClient{client: client}
}

// UsersBulkActionsClient provides UsersBulkActions operations.
type UsersBulkActionsClient struct {
	client *Client
}

// NewUsersBulkActionsClient creates a new UsersBulkActionsClient.
func NewUsersBulkActionsClient(client *Client) *UsersBulkActionsClient {
	return &UsersBulkActionsClient{client: client}
}

// UsersStatsClient provides UsersStats operations.
type UsersStatsClient struct {
	client *Client
}

// NewUsersStatsClient creates a new UsersStatsClient.
func NewUsersStatsClient(client *Client) *UsersStatsClient {
	return &UsersStatsClient{client: client}
}

