package api

import "context"

type StaticToken struct{ token string }

func (s StaticToken) Authorization(_ context.Context, _ OperationName) (Authorization, error) {
	return Authorization{Token: s.token}, nil
}
