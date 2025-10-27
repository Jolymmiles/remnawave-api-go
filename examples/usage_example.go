package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"

	remapi "github.com/Jolymmiles/remnawave-api-go/api"
)

func main() {
	// Example: How to use the remnawave-api-go v2.2.2.1 client with ClientExt
	
	// 1. Create base HTTP client
	httpClient := &http.Client{
		Timeout: 30 * time.Second,
	}

	// 2. Create base API client
	baseClient, err := remapi.NewClient(
		"https://api.example.com",
		httpClient,
	)
	if err != nil {
		log.Fatalf("Failed to create base client: %v", err)
	}

	// 3. Wrap with ClientExt for organized sub-client access
	client := remapi.NewClientExt(baseClient)

	// Example: Use Users client (17 operations)
	exampleUsersOperations(client)

	// Example: Use Nodes client (10 operations)
	exampleNodesOperations(client)

	// Example: Use Subscriptions client (5 protected + 4 public)
	exampleSubscriptionOperations(client)

	// Example: Use Bulk Actions
	exampleBulkOperations(client)

	// Example: Use System operations
	exampleSystemOperations(client)
}

// Example: Users Client - 17 operations
func exampleUsersOperations(client *remapi.ClientExt) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	fmt.Println("\n=== Users Operations ===")

	// Get all users
	if allUsers, err := client.Users().GetAllUsers(ctx); err == nil {
		fmt.Printf("✓ GetAllUsers: %v\n", allUsers)
	} else {
		fmt.Printf("✗ GetAllUsers error: %v\n", err)
	}

	// Create a new user
	createReq := &remapi.CreateUserRequest{
		// Fill with actual data
	}
	if newUser, err := client.Users().CreateUser(ctx, createReq); err == nil {
		fmt.Printf("✓ CreateUser: %v\n", newUser)
	} else {
		fmt.Printf("✗ CreateUser error: %v\n", err)
	}

	// Get user by username
	usernameParams := remapi.UsersControllerGetUserByUsernameParams{
		Username: "john_doe",
	}
	if user, err := client.Users().GetUserByUsername(ctx, usernameParams); err == nil {
		fmt.Printf("✓ GetUserByUsername: %v\n", user)
	} else {
		fmt.Printf("✗ GetUserByUsername error: %v\n", err)
	}

	// Get all user tags
	if tags, err := client.Users().GetAllTags(ctx); err == nil {
		fmt.Printf("✓ GetAllTags: %v\n", tags)
	} else {
		fmt.Printf("✗ GetAllTags error: %v\n", err)
	}
}

// Example: Nodes Client - 10 operations
func exampleNodesOperations(client *remapi.ClientExt) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	fmt.Println("\n=== Nodes Operations ===")

	// Get all nodes
	if allNodes, err := client.Nodes().GetAllNodes(ctx); err == nil {
		fmt.Printf("✓ GetAllNodes: %v\n", allNodes)
	} else {
		fmt.Printf("✗ GetAllNodes error: %v\n", err)
	}

	// Create a new node
	createReq := &remapi.CreateNodeRequest{
		// Fill with actual data
	}
	if newNode, err := client.Nodes().CreateNode(ctx, createReq); err == nil {
		fmt.Printf("✓ CreateNode: %v\n", newNode)
	} else {
		fmt.Printf("✗ CreateNode error: %v\n", err)
	}

	// Restart all nodes
	restartReq := &remapi.RestartAllNodesRequest{}
	if result, err := client.Nodes().RestartAllNodes(ctx, restartReq); err == nil {
		fmt.Printf("✓ RestartAllNodes: %v\n", result)
	} else {
		fmt.Printf("✗ RestartAllNodes error: %v\n", err)
	}
}

// Example: Protected Subscriptions Client - 5 operations
func exampleSubscriptionOperations(client *remapi.ClientExt) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	fmt.Println("\n=== Subscription Operations ===")

	// Protected Subscriptions (5 operations)
	if subs, err := client.ProtectedSubscriptions().GetAllSubscriptions(ctx); err == nil {
		fmt.Printf("✓ GetAllSubscriptions: %v\n", subs)
	} else {
		fmt.Printf("✗ GetAllSubscriptions error: %v\n", err)
	}

	// Public Subscription (4 operations)
	shortUuidParams := remapi.SubscriptionControllerGetSubscriptionParams{
		ShortUuid: "abc123",
	}
	if sub, err := client.PublicSubscription().GetSubscription(ctx, shortUuidParams); err == nil {
		fmt.Printf("✓ GetSubscription (public): %v\n", sub)
	} else {
		fmt.Printf("✗ GetSubscription error: %v\n", err)
	}

	// Subscription Templates (5 operations)
	if templates, err := client.SubscriptionTemplate().GetAllTemplates(ctx); err == nil {
		fmt.Printf("✓ GetAllTemplates: %v\n", templates)
	} else {
		fmt.Printf("✗ GetAllTemplates error: %v\n", err)
	}
}

// Example: Bulk Actions - 16 operations total (8 Users + 5 Hosts + 3 more)
func exampleBulkOperations(client *remapi.ClientExt) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	fmt.Println("\n=== Bulk Operations ===")

	// Bulk delete users
	bulkReq := &remapi.BulkUuidsRequest{
		Uuids: []string{"uuid1", "uuid2", "uuid3"},
	}
	if result, err := client.UsersBulkActions().BulkDeleteUsers(ctx, bulkReq); err == nil {
		fmt.Printf("✓ BulkDeleteUsers: %v\n", result)
	} else {
		fmt.Printf("✗ BulkDeleteUsers error: %v\n", err)
	}

	// Bulk enable hosts
	if result, err := client.HostsBulkActions().EnableHosts(ctx, bulkReq); err == nil {
		fmt.Printf("✓ EnableHosts: %v\n", result)
	} else {
		fmt.Printf("✗ EnableHosts error: %v\n", err)
	}

	// Bulk update users
	updateReq := &remapi.BulkUpdateUsersRequest{
		// Fill with actual data
	}
	if result, err := client.UsersBulkActions().BulkUpdateUsers(ctx, updateReq); err == nil {
		fmt.Printf("✓ BulkUpdateUsers: %v\n", result)
	} else {
		fmt.Printf("✗ BulkUpdateUsers error: %v\n", err)
	}
}

// Example: System Operations - 8 operations
func exampleSystemOperations(client *remapi.ClientExt) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	fmt.Println("\n=== System Operations ===")

	// Get Remnawave health
	if health, err := client.System().GetRemnawaveHealth(ctx); err == nil {
		fmt.Printf("✓ GetRemnawaveHealth: %v\n", health)
	} else {
		fmt.Printf("✗ GetRemnawaveHealth error: %v\n", err)
	}

	// Get stats
	if stats, err := client.System().GetStats(ctx); err == nil {
		fmt.Printf("✓ GetStats: %v\n", stats)
	} else {
		fmt.Printf("✗ GetStats error: %v\n", err)
	}

	// Get bandwidth stats
	if bandwidthStats, err := client.System().GetBandwidthStats(ctx); err == nil {
		fmt.Printf("✓ GetBandwidthStats: %v\n", bandwidthStats)
	} else {
		fmt.Printf("✗ GetBandwidthStats error: %v\n", err)
	}

	// Get nodes metrics
	if metrics, err := client.System().GetNodesMetrics(ctx); err == nil {
		fmt.Printf("✓ GetNodesMetrics: %v\n", metrics)
	} else {
		fmt.Printf("✗ GetNodesMetrics error: %v\n", err)
	}
}

// Additional examples for other clients (19 more controllers available)
/*
// Auth operations (8 methods)
client.Auth().Login(ctx, loginReq)
client.Auth().Register(ctx, registerReq)
client.Auth().GetStatus(ctx)

// Config Profiles (7 methods)
client.ConfigProfiles().GetConfigProfiles(ctx)
client.ConfigProfiles().CreateConfigProfile(ctx, req)
client.ConfigProfiles().GetConfigProfileByUuid(ctx, params)

// External Squads (7 methods)
client.ExternalSquads().GetExternalSquads(ctx)
client.ExternalSquads().CreateExternalSquad(ctx, req)
client.ExternalSquads().AddUsersToExternalSquad(ctx, params)

// HWID User Devices (6 methods)
client.HwidUserDevices().GetAllUsers(ctx)
client.HwidUserDevices().CreateUserHwidDevice(ctx, req)
client.HwidUserDevices().GetUserHwidDevices(ctx, params)

// Infra Billing (12 methods)
client.InfraBilling().GetInfraProviders(ctx)
client.InfraBilling().CreateInfraProvider(ctx, req)
client.InfraBilling().GetBillingNodes(ctx)

// Internal Squads (8 methods)
client.InternalSquads().GetInternalSquads(ctx)
client.InternalSquads().CreateInternalSquad(ctx, req)
client.InternalSquads().AddUsersToInternalSquad(ctx, params)

// Passkeys (4 methods)
client.Passkeys().GetActivePasskeys(ctx)
client.Passkeys().PasskeyRegistrationOptions(ctx)

// Snippets (4 methods)
client.Snippets().GetSnippets(ctx)
client.Snippets().CreateSnippet(ctx, req)

// And 10 more controllers with various operations...
// Total: 24 controllers, 139 operations
*/
