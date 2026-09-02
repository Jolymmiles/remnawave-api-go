package api

import (
	"testing"

	"github.com/go-faster/jx"
	"github.com/stretchr/testify/require"
)

func TestStatDecodesFractionalUptime(t *testing.T) {
	const payload = `{"memoryFree":3015061504,"memoryUsed":1097887744,"uptime":112669.97,"loadAvg":[0.47,0.26,0.15],"interface":null}`

	var stats Stat
	require.NoError(t, stats.Decode(jx.DecodeBytes([]byte(payload))))
	require.InDelta(t, 112669.97, stats.Uptime, 0.000001)
}
