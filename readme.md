# remnawave-api-go

**remnawave-api-go** is a slim, type-safe Go SDK for the public REST API  
of [Remnawave](https://remna.st/api).

The client is generated with [**ogen**](https://github.com/ogen-go/ogen):

* zero-reflection JSON decoder for high throughput,
* compile-time validation against the OpenAPI 3.0 spec,
* first-class `context.Context` support,
* pluggable middleware (`http.RoundTripper`, retries, tracing, …).

**TL;DR**

```bash
go get github.com/Jolymmiles/remnawave-api-go
````

```go
cli, _ := remapi.NewClient(
"https://remna.st/api",
remapi.StaticToken("YOUR_JWT"), // built-in SecuritySource
)
u, _ := cli.UsersControllerGetUserByTelegramId(ctx,
remapi.UsersControllerGetUserByTelegramIdParams{TelegramId: 123456789})
```

---

## Requirements

|                         | Minimum                 |
|-------------------------|-------------------------|
| **Go**                  | 1.24                    |
| **Remnawave JWT token** | Obtainable in the panel |


## Contributing

Bug-fixes, doc updates and new examples are welcome.

```bash
go vet ./...
go test ./...
golangci-lint run
```

---

## Donation Methods

- **Bep20 USDT:** `0x4D1ee2445fdC88fA49B9d02FB8ee3633f45Bef48`

- **SOL Solana:** `HNQhe6SCoU5UDZicFKMbYjQNv9Muh39WaEWbZayQ9Nn8`

- **TRC20 USDT:** `TBJrguLia8tvydsQ2CotUDTYtCiLDA4nPW`

- **TON USDT:** `UQAdAhVxOr9LS07DDQh0vNzX2575Eu0eOByjImY1yheatXgr`
---

## License

[MIT](LICENSE) — free to use; a ★ on GitHub is always appreciated!


