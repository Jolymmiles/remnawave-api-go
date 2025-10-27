package api

import (
	"encoding/json"
	"fmt"
	"log"
)

// UnknownFieldsDecoder is a wrapper that safely handles unknown fields in JSON responses.
// It allows the library to gracefully handle API responses that contain fields not defined in the DTO models.
type UnknownFieldsDecoder struct {
	// If true, logs warnings about unknown fields
	LogUnknownFields bool
	// If true, ignores unknown fields silently
	SilentMode bool
}

// NewUnknownFieldsDecoder creates a new decoder that handles unknown fields
func NewUnknownFieldsDecoder() *UnknownFieldsDecoder {
	return &UnknownFieldsDecoder{
		LogUnknownFields: false,
		SilentMode:       true,
	}
}

// DecodeWithUnknownFields decodes JSON data into a struct, ignoring unknown fields
// This is useful for API responses that might contain new fields not yet defined in the DTO
func (d *UnknownFieldsDecoder) DecodeWithUnknownFields(data []byte, v interface{}) error {
	// First, try to unmarshal into a map to capture unknown fields
	var rawData map[string]interface{}
	if err := json.Unmarshal(data, &rawData); err != nil {
		return err
	}

	// Then unmarshal into the actual struct (unknown fields will be ignored)
	if err := json.Unmarshal(data, v); err != nil {
		// If there's an error, return it
		return err
	}

	// Log unknown fields if configured
	if d.LogUnknownFields && !d.SilentMode {
		d.logUnknownFields(rawData, v)
	}

	return nil
}

// logUnknownFields logs any fields in the raw data that weren't mapped to the struct
func (d *UnknownFieldsDecoder) logUnknownFields(rawData map[string]interface{}, v interface{}) {
	// Get the JSON marshaling of the struct to see which fields were accepted
	structBytes, err := json.Marshal(v)
	if err != nil {
		return
	}

	var structData map[string]interface{}
	if err := json.Unmarshal(structBytes, &structData); err != nil {
		return
	}

	// Compare and find unknown fields
	for key := range rawData {
		if _, exists := structData[key]; !exists {
			log.Printf("ℹ️ Unknown field in API response: '%s'", key)
		}
	}
}

// ResponseWrapper is a generic wrapper for API responses that might have unknown fields
type ResponseWrapper struct {
	Data   interface{}            `json:"-"`
	Raw    map[string]interface{} `json:"-"`
	Fields map[string]interface{} `json:"-"`
}

// UnmarshalJSON implements custom unmarshaling that preserves all fields
func (r *ResponseWrapper) UnmarshalJSON(data []byte) error {
	if err := json.Unmarshal(data, &r.Raw); err != nil {
		return err
	}
	r.Fields = r.Raw
	return nil
}

// GetField retrieves a field from the response, returning nil if not found
func (r *ResponseWrapper) GetField(key string) interface{} {
	if r.Fields == nil {
		return nil
	}
	return r.Fields[key]
}

// GetString retrieves a string field, returning empty string if not found or wrong type
func (r *ResponseWrapper) GetString(key string) string {
	val := r.GetField(key)
	if str, ok := val.(string); ok {
		return str
	}
	return ""
}

// GetInt retrieves an int field, returning 0 if not found or wrong type
func (r *ResponseWrapper) GetInt(key string) int {
	val := r.GetField(key)
	switch v := val.(type) {
	case float64:
		return int(v)
	case int:
		return v
	}
	return 0
}

// GetBool retrieves a bool field, returning false if not found or wrong type
func (r *ResponseWrapper) GetBool(key string) bool {
	val := r.GetField(key)
	if b, ok := val.(bool); ok {
		return b
	}
	return false
}

// HasField checks if a field exists in the response
func (r *ResponseWrapper) HasField(key string) bool {
	if r.Fields == nil {
		return false
	}
	_, exists := r.Fields[key]
	return exists
}

// GetUnknownFields returns all fields that are not standard (helper for debugging)
func GetUnknownFields(rawJSON map[string]interface{}, knownFields map[string]bool) map[string]interface{} {
	unknown := make(map[string]interface{})
	for key, value := range rawJSON {
		if !knownFields[key] {
			unknown[key] = value
		}
	}
	return unknown
}

// SafeFieldExtraction safely extracts a nested field from an interface{} value
func SafeFieldExtraction(data interface{}, path ...string) (interface{}, error) {
	current := data

	for _, key := range path {
		switch v := current.(type) {
		case map[string]interface{}:
			var exists bool
			current, exists = v[key]
			if !exists {
				return nil, fmt.Errorf("field '%s' not found", key)
			}
		default:
			return nil, fmt.Errorf("cannot traverse field '%s': current value is not a map", key)
		}
	}

	return current, nil
}

// MustFieldExtraction extracts a field or returns nil without error
func MustFieldExtraction(data interface{}, path ...string) interface{} {
	result, _ := SafeFieldExtraction(data, path...)
	return result
}
