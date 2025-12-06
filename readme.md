# Remnawave GO SDK

[![Stars](https://img.shields.io/github/stars/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/stargazers)
[![Forks](https://img.shields.io/github/forks/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/network/members)
[![Issues](https://img.shields.io/github/issues/Jolymmiles/remnawave-api-go.svg)](https://github.com/Jolymmiles/remnawave-api-go/issues)

A Go SDK client for interacting with the **[Remnawave API](https://remna.st)**.

**Latest version:** `v2.3.0-5`  
**API version:** `v2.3.0`

Generated with [**ogen**](https://github.com/ogen-go/ogen):
* Zero-reflection JSON decoder for high throughput
* Compile-time validation against OpenAPI 3.0 spec
* First-class `context.Context` support
* Organized sub-clients for clean API access

## Installation

```bash
go get github.com/Jolymmiles/remnawave-api-go/v2@v2.3.0-5
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

    // Use controller methods
    users, _ := client.Users().GetAll(ctx, remapi.UsersControllerGetAllUsersParams{})
    fmt.Printf("Found %d users\n", len(users.Response.Users))

    // Create user
    user, _ := client.Users().Create(ctx, &remapi.CreateUserRequestDto{
        Username: "john_doe",
    })
    fmt.Printf("Created user: %s\n", user.Response.Username)

    // Get nodes
    nodes, _ := client.Nodes().GetAll(ctx)
    fmt.Printf("Found %d nodes\n", len(nodes.Response))
}
```

## Available Controllers

| Controller | Description |
|------------|-------------|
| `client.Users()` | User management |
| `client.UsersBulkActions()` | Bulk user operations |
| `client.UsersStats()` | User statistics |
| `client.Nodes()` | Node management |
| `client.Hosts()` | Host management |
| `client.HostsBulkActions()` | Bulk host operations |
| `client.Auth()` | Authentication |
| `client.Passkey()` | Passkey authentication |
| `client.Subscription()` | Subscription management |
| `client.Subscriptions()` | Multiple subscriptions |
| `client.SubscriptionSettings()` | Subscription settings |
| `client.SubscriptionTemplate()` | Templates |
| `client.ConfigProfile()` | Config profiles |
| `client.InternalSquad()` | Internal squads |
| `client.ExternalSquad()` | External squads |
| `client.Snippets()` | Code snippets |
| `client.System()` | System info |
| `client.ApiTokens()` | API tokens |
| `client.RemnawaveSettings()` | Panel settings |
| `client.HwidUserDevices()` | HWID devices |
| `client.InfraBilling()` | Infrastructure billing |
| `client.Keygen()` | Key generation |
| `client.NodesUsageHistory()` | Node usage history |
| `client.NodesUserUsageHistory()` | User usage on nodes |
| `client.UserSubscriptionRequestHistory()` | Request history |

## Error Handling

Unified error types for consistent error handling:

```go
resp, err := client.Users().GetByUuid(ctx, remapi.UsersControllerGetUserByUuidParams{
    Uuid: "invalid-uuid",
})

switch e := resp.(type) {
case *remapi.BadRequestError:
    // Validation errors
    for _, validationErr := range e.Errors {
        fmt.Printf("Field: %v, Error: %s\n", validationErr.Path, validationErr.Message)
    }
case *remapi.UnauthorizedError:
    fmt.Println("Invalid token")
case *remapi.NotFoundError:
    fmt.Println("User not found")
case *remapi.InternalServerError:
    fmt.Printf("Server error: %s\n", e.Message.Value)
case *remapi.UserResponse:
    fmt.Printf("User: %s\n", e.Response.Username)
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
// List all users
users, _ := client.Users().GetAll(ctx, remapi.UsersControllerGetAllUsersParams{})

// Get by UUID
user, _ := client.Users().GetByUuid(ctx, remapi.UsersControllerGetUserByUuidParams{Uuid: "..."})

// Get by username
user, _ := client.Users().GetByUsername(ctx, remapi.UsersControllerGetUserByUsernameParams{Username: "john"})

// Create
user, _ := client.Users().Create(ctx, &remapi.CreateUserRequestDto{Username: "new_user"})

// Update
user, _ := client.Users().Update(ctx, &remapi.UpdateUserRequestDto{Uuid: "...", Username: remapi.NewOptString("updated")})

// Delete
client.Users().Delete(ctx, remapi.UsersControllerDeleteUserParams{Uuid: "..."})

// Enable/Disable
client.Users().Enable(ctx, remapi.UsersControllerEnableUserParams{Uuid: "..."})
client.Users().Disable(ctx, remapi.UsersControllerDisableUserParams{Uuid: "..."})
```

### Nodes

```go
// List all
nodes, _ := client.Nodes().GetAll(ctx)

// Get one
node, _ := client.Nodes().GetOne(ctx, remapi.NodesControllerGetOneNodeParams{Uuid: "..."})

// Create
node, _ := client.Nodes().Create(ctx, &remapi.CreateNodeRequestDto{Name: "Node-1"})

// Restart
client.Nodes().Restart(ctx, remapi.NodesControllerRestartNodeParams{Uuid: "..."})

// Restart all
client.Nodes().RestartAll(ctx)
```

### Authentication

```go
// Login
resp, _ := client.Auth().Login(ctx, &remapi.LoginRequestDto{
    Username: "admin",
    Password: "password",
})
token := resp.Response.AccessToken

// Get status
status, _ := client.Auth().GetStatus(ctx)
```

## Access to Base Client

If you need direct access to the underlying ogen client:

```go
baseClient := client.Client()
// Use baseClient for advanced operations
```

## Requirements

| Requirement | Version |
|-------------|---------|
| Go | 1.21+ |
| Remnawave API | 2.3.0+ |

## License

[MIT](LICENSE.MD)

## Donation

- **BEP20 USDT:** `0x4D1ee2445fdC88fA49B9d02FB8ee3633f45Bef48`
- **SOL:** `HNQhe6SCoU5UDZicFKMbYjQNv9Muh39WaEWbZayQ9Nn8`
- **TRC20 USDT:** `TBJrguLia8tvydsQ2CotUDTYtCiLDA4nPW`
- **TON USDT:** `UQAdAhVxOr9LS07DDQh0vNzX2575Eu0eOByjImY1yheatXgr`
