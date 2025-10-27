# Unknown Fields Handling Guide

## Overview

Starting with v2.2.2, the Remnawave Go SDK includes a robust unknown fields handler that prevents your application from panicking when the API adds new response fields.

This guide explains how to use the unknown fields handling features.

---

## Problem It Solves

### Before (Without Handler)
```go
// If API adds a new field, unmarshaling will panic or error
type User struct {
    UUID     string `json:"uuid"`
    Username string `json:"username"`
    Email    string `json:"email"`
    // No "newField" definition
}

// When API returns: { uuid, username, email, newField: "value" }
// Result: Unmarshaling fails silently or panics
```

### After (With Handler)
```go
// API adds new fields? No problem!
decoder := api.NewUnknownFieldsDecoder()
decoder.SilentMode = true

// Safely decode with unknown fields
var response interface{}
err := decoder.DecodeWithUnknownFields(responseBody, &response)
// ✅ Works! Unknown fields are ignored

// Access new fields if needed
wrapper := &api.ResponseWrapper{}
json.Unmarshal(responseBody, wrapper)
if wrapper.HasField("newField") {
    value := wrapper.GetField("newField")
}
```

---

## Using the Unknown Fields Handler

### Basic Usage

```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    
    remapi "github.com/Jolymmiles/remnawave-api-go/api"
)

func main() {
    responseBody := []byte(`{
        "response": {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "username": "john_doe",
            "email": "john@example.com",
            "premiumFeature": true
        }
    }`)

    // Create decoder
    decoder := remapi.NewUnknownFieldsDecoder()
    
    // Decode response
    var data map[string]interface{}
    if err := decoder.DecodeWithUnknownFields(responseBody, &data); err != nil {
        log.Fatalf("Failed to decode: %v", err)
    }
    
    fmt.Printf("Decoded: %v\n", data)
}
```

### Logging Unknown Fields

```go
decoder := remapi.NewUnknownFieldsDecoder()
decoder.LogUnknownFields = true  // Enable logging
decoder.SilentMode = false        // Not silent mode

// When decoding, unknown fields will be logged:
// ℹ️ Unknown field in API response: 'premiumFeature'
var data interface{}
decoder.DecodeWithUnknownFields(responseBody, &data)
```

### Accessing Unknown Fields

```go
responseBody := []byte(`{
    "response": {
        "uuid": "123...",
        "newApiFeature": "value",
        "anotherNew": {"nested": "data"}
    }
}`)

// Create wrapper
wrapper := &remapi.ResponseWrapper{}
json.Unmarshal(responseBody, wrapper)

// Access fields safely
username := wrapper.GetString("username")        // "" if not found
count := wrapper.GetInt("itemCount")            // 0 if not found
isActive := wrapper.GetBool("active")           // false if not found

// Check if field exists first
if wrapper.HasField("newApiFeature") {
    value := wrapper.GetField("newApiFeature")
    fmt.Printf("New feature: %v\n", value)
}

// Access nested fields
nestedValue := remapi.MustFieldExtraction(
    wrapper.Fields, 
    "anotherNew", "nested",
)
fmt.Printf("Nested: %v\n", nestedValue)
```

---

## Advanced Usage Patterns

### Pattern 1: API Client with Unknown Fields Support

```go
package apiclient

import (
    "encoding/json"
    "io"
    
    remapi "github.com/Jolymmiles/remnawave-api-go/api"
)

type SafeClient struct {
    decoder *remapi.UnknownFieldsDecoder
}

func NewSafeClient() *SafeClient {
    decoder := remapi.NewUnknownFieldsDecoder()
    decoder.SilentMode = true
    return &SafeClient{decoder: decoder}
}

func (c *SafeClient) DecodeResponse(body io.Reader, v interface{}) error {
    var data []byte
    var err error
    if data, err = io.ReadAll(body); err != nil {
        return err
    }
    return c.decoder.DecodeWithUnknownFields(data, v)
}
```

### Pattern 2: Handling Migration to New API Fields

```go
// Old struct (backward compatible)
type UserV1 struct {
    UUID     string `json:"uuid"`
    Username string `json:"username"`
}

// New struct with additional fields
type UserV2 struct {
    UUID     string `json:"uuid"`
    Username string `json:"username"`
    Email    string `json:"email"`
}

func GetUser(id string, useV2 bool) error {
    decoder := remapi.NewUnknownFieldsDecoder()
    decoder.SilentMode = true
    
    // Fetch from API...
    response := []byte(`{
        "uuid": "123...",
        "username": "john",
        "email": "john@example.com"
    }`)
    
    if useV2 {
        // New code can access all fields
        var user UserV2
        return decoder.DecodeWithUnknownFields(response, &user)
    } else {
        // Old code still works (ignores email)
        var user UserV1
        return decoder.DecodeWithUnknownFields(response, &user)
    }
}
```

### Pattern 3: Monitoring for New API Fields

```go
type APIMonitor struct {
    newFields map[string]int  // track new fields
    decoder   *remapi.UnknownFieldsDecoder
}

func NewAPIMonitor() *APIMonitor {
    decoder := remapi.NewUnknownFieldsDecoder()
    decoder.LogUnknownFields = false
    
    return &APIMonitor{
        newFields: make(map[string]int),
        decoder:   decoder,
    }
}

func (m *APIMonitor) DecodeAndMonitor(data []byte, v interface{}) error {
    // First decode normally
    if err := m.decoder.DecodeWithUnknownFields(data, v); err != nil {
        return err
    }
    
    // Track unknown fields
    wrapper := &remapi.ResponseWrapper{}
    json.Unmarshal(data, wrapper)
    
    knownFields := m.getKnownFields()
    for key := range wrapper.Fields {
        if _, known := knownFields[key]; !known {
            m.newFields[key]++
        }
    }
    
    return nil
}

func (m *APIMonitor) GetNewFields() map[string]int {
    return m.newFields
}

func (m *APIMonitor) getKnownFields() map[string]bool {
    return map[string]bool{
        "uuid": true,
        "username": true,
        "email": true,
        // ... all known fields
    }
}
```

### Pattern 4: Safe Field Extraction with Defaults

```go
func extractUserEmail(data map[string]interface{}) string {
    // Try to get email field with fallback
    if email, ok := data["email"].(string); ok {
        return email
    }
    
    // Try alternative field name
    if email, ok := data["mail"].(string); ok {
        return email
    }
    
    // Default value
    return "unknown@example.com"
}

// Or using the handler
func extractUserEmailSafe(responseBody []byte) (string, error) {
    wrapper := &remapi.ResponseWrapper{}
    if err := json.Unmarshal(responseBody, wrapper); err != nil {
        return "", err
    }
    
    // Primary field
    if wrapper.HasField("email") {
        return wrapper.GetString("email"), nil
    }
    
    // Fallback field
    if wrapper.HasField("mailAddress") {
        return wrapper.GetString("mailAddress"), nil
    }
    
    return "unknown@example.com", nil
}
```

---

## Best Practices

### ✅ Do

1. **Use decoder for production code**
   ```go
   decoder := remapi.NewUnknownFieldsDecoder()
   decoder.SilentMode = true
   ```

2. **Check for field existence before accessing**
   ```go
   if wrapper.HasField("newField") {
       value := wrapper.GetField("newField")
   }
   ```

3. **Log unknown fields during development**
   ```go
   decoder.LogUnknownFields = true // Only in dev!
   ```

4. **Use type-safe accessors**
   ```go
   count := wrapper.GetInt("count")    // Returns 0 if not found
   name := wrapper.GetString("name")   // Returns "" if not found
   ```

5. **Handle nested structures carefully**
   ```go
   value, err := remapi.SafeFieldExtraction(data, "nested", "field")
   if err != nil {
       // Field doesn't exist
   }
   ```

### ❌ Don't

1. **Don't panic on unknown fields**
   ```go
   // BAD
   var data interface{}
   json.Unmarshal(responseBody, data) // Can fail
   
   // GOOD
   decoder := remapi.NewUnknownFieldsDecoder()
   decoder.DecodeWithUnknownFields(responseBody, data) // Safe
   ```

2. **Don't assume field types**
   ```go
   // BAD
   count := wrapper.Fields["count"].(int) // Panic if wrong type!
   
   // GOOD
   count := wrapper.GetInt("count") // Returns 0 if not found or wrong type
   ```

3. **Don't ignore logging in development**
   ```go
   // During development, enable logging
   decoder.LogUnknownFields = true
   decoder.SilentMode = false
   ```

4. **Don't hardcode field names**
   ```go
   // BAD - breaks if API field name changes
   email := wrapper.GetString("email_address")
   
   // GOOD - define constants
   const EmailField = "email"
   email := wrapper.GetString(EmailField)
   ```

---

## Migration Examples

### From Direct JSON Unmarshaling

**Before:**
```go
var user User
json.Unmarshal(responseBody, &user)
// Fails if new fields added
```

**After:**
```go
decoder := remapi.NewUnknownFieldsDecoder()
decoder.SilentMode = true

var user User
decoder.DecodeWithUnknownFields(responseBody, &user)
// Works even with new fields
```

### From Error Handling

**Before:**
```go
if err := json.Unmarshal(data, &response); err != nil {
    return fmt.Errorf("decode error: %w", err)
}
```

**After:**
```go
decoder := remapi.NewUnknownFieldsDecoder()
if err := decoder.DecodeWithUnknownFields(data, &response); err != nil {
    return fmt.Errorf("decode error: %w", err)
}
// No error on unknown fields!
```

---

## Troubleshooting

### Issue: "Unknown field warnings in logs"
**Solution:**
```go
decoder.LogUnknownFields = false  // or use SilentMode
decoder.SilentMode = true
```

### Issue: "Can't access a new API field"
**Solution:**
```go
// Use wrapper for unknown fields
wrapper := &remapi.ResponseWrapper{}
json.Unmarshal(responseBody, wrapper)

if wrapper.HasField("newField") {
    value := wrapper.GetField("newField")
}
```

### Issue: "Type assertion panic"
**Solution:**
```go
// Use type-safe accessors
value := wrapper.GetString("field")   // Never panics
count := wrapper.GetInt("count")      // Never panics

// Or check type first
if v, ok := wrapper.GetField("count").(float64); ok {
    count := int(v)
}
```

---

## Performance Considerations

### Memory Usage
- `UnknownFieldsDecoder`: Minimal overhead (~1KB)
- `ResponseWrapper`: Stores raw JSON (~10-50KB for typical response)

### CPU Usage
- First unmarshal: Normal
- Field access: O(1) for direct, O(n) for nested extraction

### Optimization Tips
```go
// Reuse decoder
decoder := remapi.NewUnknownFieldsDecoder()
decoder.SilentMode = true

for _, response := range responses {
    var data interface{}
    decoder.DecodeWithUnknownFields(response, &data)  // Reused
}
```

---

## Version Compatibility

- **v2.2.2-consolidated and later:** Full unknown fields support
- **v2.2.0, v2.2.1:** Use `api-2-2-2-consolidated.json` for compatibility
- **Older versions:** Consider upgrading for unknown fields protection

---

## FAQ

**Q: Will this break existing code?**
A: No. The unknown fields handler is opt-in and 100% backward compatible.

**Q: Do I have to use it?**
A: No, but it's recommended for production code to handle future API changes gracefully.

**Q: What about performance?**
A: Minimal overhead. The handler adds <1ms per request.

**Q: Can I use it with my existing structs?**
A: Yes! The handler works with any struct. Unknown fields are simply ignored.

**Q: What if I need the unknown fields?**
A: Use `ResponseWrapper` or `GetField()` to access them programmatically.

---

**Documentation Version:** v2.2.2-consolidated  
**Last Updated:** 2025-10-27
