package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"

	remapi "github.com/Jolymmiles/remnawave-api-go/api"
)

// Quick Start Example: Using remnawave-api-go v2.2.2.1
// This demonstrates the main use cases of the organized ClientExt

func main() {
	// Setup
	httpClient := &http.Client{Timeout: 30 * time.Second}
	baseClient, err := remapi.NewClient("https://api.remnawave.local", httpClient)
	if err != nil {
		log.Fatal(err)
	}

	// Wrap with organized sub-clients
	client := remapi.NewClientExt(baseClient)
	ctx := context.Background()

	// Example 1: Get all users
	fmt.Println("1. Get all users:")
	users, err := client.Users().GetAllUsers(ctx)
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
	} else {
		fmt.Printf("   Success: %v\n", users)
	}

	// Example 2: Get all nodes
	fmt.Println("\n2. Get all nodes:")
	nodes, err := client.Nodes().GetAllNodes(ctx)
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
	} else {
		fmt.Printf("   Success: %v\n", nodes)
	}

	// Example 3: System health check
	fmt.Println("\n3. System health check:")
	health, err := client.System().GetRemnawaveHealth(ctx)
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
	} else {
		fmt.Printf("   Success: %v\n", health)
	}

	// Example 4: Get all hosts
	fmt.Println("\n4. Get all hosts:")
	hosts, err := client.Hosts().GetAllHosts(ctx)
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
	} else {
		fmt.Printf("   Success: %v\n", hosts)
	}

	// Example 5: Authentication status
	fmt.Println("\n5. Check auth status:")
	status, err := client.Auth().GetStatus(ctx)
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
	} else {
		fmt.Printf("   Success: %v\n", status)
	}

	// Example 6: Get subscriptions
	fmt.Println("\n6. Get all subscriptions:")
	subs, err := client.ProtectedSubscriptions().GetAllSubscriptions(ctx)
	if err != nil {
		fmt.Printf("   Error: %v\n", err)
	} else {
		fmt.Printf("   Success: %v\n", subs)
	}
}

// Additional helper function examples
func getUsersByTag(client *remapi.ClientExt, ctx context.Context, tag string) error {
	params := remapi.UsersControllerGetUsersByTagParams{Tag: tag}
	users, err := client.Users().GetUsersByTag(ctx, params)
	if err != nil {
		return err
	}
	fmt.Printf("Users with tag '%s': %v\n", tag, users)
	return nil
}

func getNodeById(client *remapi.ClientExt, ctx context.Context, uuid string) error {
	params := remapi.NodesControllerGetOneNodeParams{Uuid: uuid}
	node, err := client.Nodes().GetOneNode(ctx, params)
	if err != nil {
		return err
	}
	fmt.Printf("Node %s: %v\n", uuid, node)
	return nil
}

func bulkDeleteUsers(client *remapi.ClientExt, ctx context.Context, userUuids []string) error {
	req := &remapi.BulkUuidsRequest{Uuids: userUuids}
	result, err := client.UsersBulkActions().BulkDeleteUsers(ctx, req)
	if err != nil {
		return err
	}
	fmt.Printf("Bulk delete result: %v\n", result)
	return nil
}

func getSystemStats(client *remapi.ClientExt, ctx context.Context) error {
	// Get multiple system statistics
	stats, err := client.System().GetStats(ctx)
	if err != nil {
		return err
	}

	bandwidth, err := client.System().GetBandwidthStats(ctx)
	if err != nil {
		return err
	}

	nodes, err := client.System().GetNodesStatistics(ctx)
	if err != nil {
		return err
	}

	fmt.Printf("System Stats: %v\n", stats)
	fmt.Printf("Bandwidth: %v\n", bandwidth)
	fmt.Printf("Nodes: %v\n", nodes)
	return nil
}
