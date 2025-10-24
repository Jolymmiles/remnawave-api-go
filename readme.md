# Remnawave GO SDK


[![Stars](https://img.shields.io/github/stars/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/stargazers)
[![Forks](https://img.shields.io/github/forks/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/network/members)
[![Issues](https://img.shields.io/github/issues/Jolymmiles/remnawave-api-go.svg)](https://github.com/Jolymmiles/remnawave-api-go/issues)

A Go SDK client for interacting with the **[Remnawave API](https://remna.st)**.
Library checked with Remnawave **[v2.2.0](https://github.com/remnawave/panel/releases/tag/2.0.0)**

The client is generated with [**ogen**](https://github.com/ogen-go/ogen):

* zero-reflection JSON decoder for high throughput,
* compile-time validation against the OpenAPI 3.0 spec,
* first-class `context.Context` support,
* pluggable middleware (`http.RoundTripper`, retries, tracing, …),
* **organized sub-clients for better API organization** ✨

**TL;DR**

```bash
go get github.com/Jolymmiles/remnawave-api-go@latest
````

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

**📖 [See detailed examples →](SUBCLIENT_EXAMPLES.md)**

---

## Requirements

|                         | Minimum                 |
|-------------------------|-------------------------|
| **Go**                  | 1.24                    |
| **Remnawave JWT token** | Obtainable in the panel |


---

## Donation Methods

- **Bep20 USDT:** `0x4D1ee2445fdC88fA49B9d02FB8ee3633f45Bef48`

- **SOL Solana:** `HNQhe6SCoU5UDZicFKMbYjQNv9Muh39WaEWbZayQ9Nn8`

- **TRC20 USDT:** `TBJrguLia8tvydsQ2CotUDTYtCiLDA4nPW`

- **TON USDT:** `UQAdAhVxOr9LS07DDQh0vNzX2575Eu0eOByjImY1yheatXgr`
---

## License

[MIT](LICENSE.MD) — free to use; a ★ on GitHub is always appreciated!


