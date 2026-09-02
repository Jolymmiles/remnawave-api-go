# Remnawave GO SDK

[![Stars](https://img.shields.io/github/stars/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/stargazers)
[![Forks](https://img.shields.io/github/forks/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/network/members)
[![Issues](https://img.shields.io/github/issues/Jolymmiles/remnawave-api-go.svg)](https://github.com/Jolymmiles/remnawave-api-go/issues)

A Go SDK client for interacting with the **[Remnawave API](https://remna.st)**.

## Version Compatibility

| API Version | SDK Version | Install |
|-------------|-------------|---------|
| 3.4.3 | v3.4.3 | `go get github.com/Jolymmiles/remnawave-api-go/v3@v3.4.3` |
| 2.8.0 | v2.8.0 | `go get github.com/Jolymmiles/remnawave-api-go/v2@v2.8.0` |
| 2.6.1 | v2.6.1 | `go get github.com/Jolymmiles/remnawave-api-go/v2@v2.6.1` |
| 2.5.3 | v2.5.3 | `go get github.com/Jolymmiles/remnawave-api-go/v2@v2.5.3` |
| 2.3.0 | v2.3.0-6 | `go get github.com/Jolymmiles/remnawave-api-go/v2@v2.3.0-6` |
| 2.2.6 | v2.2.6-1 | `go get github.com/Jolymmiles/remnawave-api-go/v2@v2.2.6-1` |

Generated with [**ogen**](https://github.com/ogen-go/ogen) v1.24.0:
* Zero-reflection JSON decoder for high throughput
* Compile-time validation against OpenAPI 3.0 spec
* First-class `context.Context` support
* Built-in OpenTelemetry instrumentation
* Per-request options via `RequestOption`
* Request/response editors (middleware)
* Organized sub-clients for clean API access
* Simplified method signatures for common operations, without verbose `Params` structs

## Installation

```bash
go get github.com/Jolymmiles/remnawave-api-go/v3@v3.4.3
```

## What's new in v3.4.3

The SDK is generated from the official Remnawave 3.4.3 OpenAPI document. It
includes 217 operations across 32 controllers, including resource tags, node
integrations, shared lists, plugin/snippet sync, geocheck, and the raw
subscription endpoint.

The Go generation pipeline maps integral API values to `int` and RFC3339
fields to `time.Time`/`OptDateTime`, avoiding `float64` and plain strings for
values that have stronger semantics in Go.

## v3 migration notes

This is a major API release and is not wire-compatible with v2:

- User resource identifiers are numeric `id` values. UUIDs were removed from
  user paths and request bodies; `shortUuid` remains a separate subscription
  identifier.
- The old user lookup endpoints by Telegram ID, email, tag, and ID were
  removed. Use `Users().GetUsersStream()` with cursor pagination and filters
  (`telegramId`, `email`, `tag`, `status`, `trafficLimitStrategy`, and
  `externalSquadUuid`). Pass `nextCursor` from the response as `cursor` on the
  next request; `size` is limited to 1000 and defaults to 250.
- `Users().ExtendUserExpirationDate()` is available for the new
  `POST /api/users/{userId}/actions/extend` operation with `{days: N}`.
- `/api/ip-control` was renamed to `/api/connections`. Existing token scopes
  migrate automatically; integrations that create tokens should use the new
  `connections:*` scopes.
- Delete and bulk operations now return empty `204` or asynchronous `202`
  responses. They no longer return `affectedRows`; handle the generated
  `NoContent` and `Accepted` response variants.
- Key generation returns `response.secretKey` instead of `response.pubKey`.
  Subscription settings use custom response headers, and external squads split
  headers into `responseHeadersAdd` and `responseHeadersRemove`.
- New v3 operations include digest and HTTP statistics, node and internal
  squad usage statistics, geocheck, node integrations, shared lists, tags,
  plugin/snippet synchronization, and raw subscriptions by `shortUuid`.
- Error responses are typed in OpenAPI (`400`, `404`, and `500` where
  applicable). Handle these response variants explicitly, in addition to
  transport errors.

The v3 release also changes panel configuration outside the SDK: migrate
`JWT_AUTH_SECRET` to `APP_SECRET`, remove the deprecated docs-related and JWT
token-secret variables, and review the new fixed documentation paths. Redis
Streams exports (`ioraw:export:user_usage`,
`ioraw:export:subscription_requests`, and
`ioraw:export:node_connections`) and additional webhook URLs are
backend/deployment concerns. The SDK exposes typed stream payload models, but
enabling or consuming the streams is not a REST client operation.

## Quick Start

```go
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

	baseClient, err := remapi.NewClient(
		"https://your-panel.example.com",
		remapi.StaticToken{Token: "YOUR_JWT_TOKEN"},
	)
	if err != nil {
		log.Fatal(err)
	}

	client := remapi.NewClientExt(baseClient)

	// User IDs are numeric in Remnawave 3.4.3.
	user, err := client.Users().GetUserById(ctx, 123)
	if err != nil {
		log.Fatal(err)
	}
	if response, ok := user.(*remapi.UserResponse); ok {
		fmt.Printf("User: %s (ID: %d)\n", response.Response.Username, response.Response.ID)
	}

	newUser, err := client.Users().CreateUser(ctx, &remapi.CreateUserBody{
		Username: "john_doe",
		ExpireAt: time.Now().AddDate(1, 0, 0).UTC(),
	})
	if err != nil {
		log.Fatal(err)
	}
	if response, ok := newUser.(*remapi.UserResponse); ok {
		fmt.Printf("Created: %s (ID: %d)\n", response.Response.Username, response.Response.ID)
	}
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
| `client.Connections()` | Active connection management |
| `client.ExternalSquad()` | External squads |
| `client.Hosts()` | Host management |
| `client.HostsBulkActions()` | Bulk host operations |
| `client.HwidUserDevices()` | HWID devices |
| `client.InfraBilling()` | Infrastructure billing |
| `client.InternalSquad()` | Internal squads |
| `client.InternalSquadStats()` | Internal squad statistics |
| `client.Keygen()` | Key generation |
| `client.Metadata()` | User and node metadata |
| `client.NodeIntegration()` | Node integrations |
| `client.NodePlugin()` | Node plugin management |
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
| `client.TorrentBlockerReports()` | Torrent blocker reports |
| `client.UserSubscriptionRequestHistory()` | Request history |
| `client.Users()` | User management |
| `client.UsersBulkActions()` | Bulk user operations |

## Error Handling

Unified error types for consistent error handling:

```go
resp, err := client.Users().GetUserById(ctx, 999999)
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
| `BadRequestError` | 400 | Business errors or validation errors with optional `[]ValidationError` |
| `UnauthorizedError` | 401 | Authentication required |
| `ForbiddenError` | 403 | Access denied |
| `NotFoundError` | 404 | Resource not found |
| `InternalServerError` | 500 | Server error |

### ValidationError Structure

```go
type ValidationError struct {
    Validation string   // e.g., "number"
    Code       string   // e.g., "invalid_string"
    Message    string   // e.g., "Invalid uuid"
    Path       []string // e.g., ["uuid"]
}
```

## Common Operations

### Users

```go
// Get by numeric ID
user, _ := client.Users().GetUserById(ctx, 123)

// List with simple offset pagination.
users, _ := client.Users().GetUsers(ctx, 0, 50)

// Use WithParams only for optional JSON filters and sorting.
users, _ = client.Users().GetUsersWithParams(ctx, remapi.UsersGetUsersParams{
    Start: remapi.NewOptInt(0),
    Size: remapi.NewOptInt(50),
    Filters: remapi.NewOptString(`[{"id":"username","value":"john"}]`),
})

// Get by username
user, _ := client.Users().GetUserByUsername(ctx, "john")

// Get by short UUID
user, _ := client.Users().GetUserByShortUuid(ctx, "short-uuid")

// Cursor-paginated stream with server-side filters.
stream, _ := client.Users().GetUsersStream(ctx, remapi.UsersGetUsersStreamParams{
    Size:  remapi.NewOptInt(250),
    Email: remapi.NewOptString("john@example.com"),
})
_ = stream

// Create. ExpireAt is required.
user, _ := client.Users().CreateUser(ctx, &remapi.CreateUserBody{
    Username: "new_user",
    ExpireAt: time.Now().AddDate(1, 0, 0).UTC(),
})

// Update
user, _ := client.Users().UpdateUser(ctx, &remapi.UpdateUserBody{
    ID: remapi.NewOptInt(123),
    Username: remapi.NewOptString("new_user"),
})

// Delete
client.Users().DeleteUser(ctx, 123)

// Enable/Disable
client.Users().EnableUser(ctx, 123)
client.Users().DisableUser(ctx, 123)

// Reset traffic
client.Users().ResetUserTraffic(ctx, 123)
```

### Nodes

```go
// List all
nodes, _ := client.Nodes().GetNodes(ctx)

// Get one
node, _ := client.Nodes().GetNode(ctx, "uuid-here")

// Create
node, err := client.Nodes().CreateNode(ctx, &remapi.CreateNodeBody{
    Name:    "Node-1",
    Address: "203.0.113.10",
    ConfigProfile: remapi.ConfigProfile2{
        ActiveConfigProfileUuid: uuid.MustParse("00000000-0000-4000-8000-000000000001"),
        ActiveInbounds: []uuid.UUID{
            uuid.MustParse("00000000-0000-4000-8000-000000000002"),
        },
    },
})

// Delete
client.Nodes().DeleteNode(ctx, "uuid-here")

// Enable/Disable
client.Nodes().EnableNode(ctx, "uuid-here")
client.Nodes().DisableNode(ctx, "uuid-here")

// Restart
client.Nodes().RestartNode(ctx, &remapi.NodeBodyRequest{
    ForceRestart: false,
}, "uuid-here")

// Reset traffic
client.Nodes().ResetNodeTraffic(ctx, "uuid-here")
```

### Hosts

```go
// List all
hosts, _ := client.Hosts().GetHosts(ctx)

// Get one
host, _ := client.Hosts().GetOneHost(ctx, "uuid-here")

// Create
host, err := client.Hosts().CreateHost(ctx, &remapi.CreateHostBody{
    Inbound: remapi.Inbound2{
        ConfigProfileUuid: uuid.MustParse("00000000-0000-4000-8000-000000000001"),
        ConfigProfileInboundUuid: uuid.MustParse("00000000-0000-4000-8000-000000000002"),
    },
    Remark:  "Edge TLS",
    Address: "edge.example.com",
    Port:    443,
})

// Delete
client.Hosts().DeleteHost(ctx, "uuid-here")
```

### Authentication

```go
// Login
resp, _ := client.Auth().Login(ctx, &remapi.LoginBody{
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
user, err := client.Users().GetUserById(ctx, 123, opts...)
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

## Regenerating the SDK

The committed generated code is reproducible from the official 3.4.3 document:

```bash
python3 scripts/pipeline.py specs/3.4.3.json
```

The pipeline validates the v3.4.3 contract, normalizes the document for ogen,
generates the SDK and verifies that every OpenAPI operation has a Go wrapper.

## Requirements

| Requirement | Version |
|-------------|---------|
| Go | 1.26+ |
| Remnawave API | 3.4.3 |

## License

[MIT](LICENSE.MD)

## Donation

- **BEP20 USDT:** `0x4D1ee2445fdC88fA49B9d02FB8ee3633f45Bef48`
- **SOL:** `HNQhe6SCoU5UDZicFKMbYjQNv9Muh39WaEWbZayQ9Nn8`
- **TRC20 USDT:** `TBJrguLia8tvydsQ2CotUDTYtCiLDA4nPW`
- **TON USDT:** `UQAdAhVxOr9LS07DDQh0vNzX2575Eu0eOByjImY1yheatXgr`
