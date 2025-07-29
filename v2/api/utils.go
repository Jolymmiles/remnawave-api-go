package api

import "context"

type StaticToken struct{ Token string }

func (s StaticToken) Authorization(_ context.Context, _ OperationName) (Authorization, error) {
	return Authorization{Token: s.Token}, nil
}
