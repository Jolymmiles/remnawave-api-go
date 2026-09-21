package api

import (
	"testing"
	"time"
)

func TestNodeConnectionsStreamMessageDecodeUsers(t *testing.T) {
	t.Parallel()

	m := NodeConnectionsStreamMessage{
		Users: `[{"userId":"42","ips":[{"ip":"203.0.113.10","lastSeen":"2026-07-16T11:59:30Z"}]}]`,
	}
	users, err := m.DecodeUsers()
	if err != nil {
		t.Fatalf("DecodeUsers() error = %v", err)
	}
	if len(users) != 1 || users[0].UserID != "42" || len(users[0].IPs) != 1 {
		t.Fatalf("DecodeUsers() = %#v, want one user with one IP", users)
	}
	if want := time.Date(2026, time.July, 16, 11, 59, 30, 0, time.UTC); !users[0].IPs[0].LastSeen.Equal(want) {
		t.Fatalf("LastSeen = %v, want %v", users[0].IPs[0].LastSeen, want)
	}
}

func TestNodeConnectionsStreamMessageDecodeUsersRejectsInvalidJSON(t *testing.T) {
	t.Parallel()

	if _, err := (NodeConnectionsStreamMessage{Users: "not-json"}).DecodeUsers(); err == nil {
		t.Fatal("DecodeUsers() error = nil, want an error")
	}
}
