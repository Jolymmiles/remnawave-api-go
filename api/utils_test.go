package api

import (
	"context"
	"net/http"
	"testing"
)

func TestStaticTokenAuthorizationNormalizesBearerPrefix(t *testing.T) {
	t.Parallel()

	security, err := (StaticToken{Token: "  bEaReR  token-value  "}).Authorization(
		context.Background(),
		OperationName("test"),
	)
	if err != nil {
		t.Fatalf("Authorization() error = %v", err)
	}
	if security.Token != "token-value" {
		t.Fatalf("Authorization().Token = %q, want %q", security.Token, "token-value")
	}
}

func TestStaticTokenAuthorizationRejectsEmptyToken(t *testing.T) {
	t.Parallel()

	_, err := (StaticToken{}).Authorization(context.Background(), OperationName("test"))
	if err == nil {
		t.Fatal("Authorization() error = nil, want an error")
	}
}

func TestStaticTokenAuthorizationProducesBearerHeader(t *testing.T) {
	t.Parallel()

	client := &Client{sec: StaticToken{Token: "Bearer token-value"}}
	req, err := http.NewRequestWithContext(context.Background(), http.MethodGet, "https://example.test", nil)
	if err != nil {
		t.Fatal(err)
	}
	if err := client.securityAuthorization(context.Background(), OperationName("test"), req); err != nil {
		t.Fatalf("securityAuthorization() error = %v", err)
	}
	if got, want := req.Header.Get("Authorization"), "Bearer token-value"; got != want {
		t.Fatalf("Authorization header = %q, want %q", got, want)
	}
}
