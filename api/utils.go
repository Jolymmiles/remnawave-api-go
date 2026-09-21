package api

import (
	"context"
	"errors"
	"strings"
)

// StaticToken supplies a fixed API token for every request.
type StaticToken struct{ Token string }

func (s StaticToken) Authorization(_ context.Context, _ OperationName) (Authorization, error) {
	token := strings.TrimSpace(s.Token)
	if len(token) >= len("Bearer ") && strings.EqualFold(token[:len("Bearer ")], "Bearer ") {
		token = strings.TrimSpace(token[len("Bearer "):])
	}
	if token == "" {
		return Authorization{}, errors.New("remnawave: token must not be empty")
	}
	return Authorization{Token: token}, nil
}
