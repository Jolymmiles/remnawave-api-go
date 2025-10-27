# Remnawave GO SDK


[![Stars](https://img.shields.io/github/stars/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/stargazers)
[![Forks](https://img.shields.io/github/forks/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/network/members)
[![Issues](https://img.shields.io/github/issues/Jolymmiles/remnawave-api-go.svg)](https://github.com/Jolymmiles/remnawave-api-go/issues)

A Go SDK client for interacting with the **[Remnawave API](https://remna.st)**.
Latest version: **v2.2.0.1** (with pagination parameter support)
Library checked with Remnawave **[v2.2.0](https://github.com/remnawave/panel/releases/tag/2.0.0)**

The client is generated with [**ogen**](https://github.com/ogen-go/ogen):

* zero-reflection JSON decoder for high throughput,
* compile-time validation against the OpenAPI 3.0 spec,
* first-class `context.Context` support,
* pluggable middleware (`http.RoundTripper`, retries, tracing, …),
* **organized sub-clients for better API organization** ✨

**TL;DR**

```bash
go get github.com/Jolymmiles/remnawave-api-go/v2@v2.2.0.1
```

### Quick Start (New Organized API)

```go
import (
	"context"
	"fmt"
	remapi "github.com/Jolymmiles/remnawave-api-go/api"
)

func main() {
	ctx := context.Background()

	baseClient, _ := remapi.NewClient(
		"https://example.com",
		remapi.StaticToken{Token: "JWT_TOKEN"},
	)

	// Use organized sub-clients
	client := remapi.NewClientExt(baseClient)

	// Get all nodes
	nodes, err := client.Nodes().GetAll(ctx)
	if err != nil {
		panic(err)
	}

	// Create user
	user, err := client.Users().Create(ctx, &remapi.CreateUserRequestDto{
		Username: "john",
		Email:    "john@example.com",
	})

	// Get user by ID
	userData, err := client.Users().GetByID(ctx, "user-uuid")

	// Authenticate
	loginResp, err := client.Auth().Login(ctx, &remapi.LoginRequestDto{
		Username: "admin",
		Password: "password",
	})

	fmt.Println(nodes, user, userData, loginResp)
}
```

### Classic API (Still Supported)

```go
// Old way still works (backward compatible)
resp, err := rclient.NodesControllerGetAllNodes(ctx, remapi.NodesControllerGetAllNodesParams{})
```

### Sub-Clients Available

- **`client.Users()`** - User management (17 operations)
  - `Create()`, `GetAll()`, `GetByID()`, `Update()`, `Delete()`, `Enable()`, `Disable()`, etc.

- **`client.Nodes()`** - Node management (10 operations)
  - `Create()`, `GetAll()`, `GetByID()`, `Update()`, `Restart()`, `RestartAll()`, `Enable()`, `Disable()`, etc.

- **`client.Hosts()`** - Host management (8 operations)
  - `Create()`, `GetAll()`, `GetByID()`, `Update()`, `Delete()`, `Reorder()`, etc.

- **`client.Auth()`** - Authentication (8 operations)
  - `Login()`, `Register()`, `GetStatus()`, `OAuth2Authorize()`, `PasskeyAuthenticationOptions()`, etc.

- **`client.System()`** - System operations (5 operations)
  - `GetHealth()`, `GetStats()`, `GetBandwidthStats()`, `GetNodesStatistics()`, `GetNodesMetrics()`

---

## Detailed Usage Examples

### Pagination Helpers

The SDK provides automatic pagination management for endpoints that support it:

```go
import (
	"context"
	"fmt"
	remapi "github.com/Jolymmiles/remnawave-api-go/v2/api"
)

ctx := context.Background()
client := remapi.NewClientExt(baseClient)

// Create pagination helper with page size
pager := remapi.NewPaginationHelper(50) // 50 items per page

// Iterate through pages
for {
	// Create params with pagination
	params := remapi.UsersControllerGetAllUsersParams{
		Start: remapi.NewOptFloat64(float64(pager.Offset)),
		Size:  remapi.NewOptFloat64(float64(pager.Limit)),
	}

	// Get users with pagination
	users, err := client.Users().GetAll(ctx, params)
	if err != nil {
		panic(err)
	}

	fmt.Printf("Page %d - Fetched %d users\n", pager.CurrentPage(), len(users.Response))
	
	// Process users...
	for _, user := range users.Response {
		fmt.Println(user.Username)
	}

	// If we got less than requested, it's the last page
	if len(users.Response) < pager.Limit {
		break
	}

	// Move to next page
	if !pager.NextPage() {
		break
	}
}

// Navigation methods
pager.FirstPage()      // Go to first page
pager.NextPage()       // Go to next page (returns true if moved, false if already last)
pager.PreviousPage()   // Go to previous page (returns true if moved, false if at first)
pager.CurrentPage()    // Get current page number (1-indexed)
pager.TotalPages()     // Get total pages (needs SetTotal() to be called first)
pager.CanGoNext()      // Check if there's a next page
pager.CanGoPrevious()  // Check if there's a previous page
pager.SetTotal(100)    // Set total items count to calculate total pages
```

**Alternative: Get all users without pagination**

```go
// Get all users at once (no pagination needed)
users, err := client.Users().GetAll(ctx, remapi.UsersControllerGetAllUsersParams{})
```

### User Operations

```go
// Get all users (with pagination support)
users, err := client.Users().GetAll(ctx, remapi.UsersControllerGetAllUsersParams{})

// Get all users (with custom pagination)
params := remapi.UsersControllerGetAllUsersParams{
	Start: remapi.NewOptFloat64(0),
	Size:  remapi.NewOptFloat64(50),
}
users, err := client.Users().GetAll(ctx, params)

// Create user
user, err := client.Users().Create(ctx, &remapi.CreateUserRequestDto{
    Username: "john",
    Email:    "john@example.com",
})

// Get user by ID
user, err := client.Users().GetByID(ctx, "user-uuid")

// Get user by username
user, err := client.Users().GetByUsername(ctx, "john")

// Get user by email
user, err := client.Users().GetByEmail(ctx, "john@example.com")

// Update user
user, err := client.Users().Update(ctx, &remapi.UpdateUserRequestDto{
    UUID:  "user-uuid",
    Email: "newemail@example.com",
})

// Enable/Disable user
client.Users().Enable(ctx, "user-uuid")
client.Users().Disable(ctx, "user-uuid")

// Reset user traffic
client.Users().ResetTraffic(ctx, "user-uuid")

// Delete user
client.Users().Delete(ctx, "user-uuid")

// Get user tags
tags, err := client.Users().GetTags(ctx)

// Get users by tag
users, err := client.Users().GetByTag(ctx, "tag-name")
```

### Node Operations

```go
// Get all nodes
nodes, err := client.Nodes().GetAll(ctx)

// Create node
node, err := client.Nodes().Create(ctx, &remapi.CreateNodeRequestDto{
    Name: "Node-1",
})

// Get node by ID
node, err := client.Nodes().GetByID(ctx, "node-uuid")

// Update node
node, err := client.Nodes().Update(ctx, &remapi.UpdateNodeRequestDto{
    UUID: "node-uuid",
    Name: "Updated-Node",
})

// Enable/Disable node
client.Nodes().Enable(ctx, "node-uuid")
client.Nodes().Disable(ctx, "node-uuid")

// Restart node
client.Nodes().Restart(ctx, "node-uuid")

// Restart all nodes
client.Nodes().RestartAll(ctx)

// Delete node
client.Nodes().Delete(ctx, "node-uuid")

// Reorder nodes
client.Nodes().Reorder(ctx, &remapi.ReorderNodeRequestDto{
    UUIDs: []string{"node-1", "node-2", "node-3"},
})
```

### Host Operations

```go
// Get all hosts
hosts, err := client.Hosts().GetAll(ctx)

// Create host
host, err := client.Hosts().Create(ctx, &remapi.CreateHostRequestDto{
    Name: "Host-1",
})

// Get host by ID
host, err := client.Hosts().GetByID(ctx, "host-uuid")

// Update host
host, err := client.Hosts().Update(ctx, &remapi.UpdateHostRequestDto{
    UUID: "host-uuid",
    Name: "Updated-Host",
})

// Delete host
client.Hosts().Delete(ctx, "host-uuid")

// Get host tags
tags, err := client.Hosts().GetTags(ctx)

// Reorder hosts
client.Hosts().Reorder(ctx, &remapi.ReorderHostRequestDto{
    UUIDs: []string{"host-1", "host-2"},
})
```

### Authentication Operations

```go
// Login
loginResp, err := client.Auth().Login(ctx, &remapi.LoginRequestDto{
    Username: "admin",
    Password: "password",
})

// Register
registerResp, err := client.Auth().Register(ctx, &remapi.RegisterRequestDto{
    Username: "newuser",
    Email:    "newuser@example.com",
    Password: "password",
})

// Get auth status
status, err := client.Auth().GetStatus(ctx)

// OAuth2 authorize
oauthResp, err := client.Auth().OAuth2Authorize(ctx, &remapi.OAuth2AuthorizeRequestDto{
    Provider: "github",
})
```

### System Operations

```go
// Get system health
health, err := client.System().GetHealth(ctx)

// Get stats
stats, err := client.System().GetStats(ctx)

// Get bandwidth stats
bwStats, err := client.System().GetBandwidthStats(ctx)

// Get nodes statistics
nodesStats, err := client.System().GetNodesStatistics(ctx)

// Get nodes metrics
metrics, err := client.System().GetNodesMetrics(ctx)
```

---

## Tools & Utilities

### 1. Schema Analysis Tool

**Find duplicate and identical schemas in OpenAPI specifications:**

```bash
# Analyze api-2-2-0.json for duplicate schemas
python3 find_duplicate_schemas.py api-2-2-0.json

# Show only first 10 duplicate groups
python3 find_duplicate_schemas.py api-2-2-0.json 10
```

**Features:**
- Finds identical request/response DTOs
- Groups schemas by type and pattern
- Provides consolidation recommendations
- Handles malformed JSON files
- Generates detailed analysis reports

For detailed usage and examples, see [SCHEMA_ANALYZER_README.md](SCHEMA_ANALYZER_README.md)

### 2. Schema Consolidation Tools

**Consolidate duplicate schemas for cleaner API specifications:**

```bash
# Create consolidated schema (removes 42.1% duplicate definitions)
python3 create_consolidated_schema.py api-2-2-0.json api-2-2-0-consolidated.json

# Analyze the consolidated result
python3 find_duplicate_schemas.py api-2-2-0-consolidated.json
```

**Consolidation Results:**
- **Original:** 195 schemas (691 KB)
- **Consolidated:** 113 schemas (420 KB)
- **Reduction:** 82 schemas (-42.1%), 271 KB saved (-39.2%)
- **Generic Schemas:** 4 new reusable patterns

**New Generic Schemas Created:**
- `DeleteResponseDto` - for all DELETE operations (8 schemas consolidated)
- `EventResponseDto` - for event-based operations (8 schemas consolidated)
- `BulkActionResponseDto` - for bulk operations (6 schemas consolidated)
- `BulkUuidsRequestDto` - for bulk request handling (5 schemas consolidated)

For detailed consolidation report, see [CONSOLIDATION_REPORT.md](CONSOLIDATION_REPORT.md)

---

## Requirements

|                         | Version                 |
|-------------------------|-------------------------|
| **Go**                  | 1.25+                   |
| **Remnawave API**       | 2.2.0+                  |
| **Remnawave JWT token** | Obtainable in the panel |
| **Python** (optional)   | 3.6+ (for schema analysis)|


---

## Donation Methods

- **Bep20 USDT:** `0x4D1ee2445fdC88fA49B9d02FB8ee3633f45Bef48`

- **SOL Solana:** `HNQhe6SCoU5UDZicFKMbYjQNv9Muh39WaEWbZayQ9Nn8`

- **TRC20 USDT:** `TBJrguLia8tvydsQ2CotUDTYtCiLDA4nPW`

- **TON USDT:** `UQAdAhVxOr9LS07DDQh0vNzX2575Eu0eOByjImY1yheatXgr`
---

## License

[MIT](LICENSE.MD) — free to use; a ★ on GitHub is always appreciated!


