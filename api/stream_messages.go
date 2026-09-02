package api

import (
	"encoding/json"
	"time"
)

// UserUsageStreamMessage is a message from the
// ioraw:export:user_usage Redis Stream.
//
// NodeID and the user IDs inside Records are strings because the backend
// serializes bigint values as decimal strings. Records has the wire format
// "userId:totalBytes;userId:totalBytes".
type UserUsageStreamMessage struct {
	Version   string    `json:"v"`
	NodeID    string    `json:"nodeId"`
	Timestamp time.Time `json:"ts"`
	Records   string    `json:"records"`
}

// SubscriptionRequestStreamMessage is a message from the
// ioraw:export:subscription_requests Redis Stream.
type SubscriptionRequestStreamMessage struct {
	Version         string    `json:"v"`
	UserID          string    `json:"userId"`
	RequestedAt     time.Time `json:"requestAt"`
	RequestIP       *string   `json:"requestIp,omitempty"`
	UserAgent       *string   `json:"userAgent,omitempty"`
	SRRRuleName     *string   `json:"srrRuleName,omitempty"`
	SRRResponseType string    `json:"srrResponseType"`
}

// NodeConnectionsStreamMessage is a message from the
// ioraw:export:node_connections Redis Stream.
//
// Users is a JSON-encoded array in the stream protocol. Use DecodeUsers to
// parse it into typed Go values.
type NodeConnectionsStreamMessage struct {
	Version   string    `json:"v"`
	NodeID    string    `json:"nodeId"`
	Timestamp time.Time `json:"ts"`
	Users     string    `json:"users"`
}

// NodeConnectionUser describes one user in a node connection snapshot.
type NodeConnectionUser struct {
	UserID string             `json:"userId"`
	IPs    []NodeConnectionIP `json:"ips"`
}

// NodeConnectionIP describes an IP observed for a connected user.
type NodeConnectionIP struct {
	IP       string    `json:"ip"`
	LastSeen time.Time `json:"lastSeen"`
}

// DecodeUsers decodes the nested users JSON from a node connection message.
func (m NodeConnectionsStreamMessage) DecodeUsers() ([]NodeConnectionUser, error) {
	var users []NodeConnectionUser
	if err := json.Unmarshal([]byte(m.Users), &users); err != nil {
		return nil, err
	}
	return users, nil
}
