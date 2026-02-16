package main

import (
	"context"
	"fmt"
	"log"

	remapi "github.com/Jolymmiles/remnawave-api-go/v2/api"
)

func main() {
	ctx := context.Background()

	baseClient, err := remapi.NewClient(
		"https://your-panel.example.com",
		remapi.StaticToken{Token: "YOUR_JWT_TOKEN"},
	)
	if err != nil {
		log.Fatal(err)
	}
	client := remapi.NewClientExt(baseClient)

	// All API methods return a response interface that can be type-switched.
	// Available error types depend on the endpoint — check the generated
	// Res interface (e.g. UsersGetUserByUuidRes) for the full list.
	resp, err := client.Users().GetUserByUuid(ctx, "invalid-uuid")
	if err != nil {
		// Network or protocol error
		log.Fatal(err)
	}

	switch e := resp.(type) {
	case *remapi.UserResponse:
		fmt.Printf("User: %s\n", e.Response.Username)

	case *remapi.BadRequestError:
		// 400 — validation errors with detailed field info
		fmt.Printf("Bad request: %s\n", e.Message)
		for _, ve := range e.Errors {
			fmt.Printf("  Field %v: %s (%s)\n", ve.Path, ve.Message, ve.Code)
		}

	case *remapi.NotFoundError:
		// 404 — resource not found
		fmt.Println("User not found")

	case *remapi.InternalServerError:
		// 500 — server error
		fmt.Printf("Server error: %s\n", e.Message.Value)
	}
}
