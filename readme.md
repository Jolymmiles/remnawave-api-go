# Remnawave GO SDK


[![Stars](https://img.shields.io/github/stars/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/stargazers)
[![Forks](https://img.shields.io/github/forks/Jolymmiles/remnawave-api-go.svg?style=social)](https://github.com/Jolymmiles/remnawave-api-go/network/members)
[![Issues](https://img.shields.io/github/issues/Jolymmiles/remnawave-api-go.svg)](https://github.com/Jolymmiles/remnawave-api-go/issues)

A Go SDK client for interacting with the **[Remnawave API](https://remna.st)**.
Library checked with Remnawave **[v2.0.0](https://github.com/remnawave/panel/releases/tag/1.5.7)**

The client is generated with [**ogen**](https://github.com/ogen-go/ogen):

* zero-reflection JSON decoder for high throughput,
* compile-time validation against the OpenAPI 3.0 spec,
* first-class `context.Context` support,
* pluggable middleware (`http.RoundTripper`, retries, tracing, …).

**TL;DR**

```bash
go get github.com/Jolymmiles/remnawave-api-go@latest
````

```go

import (
	"context"
	"fmt"
	remapi "github.com/Jolymmiles/remnawave-api-go/api"
)

func main() {
	ctx := context.Background()

	rclient, _ := remapi.NewClient(
		"https://example.com",       //server url
		remapi.StaticToken{Token: "JWT_TOKEN"}, //your JWT token
	)

	resp, err := rclient.NodesControllerGetAllNodes(ctx)
	if err != nil {
		panic(err)
	}
	fmt.Println(resp)
}
```

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


