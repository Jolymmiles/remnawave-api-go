#!/usr/bin/env python3
"""Compatibility entry point for the current ``client_ext.go`` generator.

The old implementation was tied to a removed historical 2.x consolidated
file. Use the shared generator from ``pipeline.py`` so the wrapper stays aligned
with the Remnawave 3.4.3 OpenAPI document and the installed ogen version.

Usage:
    python3 scripts/generate_clientext_final.py [spec.json]
"""

import generate_client_ext


def main() -> int:
    return generate_client_ext.main()


if __name__ == "__main__":
    raise SystemExit(main())
