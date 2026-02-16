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

	// Use PaginationHelper for iterating through pages
	pager := remapi.NewPaginationHelper(50) // 50 items per page

	for pager.HasMore {
		resp, err := client.Users().GetAllUsers(ctx,
			pager.Limit,  // size
			pager.Offset, // start
		)
		if err != nil {
			log.Fatal(err)
		}

		users, ok := resp.(*remapi.GetAllUsersResponse)
		if !ok {
			log.Fatal("unexpected response type")
		}

		for _, user := range users.Response.Users {
			fmt.Printf("User: %s (UUID: %s)\n", user.Username, user.UUID)
		}

		// Advance to next page
		pager.SetTotal(int(users.Response.Total))
		pager.NextPage()
	}

	fmt.Printf("Total users: %d\n", *pager.Total)
}
