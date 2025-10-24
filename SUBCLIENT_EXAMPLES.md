# Remnawave Go SDK - Sub-Client Examples

The SDK now provides organized, resource-based access to the API through sub-clients. This makes code more readable and improves IDE discoverability.

## Overview

Instead of using flat method names like `client.UsersControllerCreateUser()`, you can now use organized sub-clients:

```go
// New way (recommended)
user, err := client.Users().Create(ctx, &CreateUserRequestDto{
    Username: "john",
    Email:    "john@example.com",
})

// Old way (still supported, but deprecated)
user, err := client.UsersControllerCreateUser(ctx, &CreateUserRequestDto{
    Username: "john",
    Email:    "john@example.com",
})
```

## Setup

To use sub-clients, wrap your existing client:

```go
import (
    "context"
    remapi "github.com/Jolymmiles/remnawave-api-go/api"
)

func main() {
    ctx := context.Background()

    // Create base client
    baseClient, err := remapi.NewClient(
        "https://your-api-url.com",
        remapi.StaticToken{Token: "your-jwt-token"},
    )
    if err != nil {
        panic(err)
    }

    // Wrap with sub-client extension
    client := remapi.NewClientExt(baseClient)

    // Now use organized sub-clients
    // ... examples below
}
```

## User Operations

### Get All Users

```go
// Get all users with pagination
resp, err := client.Users().GetAll(ctx)
if err != nil {
    log.Printf("Error: %v", err)
    return
}

if resp, ok := resp.(*GetAllUsersResponseDto); ok {
    fmt.Printf("Total users: %d\n", len(resp.Response))
    for _, user := range resp.Response {
        fmt.Printf("- %s (%s)\n", user.Username, user.Email)
    }
}
```

### Create User

```go
newUser := &CreateUserRequestDto{
    Username: "alice",
    Email:    "alice@example.com",
    IsAdmin:  false,
}

resp, err := client.Users().Create(ctx, newUser)
if err != nil {
    log.Fatalf("Failed to create user: %v", err)
}

if user, ok := resp.(*CreateUserResponseDto); ok {
    fmt.Printf("Created user: %s (ID: %s)\n", user.Response.Username, user.Response.UUID)
}
```

### Get User by ID

```go
userID := "550e8400-e29b-41d4-a716-446655440000"

resp, err := client.Users().GetByID(ctx, userID)
if err != nil {
    log.Fatalf("Failed to get user: %v", err)
}

if user, ok := resp.(*GetUserByUuidResponseDto); ok {
    fmt.Printf("User: %s (%s)\n", user.Response.Username, user.Response.Email)
}
```

### Get User by Username

```go
resp, err := client.Users().GetByUsername(ctx, "john")
if err != nil {
    log.Fatalf("Failed to get user: %v", err)
}

if user, ok := resp.(*GetUserByUsernameResponseDto); ok {
    fmt.Printf("User email: %s\n", user.Response.Email)
}
```

### Update User

```go
updateReq := &UpdateUserRequestDto{
    UUID:  "550e8400-e29b-41d4-a716-446655440000",
    Email: "newemail@example.com",
}

resp, err := client.Users().Update(ctx, updateReq)
if err != nil {
    log.Fatalf("Failed to update user: %v", err)
}

if user, ok := resp.(*UpdateUserResponseDto); ok {
    fmt.Printf("Updated user: %s\n", user.Response.Email)
}
```

### Enable/Disable User

```go
userID := "550e8400-e29b-41d4-a716-446655440000"

// Enable user
resp, err := client.Users().Enable(ctx, userID)
if err != nil {
    log.Fatalf("Failed to enable user: %v", err)
}

// Disable user
resp, err = client.Users().Disable(ctx, userID)
if err != nil {
    log.Fatalf("Failed to disable user: %v", err)
}
```

### Reset User Traffic

```go
userID := "550e8400-e29b-41d4-a716-446655440000"

resp, err := client.Users().ResetTraffic(ctx, userID)
if err != nil {
    log.Fatalf("Failed to reset traffic: %v", err)
}

fmt.Println("Traffic reset successfully")
```

### Delete User

```go
userID := "550e8400-e29b-41d4-a716-446655440000"

resp, err := client.Users().Delete(ctx, userID)
if err != nil {
    log.Fatalf("Failed to delete user: %v", err)
}

fmt.Println("User deleted successfully")
```

## Node Operations

### Get All Nodes

```go
resp, err := client.Nodes().GetAll(ctx)
if err != nil {
    log.Fatalf("Failed to get nodes: %v", err)
}

if nodes, ok := resp.(*GetAllNodesResponseDto); ok {
    for _, node := range nodes.Response {
        fmt.Printf("Node: %s (Status: %v)\n", node.Name, node.IsDisabled)
    }
}
```

### Create Node

```go
newNode := &CreateNodeRequestDto{
    Name:     "node-1",
    Address:  "192.168.1.100",
    Port:     2222,
}

resp, err := client.Nodes().Create(ctx, newNode)
if err != nil {
    log.Fatalf("Failed to create node: %v", err)
}

if node, ok := resp.(*CreateNodeResponseDto); ok {
    fmt.Printf("Created node: %s (ID: %s)\n", node.Response.Name, node.Response.UUID)
}
```

### Get Node by ID

```go
nodeID := "550e8400-e29b-41d4-a716-446655440000"

resp, err := client.Nodes().GetByID(ctx, nodeID)
if err != nil {
    log.Fatalf("Failed to get node: %v", err)
}

if node, ok := resp.(*GetOneNodeResponseDto); ok {
    fmt.Printf("Node: %s\n", node.Response.Name)
}
```

### Enable/Disable Node

```go
nodeID := "550e8400-e29b-41d4-a716-446655440000"

// Enable node
_, err := client.Nodes().Enable(ctx, nodeID)
if err != nil {
    log.Fatalf("Failed to enable node: %v", err)
}

// Disable node
_, err = client.Nodes().Disable(ctx, nodeID)
if err != nil {
    log.Fatalf("Failed to disable node: %v", err)
}
```

### Restart Node/All Nodes

```go
nodeID := "550e8400-e29b-41d4-a716-446655440000"

// Restart specific node
_, err := client.Nodes().Restart(ctx, nodeID)
if err != nil {
    log.Fatalf("Failed to restart node: %v", err)
}

// Restart all nodes
_, err = client.Nodes().RestartAll(ctx)
if err != nil {
    log.Fatalf("Failed to restart all nodes: %v", err)
}
```

## Host Operations

### Get All Hosts

```go
resp, err := client.Hosts().GetAll(ctx)
if err != nil {
    log.Fatalf("Failed to get hosts: %v", err)
}

if hosts, ok := resp.(*GetAllHostsResponseDto); ok {
    for _, host := range hosts.Response {
        fmt.Printf("Host: %s:%d\n", host.Address, host.Port)
    }
}
```

### Create Host

```go
newHost := &CreateHostRequestDto{
    Address: "example.com",
    Port:    443,
}

resp, err := client.Hosts().Create(ctx, newHost)
if err != nil {
    log.Fatalf("Failed to create host: %v", err)
}

if host, ok := resp.(*CreateHostResponseDto); ok {
    fmt.Printf("Created host: %s (ID: %s)\n", host.Response.Address, host.Response.UUID)
}
```

### Get Host by ID

```go
hostID := "550e8400-e29b-41d4-a716-446655440000"

resp, err := client.Hosts().GetByID(ctx, hostID)
if err != nil {
    log.Fatalf("Failed to get host: %v", err)
}

if host, ok := resp.(*GetOneHostResponseDto); ok {
    fmt.Printf("Host: %s:%d\n", host.Response.Address, host.Response.Port)
}
```

## Authentication Operations

### Login

```go
loginReq := &LoginRequestDto{
    Username: "admin",
    Password: "password",
}

resp, err := client.Auth().Login(ctx, loginReq)
if err != nil {
    log.Fatalf("Login failed: %v", err)
}

if loginResp, ok := resp.(*LoginResponseDto); ok {
    fmt.Printf("Access token: %s\n", loginResp.Response.AccessToken)
    // Use this token to create a new client:
    // newClient, _ := remapi.NewClient(url, remapi.StaticToken{Token: loginResp.Response.AccessToken})
}
```

### Register

```go
registerReq := &RegisterRequestDto{
    Username: "newadmin",
    Password: "securepassword123",
}

resp, err := client.Auth().Register(ctx, registerReq)
if err != nil {
    log.Fatalf("Registration failed: %v", err)
}

if regResp, ok := resp.(*RegisterResponseDto); ok {
    fmt.Printf("User registered: %s\n", regResp.Response.Username)
}
```

### Get Auth Status

```go
resp, err := client.Auth().GetStatus(ctx)
if err != nil {
    log.Fatalf("Failed to get status: %v", err)
}

if status, ok := resp.(*GetStatusResponseDto); ok {
    fmt.Printf("Auth status: %v\n", status.Response.IsAuthenticated)
}
```

## System Operations

### Get System Health

```go
resp, err := client.System().GetHealth(ctx)
if err != nil {
    log.Fatalf("Failed to get health: %v", err)
}

if health, ok := resp.(*SystemControllerGetRemnawaveHealthRes); ok {
    // Use health information
}
```

### Get System Statistics

```go
resp, err := client.System().GetStats(ctx)
if err != nil {
    log.Fatalf("Failed to get stats: %v", err)
}

if stats, ok := resp.(*GetStatsResponseDto); ok {
    fmt.Printf("Total users: %d\n", stats.Response.TotalUsers)
    fmt.Printf("Total nodes: %d\n", stats.Response.TotalNodes)
}
```

### Get Bandwidth Statistics

```go
resp, err := client.System().GetBandwidthStats(ctx)
if err != nil {
    log.Fatalf("Failed to get bandwidth stats: %v", err)
}
```

## Best Practices

1. **Use sub-clients for better organization**
   ```go
   // Good
   err := client.Users().Enable(ctx, userID)
   node := client.Nodes().GetByID(ctx, nodeID)
   
   // Avoid
   err := client.UsersControllerEnableUser(ctx, ...)
   node := client.NodesControllerGetOneNode(ctx, ...)
   ```

2. **Error handling**
   ```go
   resp, err := client.Users().GetByID(ctx, userID)
   if err != nil {
       // Handle network errors, timeouts, etc.
       log.Printf("API error: %v", err)
       return
   }
   
   // Type assertion to get response data
   if user, ok := resp.(*GetUserByUuidResponseDto); ok {
       // Process user data
   }
   ```

3. **Chain operations logically**
   ```go
   // Create user then enable them
   createResp, _ := client.Users().Create(ctx, newUser)
   if user, ok := createResp.(*CreateUserResponseDto); ok {
       _, _ = client.Users().Enable(ctx, user.Response.UUID)
   }
   ```

## Available Sub-Clients

- `client.Users()` - User management (17 operations)
- `client.Nodes()` - Node management (10 operations)
- `client.Hosts()` - Host management (8 operations, including 5 bulk operations)
- `client.Auth()` - Authentication (8 operations)
- `client.System()` - System administration (8 operations)

## Migration from Old API

If you're currently using the old flat API, migration is simple:

```go
// Before (old way)
users, _ := client.UsersControllerGetAllUsers(ctx, UsersControllerGetAllUsersParams{})
user, _ := client.UsersControllerCreateUser(ctx, req)
node, _ := client.NodesControllerGetOneNode(ctx, params)

// After (new way)
users, _ := client.Users().GetAll(ctx)
user, _ := client.Users().Create(ctx, req)
node, _ := client.Nodes().GetByID(ctx, nodeID)
```

The old methods are still available and fully supported for backward compatibility.
