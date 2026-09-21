package api

import "testing"

func TestPaginationHelperStopsAtKnownTotal(t *testing.T) {
	t.Parallel()

	pager := NewPaginationHelper(50)
	pager.SetTotal(100)
	if !pager.HasMore {
		t.Fatal("HasMore = false after first page, want true")
	}
	if !pager.NextPage() || pager.Offset != 50 {
		t.Fatalf("NextPage() = false or offset = %d, want true and 50", pager.Offset)
	}
	if pager.NextPage() {
		t.Fatal("NextPage() = true on the last page, want false")
	}
	if pager.HasMore {
		t.Fatal("HasMore = true after the last page, want false")
	}
}

func TestPaginationHelperHandlesEmptyResult(t *testing.T) {
	t.Parallel()

	pager := NewPaginationHelper(25)
	pager.SetTotal(0)
	if pager.HasMore {
		t.Fatal("HasMore = true for an empty result, want false")
	}
	if pager.NextPage() {
		t.Fatal("NextPage() = true for an empty result, want false")
	}
}

func TestPaginationHelperFirstPageRestoresNavigation(t *testing.T) {
	t.Parallel()

	pager := NewPaginationHelper(10)
	pager.SetTotal(30)
	if !pager.NextPage() {
		t.Fatal("first NextPage() = false, want true")
	}
	pager.FirstPage()
	if pager.Offset != 0 || !pager.HasMore {
		t.Fatalf("FirstPage() = offset %d, hasMore %v; want 0, true", pager.Offset, pager.HasMore)
	}
}
