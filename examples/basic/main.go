package main

import (
	"context"
	"fmt"
	"log"

	remapi "github.com/Jolymmiles/remnawave-api-go/v2/api"
)

func main() {
	ctx := context.Background()

	// Create base client with your panel URL and JWT token
	baseClient, err := remapi.NewClient(
		"https://your-panel.example.com",
		remapi.StaticToken{Token: "YOUR_JWT_TOKEN"},
	)
	if err != nil {
		log.Fatal(err)
	}

	// Wrap with organized sub-clients
	client := remapi.NewClientExt(baseClient)

	// Get user by UUID - simplified parameter (just a string)
	resp, err := client.Users().GetUserByUuid(ctx, "550e8400-e29b-41d4-a716-446655440000")
	if err != nil {
		log.Fatal(err)
	}
	if user, ok := resp.(*remapi.UserResponse); ok {
		fmt.Printf("User: %s (UUID: %s)\n", user.Response.Username, user.Response.UUID)
	}

	// List all nodes
	nodesResp, err := client.Nodes().GetAllNodes(ctx)
	if err != nil {
		log.Fatal(err)
	}
	if nodes, ok := nodesResp.(*remapi.NodesResponse); ok {
		for _, node := range nodes.Response {
			fmt.Printf("Node: %s (%s) connected=%v\n", node.Name, node.Address, node.IsConnected)
		}
	}

	// Create a user
	createResp, err := client.Users().CreateUser(ctx, &remapi.CreateUserRequest{
		Username: "john_doe",
	})
	if err != nil {
		log.Fatal(err)
	}
	if created, ok := createResp.(*remapi.UserResponse); ok {
		fmt.Printf("Created user: %s\n", created.Response.Username)
	}

	// Delete a user
	_, err = client.Users().DeleteUser(ctx, "550e8400-e29b-41d4-a716-446655440000")
	if err != nil {
		log.Fatal(err)
	}
}
