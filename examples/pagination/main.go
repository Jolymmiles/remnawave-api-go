package main

import (
	"context"
	"fmt"
	"log"

	remapi "github.com/Jolymmiles/remnawave-api-go/v3/api"
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

	// Use PaginationHelper for iterating through pages
	pager := remapi.NewPaginationHelper(50) // 50 items per page

	for pager.HasMore {
		resp, err := client.Users().GetUsers(ctx, pager.Offset, pager.Limit)
		if err != nil {
			log.Fatal(err)
		}

		users, ok := resp.(*remapi.GetUsersResponse)
		if !ok {
			log.Fatal("unexpected response type")
		}

		for _, user := range users.Response.Users {
			fmt.Printf("User: %s (ID: %d)\n", user.Username, user.ID)
		}

		// Advance to next page
		pager.SetTotal(users.Response.Total)
		pager.NextPage()
	}

	fmt.Printf("Total users: %d\n", *pager.Total)
}
