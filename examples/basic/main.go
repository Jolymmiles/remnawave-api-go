package main

import (
	"context"
	"fmt"
	"log"
	"time"

	remapi "github.com/Jolymmiles/remnawave-api-go/v3/api"
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

	// Users are identified by their numeric ID in Remnawave 3.4.3.
	resp, err := client.Users().GetUserById(ctx, 123)
	if err != nil {
		log.Fatal(err)
	}
	if user, ok := resp.(*remapi.UserResponse); ok {
		fmt.Printf("User: %s (ID: %d)\n", user.Response.Username, user.Response.ID)
	}

	// List all nodes
	nodesResp, err := client.Nodes().GetNodes(ctx)
	if err != nil {
		log.Fatal(err)
	}
	if nodes, ok := nodesResp.(*remapi.NodesResponseResponse); ok {
		for _, node := range nodes.Response {
			fmt.Printf("Node: %s (%s) connected=%v\n", node.Name, node.Address, node.IsConnected)
		}
	}

	// Create a user
	createResp, err := client.Users().CreateUser(ctx, &remapi.CreateUserBody{
		Username: "john_doe",
		ExpireAt: time.Now().AddDate(1, 0, 0).UTC(),
	})
	if err != nil {
		log.Fatal(err)
	}
	if created, ok := createResp.(*remapi.UserResponse); ok {
		fmt.Printf("Created user: %s\n", created.Response.Username)
	}

	// Delete the created user by numeric ID
	if created, ok := createResp.(*remapi.UserResponse); ok {
		_, err = client.Users().DeleteUser(ctx, created.Response.ID)
	}
	if err != nil {
		log.Fatal(err)
	}
}
