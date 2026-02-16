// Package api provides a Go client for the Remnawave API.
//
// The client is generated from the OpenAPI 3.0 specification using ogen,
// providing zero-reflection JSON encoding/decoding and compile-time validation.
//
// # Quick Start
//
// Create a base client and wrap it with ClientExt for organized sub-client access:
//
//	baseClient, err := api.NewClient(
//	    "https://your-panel.example.com",
//	    api.StaticToken{Token: "YOUR_JWT_TOKEN"},
//	)
//	if err != nil {
//	    log.Fatal(err)
//	}
//	client := api.NewClientExt(baseClient)
//
// # Sub-Clients
//
// ClientExt provides organized access to API operations via controller methods:
//
//	client.Users()         // User management
//	client.Nodes()         // Node management
//	client.Hosts()         // Host management
//	client.Subscription()  // Subscription management
//	client.Auth()          // Authentication
//
// # Simplified Parameters
//
// Methods with simple parameters (UUID, string) accept them directly
// instead of requiring Params structs:
//
//	// Instead of: client.Users().GetUserByUuid(ctx, UsersGetUserByUuidParams{UUID: "..."})
//	user, err := client.Users().GetUserByUuid(ctx, "user-uuid-here")
//
// # Request Options
//
// All methods accept optional RequestOption arguments for per-request customization:
//
//	user, err := client.Users().GetUserByUuid(ctx, "uuid", api.WithHeader("X-Custom", "value"))
//
// # Error Handling
//
// API errors are returned as typed responses that can be checked with type switches:
//
//	resp, err := client.Users().GetUserByUuid(ctx, "invalid-uuid")
//	if err != nil {
//	    log.Fatal(err)
//	}
//	switch e := resp.(type) {
//	case *api.BadRequestError:
//	    fmt.Println("Bad request:", e.Message)
//	case *api.NotFoundError:
//	    fmt.Println("Not found")
//	case *api.UserResponse:
//	    fmt.Println("User:", e.Response.Username)
//	}
//
// # OpenTelemetry
//
// The client includes built-in OpenTelemetry instrumentation for tracing.
package api
