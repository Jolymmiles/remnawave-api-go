# Remnawave GO SDK

[![Stars](https://img.shields.io/github/stars/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/stargazers)
[![Forks](https://img.shields.io/github/forks/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/network/members)
[![Issues](https://img.shields.io/github/issues/Jolymmiles/remnawave-api-go.svg)](https://github.com/Jolymmiles/remnawave-api-go/issues)

A Go SDK client for interacting with the **[Remnawave API](https://remna.st)**.

## Version Compatibility

| API Version | SDK Version | Install |
|-------------|-------------|---------|
| 2.6.1 | v2.6.1 | `go get github.com/Jolymmiles/remnawave-api-go/v2@v2.6.1` |
| 2.5.3 | v2.5.3 | `go get github.com/Jolymmiles/remnawave-api-go/v2@v2.5.3` |
| 2.3.0 | v2.3.0-6 | `go get github.com/Jolymmiles/remnawave-api-go/v2@v2.3.0-6` |
| 2.2.6 | v2.2.6-1 | `go get github.com/Jolymmiles/remnawave-api-go/v2@v2.2.6-1` |

Generated with [**ogen**](https://github.com/ogen-go/ogen) v1.19.0:
* Zero-reflection JSON decoder for high throughput
* Compile-time validation against OpenAPI 3.0 spec
* First-class `context.Context` support
* Built-in OpenTelemetry instrumentation
* Per-request options via `RequestOption`
* Request/response editors (middleware)
* Organized sub-clients for clean API access
* Simplified method signatures (no verbose Params structs)

## Installation

```bash
go get github.com/Jolymmiles/remnawave-api-go/v2@v2.6.1
```

## Quick Start

```go
package main

import (
    "context"
    "fmt"
    remapi "github.com/Jolymmiles/remnawave-api-go/v2/api"
)

func main() {
    ctx := context.Background()

    // Create base client
    baseClient, _ := remapi.NewClient(
        "https://your-panel.example.com",
        remapi.StaticToken{Token: "YOUR_JWT_TOKEN"},
    )

    // Wrap with organized sub-clients
    client := remapi.NewClientExt(baseClient)

    // Get user by UUID - simple string argument
    user, _ := client.Users().GetUserByUuid(ctx, "user-uuid-here")
    fmt.Printf("User: %s\n", user.(*remapi.UserResponse).Response.Username)

    // Get node by UUID
    node, _ := client.Nodes().GetOneNode(ctx, "node-uuid-here")
    fmt.Printf("Node: %s\n", node.(*remapi.NodeResponse).Response.Name)

    // Create user
    newUser, _ := client.Users().CreateUser(ctx, &remapi.CreateUserRequest{
        Username: "john_doe",
    })
    fmt.Printf("Created: %s\n", newUser.(*remapi.UserResponse).Response.Username)
}
```

## Available Controllers

| Controller | Description |
|------------|-------------|
| `client.ApiTokens()` | API token management |
| `client.Auth()` | Authentication |
| `client.BandwidthStatsNodes()` | Node bandwidth statistics |
| `client.BandwidthStatsUsers()` | User bandwidth statistics |
| `client.ConfigProfile()` | Config profiles |
| `client.ExternalSquad()` | External squads |
| `client.Hosts()` | Host management |
| `client.HostsBulkActions()` | Bulk host operations |
| `client.HwidUserDevices()` | HWID devices |
| `client.InfraBilling()` | Infrastructure billing |
| `client.InternalSquad()` | Internal squads |
| `client.Keygen()` | Key generation |
| `client.Nodes()` | Node management |
| `client.NodesUsageHistory()` | Node usage history |
| `client.Passkey()` | Passkey authentication |
| `client.RemnawaveSettings()` | Panel settings |
| `client.Snippets()` | Code snippets |
| `client.Subscription()` | Subscription management |
| `client.SubscriptionPageConfig()` | Subscription page config |
| `client.SubscriptionSettings()` | Subscription settings |
| `client.SubscriptionTemplate()` | Subscription templates |
| `client.Subscriptions()` | Multiple subscriptions |
| `client.System()` | System info |
| `client.UserSubscriptionRequestHistory()` | Request history |
| `client.Users()` | User management |
| `client.UsersBulkActions()` | Bulk user operations |

## Error Handling

Unified error types for consistent error handling:

```go
resp, err := client.Users().GetUserByUuid(ctx, "invalid-uuid")
if err != nil {
    panic(err)
}

switch e := resp.(type) {
case *remapi.UserResponse:
    fmt.Printf("User: %s\n", e.Response.Username)
case *remapi.BadRequestError:
    for _, validationErr := range e.Errors {
        fmt.Printf("Field: %v, Error: %s\n", validationErr.Path, validationErr.Message)
    }
case *remapi.NotFoundError:
    fmt.Println("User not found")
case *remapi.InternalServerError:
    fmt.Printf("Server error: %s\n", e.Message.Value)
}
```

### Error Types

| Type | Status | Description |
|------|--------|-------------|
| `BadRequestError` | 400 | Validation errors with `[]ValidationError` |
| `UnauthorizedError` | 401 | Authentication required |
| `ForbiddenError` | 403 | Access denied |
| `NotFoundError` | 404 | Resource not found |
| `InternalServerError` | 500 | Server error |

### ValidationError Structure

```go
type ValidationError struct {
    Validation string   // e.g., "uuid"
    Code       string   // e.g., "invalid_string"
    Message    string   // e.g., "Invalid uuid"
    Path       []string // e.g., ["uuid"]
}
```

## Common Operations

### Users

```go
// Get by UUID (simplified - just pass the string)
user, _ := client.Users().GetUserByUuid(ctx, "uuid-here")

// Get by username
user, _ := client.Users().GetUserByUsername(ctx, "john")

// Get by short UUID
user, _ := client.Users().GetUserByShortUuid(ctx, "short-uuid")

// Create
user, _ := client.Users().CreateUser(ctx, &remapi.CreateUserRequest{
    Username: "new_user",
})

// Update
user, _ := client.Users().UpdateUser(ctx, &remapi.UpdateUserRequest{
    Uuid: "uuid-here",
})

// Delete
client.Users().DeleteUser(ctx, "uuid-here")

// Enable/Disable
client.Users().EnableUser(ctx, "uuid-here")
client.Users().DisableUser(ctx, "uuid-here")

// Reset traffic
client.Users().ResetUserTraffic(ctx, "uuid-here")
```

### Nodes

```go
// List all
nodes, _ := client.Nodes().GetAllNodes(ctx)

// Get one (simplified)
node, _ := client.Nodes().GetOneNode(ctx, "uuid-here")

// Create
node, _ := client.Nodes().CreateNode(ctx, &remapi.CreateNodeRequest{
    Name: "Node-1",
})

// Delete
client.Nodes().DeleteNode(ctx, "uuid-here")

// Enable/Disable
client.Nodes().EnableNode(ctx, "uuid-here")
client.Nodes().DisableNode(ctx, "uuid-here")

// Restart
client.Nodes().RestartNode(ctx, "uuid-here")

// Reset traffic
client.Nodes().ResetNodeTraffic(ctx, "uuid-here")
```

### Hosts

```go
// List all
hosts, _ := client.Hosts().GetAllHosts(ctx)

// Get one
host, _ := client.Hosts().GetOneHost(ctx, "uuid-here")

// Create
host, _ := client.Hosts().CreateHost(ctx, &remapi.CreateHostRequest{...})

// Delete
client.Hosts().DeleteHost(ctx, "uuid-here")
```

### Authentication

```go
// Login
resp, _ := client.Auth().Login(ctx, &remapi.LoginRequest{
    Username: "admin",
    Password: "password",
})
token := resp.(*remapi.TokenResponse).Response.AccessToken

// Get status
status, _ := client.Auth().GetStatus(ctx)
```

## Request Options

All methods support per-request `RequestOption` for customization:

```go
// Pass options as the last variadic argument
user, err := client.Users().GetUserByUuid(ctx, "uuid-here", opts...)
```

## Access to Base Client

If you need direct access to the underlying ogen client:

```go
baseClient := client.Client()
```

## Examples

See the [`examples/`](examples/) directory for complete working examples:
- [`basic/`](examples/basic/) — CRUD operations
- [`pagination/`](examples/pagination/) — Paginated listing with PaginationHelper
- [`error_handling/`](examples/error_handling/) — Type-switch error handling

## Requirements

| Requirement | Version |
|-------------|---------|
| Go | 1.21+ |
| Remnawave API | 2.6.1+ |

## License

[MIT](LICENSE.MD)

## Donation

- **BEP20 USDT:** `0x4D1ee2445fdC88fA49B9d02FB8ee3633f45Bef48`
- **SOL:** `HNQhe6SCoU5UDZicFKMbYjQNv9Muh39WaEWbZayQ9Nn8`
- **TRC20 USDT:** `TBJrguLia8tvydsQ2CotUDTYtCiLDA4nPW`
- **TON USDT:** `UQAdAhVxOr9LS07DDQh0vNzX2575Eu0eOByjImY1yheatXgr`
