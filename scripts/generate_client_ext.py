#!/usr/bin/env python3
"""Generate the current ``api/client_ext.go`` wrapper.

The wrapper used to contain a second, incomplete generator for a historical
2.x specification. The version-aware pipeline is now the single source of
truth; this compatibility entry point delegates to its wrapper generator.

Usage:
    python3 scripts/generate_client_ext.py [spec.json]

By default the committed Remnawave 3.4.3 derived specification is used.
"""

from pathlib import Path
import sys

from pipeline import generate_client_ext


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = ROOT / "specs" / "3.4.3-final.json"


def main() -> int:
    spec_file = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SPEC
    if not spec_file.is_absolute():
        spec_file = Path.cwd() / spec_file

    if not spec_file.exists():
        print(f"Spec not found: {spec_file}", file=sys.stderr)
        return 1

    controllers, methods, _operation_ids = generate_client_ext(
        str(spec_file),
        str(ROOT / "api" / "oas_client_gen.go"),
        str(ROOT / "api" / "client_ext.go"),
    )
    print(f"Generated {methods} methods across {controllers} controllers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
