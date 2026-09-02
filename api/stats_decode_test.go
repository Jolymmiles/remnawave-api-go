package api

import (
	"testing"

	"github.com/go-faster/jx"
	"github.com/stretchr/testify/require"
)

func TestGetStatsResponseDecodesFractionalUptime(t *testing.T) {
	const payload = `{"response":{"cpu":{"cores":8},"memory":{"total":8393605120,"free":7256100864,"used":1137504256},"uptime":47376.49,"timestamp":1788370226376,"users":{"statusCounts":{"ACTIVE":1,"DISABLED":0,"LIMITED":0,"EXPIRED":0},"totalUsers":1},"onlineStats":{"onlineNow":0,"lastDay":0,"lastWeek":0,"neverOnline":1},"nodes":{"totalOnline":0,"totalBytesLifetime":"0"}}}`

	var response GetStatsResponse
	require.NoError(t, response.Decode(jx.DecodeBytes([]byte(payload))))
	require.InDelta(t, 47376.49, response.Response.Uptime, 0.000001)
}
