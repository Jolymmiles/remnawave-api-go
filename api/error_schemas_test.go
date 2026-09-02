package api

import (
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"testing"
)

func TestNotFoundErrorDecodesRemnawaveBusinessError(t *testing.T) {
	var got NotFoundError

	err := json.Unmarshal([]byte(`{
		"timestamp":"2026-09-02T16:46:31.329Z",
		"path":"/api/users/by-username/6_6838962",
		"message":"User with specified params not found",
		"errorCode":"A063"
	}`), &got)
	if err != nil {
		t.Fatalf("decode Remnawave 404: %v", err)
	}
	if got.Message != "User with specified params not found" {
		t.Fatalf("message = %q, want %q", got.Message, "User with specified params not found")
	}
	if got.ErrorCode.Value != "A063" || !got.ErrorCode.Set {
		t.Fatalf("errorCode = %#v, want set to A063", got.ErrorCode)
	}
	if got.StatusCode.Set {
		t.Fatalf("statusCode unexpectedly set: %#v", got.StatusCode)
	}
}

func TestNotFoundErrorDecodesLegacyStatusCode(t *testing.T) {
	var got NotFoundError

	err := json.Unmarshal([]byte(`{
		"message":"Not Found",
		"statusCode":404
	}`), &got)
	if err != nil {
		t.Fatalf("decode legacy 404: %v", err)
	}
	if !got.StatusCode.Set || got.StatusCode.Value != 404 {
		t.Fatalf("statusCode = %#v, want set to 404", got.StatusCode)
	}
}

func TestUsersGetUserByUsernameDecodesRemnawaveNotFoundResponse(t *testing.T) {
	resp := &http.Response{
		StatusCode: http.StatusNotFound,
		Header:     make(http.Header),
		Body: io.NopCloser(strings.NewReader(`{
			"timestamp":"2026-09-02T16:46:31.329Z",
			"path":"/api/users/by-username/6_6838962",
			"message":"User with specified params not found",
			"errorCode":"A063"
		}`)),
	}
	resp.Header.Set("Content-Type", "application/json")

	decoded, err := decodeUsersGetUserByUsernameResponse(resp)
	if err != nil {
		t.Fatalf("decode users by username 404 response: %v", err)
	}
	notFound, ok := decoded.(*NotFoundError)
	if !ok {
		t.Fatalf("response type = %T, want *NotFoundError", decoded)
	}
	if notFound.GetMessage() != "User with specified params not found" {
		t.Fatalf("message = %q, want %q", notFound.GetMessage(), "User with specified params not found")
	}
}

func TestBadRequestErrorDecodesBusinessError(t *testing.T) {
	var got BadRequestError

	err := json.Unmarshal([]byte(`{
		"timestamp":"2026-09-02T16:46:31.329Z",
		"path":"/api/users",
		"message":"User username already exists",
		"errorCode":"A019"
	}`), &got)
	if err != nil {
		t.Fatalf("decode Remnawave business 400: %v", err)
	}
	if got.Message != "User username already exists" {
		t.Fatalf("message = %q, want %q", got.Message, "User username already exists")
	}
	if got.ErrorCode.Value != "A019" || !got.ErrorCode.Set {
		t.Fatalf("errorCode = %#v, want set to A019", got.ErrorCode)
	}
	if got.Errors != nil {
		t.Fatalf("errors unexpectedly set: %#v", got.Errors)
	}
}

func TestBadRequestErrorDecodesValidationError(t *testing.T) {
	var got BadRequestError

	err := json.Unmarshal([]byte(`{
		"message":"Validation failed",
		"statusCode":400,
		"errors":[{
			"validation":"uuid",
			"code":"invalid_string",
			"message":"Invalid uuid",
			"path":["id"]
		}]
	}`), &got)
	if err != nil {
		t.Fatalf("decode validation 400: %v", err)
	}
	if len(got.Errors) != 1 || got.Errors[0].Message != "Invalid uuid" {
		t.Fatalf("errors = %#v, want one Invalid uuid error", got.Errors)
	}
	if !got.StatusCode.Set || got.StatusCode.Value != 400 {
		t.Fatalf("statusCode = %#v, want set to 400", got.StatusCode)
	}
}
