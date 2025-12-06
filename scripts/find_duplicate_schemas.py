#!/usr/bin/env python3
"""
OpenAPI Schema Duplicate Finder

This script analyzes OpenAPI/Swagger JSON files to find duplicate or identical
request/response models (DTOs). Useful for identifying opportunities to consolidate
schemas and reduce API specification redundancy.

Usage:
    python3 find_duplicate_schemas.py <path_to_openapi.json>
    python3 find_duplicate_schemas.py api-2-2-2.json
    python3 find_duplicate_schemas.py api-2-2-0.json

Features:
    - Handles malformed JSON files by attempting salvage through truncation
    - Groups identical schemas together
    - Shows detailed analysis of each duplicate group
    - Outputs statistics and recommendations
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def find_schemas_section(content: str) -> tuple[str, int]:
    """
    Extract the schemas JSON object from OpenAPI file.
    
    Returns:
        Tuple of (schemas_json_string, end_position)
    """
    schemas_start = content.find('"schemas": {')
    if schemas_start < 0:
        raise ValueError('Could not find "schemas" section in JSON file')
    
    schemas_part = content[schemas_start + len('"schemas": '):]
    
    # Count braces to find the end of the schemas object
    brace_count = 0
    in_string = False
    escape = False
    end_pos = 0
    
    for i, char in enumerate(schemas_part):
        if escape:
            escape = False
            continue
        if char == '\\':
            escape = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break
    
    if end_pos == 0:
        raise ValueError('Could not find end of schemas section')
    
    schemas_json = schemas_part[:end_pos]
    return schemas_json, schemas_start + len('"schemas": ') + end_pos


def load_schemas(filepath: str) -> dict:
    """
    Load schemas from an OpenAPI JSON file.
    Attempts to handle malformed files by extracting only the schemas section.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    print(f"📂 Reading file: {filepath}", file=sys.stderr)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    file_size_mb = len(content) / (1024 * 1024)
    print(f"📊 File size: {file_size_mb:.2f} MB", file=sys.stderr)
    
    try:
        # Try parsing the entire file first
        spec = json.loads(content)
        schemas = spec.get('components', {}).get('schemas', {})
        print(f"✓ File parsed successfully (full JSON)", file=sys.stderr)
    except json.JSONDecodeError:
        print(f"⚠ Full JSON parse failed, attempting schema extraction...", file=sys.stderr)
        
        try:
            schemas_json, _ = find_schemas_section(content)
            wrapped = '{"schemas": ' + schemas_json + '}'
            data = json.loads(wrapped)
            schemas = data['schemas']
            print(f"✓ Schemas extracted successfully (partial extraction)", file=sys.stderr)
        except (ValueError, json.JSONDecodeError) as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    return schemas


def find_duplicates(schemas: dict) -> tuple[dict, list]:
    """
    Find duplicate/identical schemas.
    
    Returns:
        Tuple of (schema_groups_dict, sorted_duplicates_list)
    """
    schema_groups = defaultdict(list)
    
    for name, schema_def in schemas.items():
        # Convert schema to JSON string for comparison
        key = json.dumps(schema_def, sort_keys=True, default=str)
        schema_groups[key].append(name)
    
    # Extract duplicates (groups with more than one schema)
    duplicates = sorted(
        [(v, k) for k, v in schema_groups.items() if len(v) > 1],
        key=lambda x: len(x[0]),
        reverse=True
    )
    
    return schema_groups, duplicates


def print_summary(schemas: dict, schema_groups: dict, duplicates: list) -> None:
    """Print summary statistics."""
    print("\n" + "=" * 130)
    print("📈 SUMMARY STATISTICS")
    print("=" * 130)
    print(f"Total schemas:        {len(schemas)}")
    print(f"Unique definitions:   {len(schema_groups)}")
    print(f"Duplicate groups:     {len(duplicates)}")
    print(f"Redundant schemas:    {len(schemas) - len(schema_groups)}")
    print("=" * 130 + "\n")


def print_duplicates(duplicates: list, max_groups: int = None) -> None:
    """Print detailed information about each duplicate group."""
    if not duplicates:
        print("✓ No duplicate schemas found - all schemas are unique!")
        return
    
    print("=" * 130)
    print("🔍 DUPLICATE SCHEMAS FOUND:")
    print("=" * 130)
    
    for idx, (names, schema_json) in enumerate(duplicates[:max_groups] if max_groups else duplicates, 1):
        schema_def = json.loads(schema_json)
        
        print(f"\n[GROUP {idx}] {len(names)} IDENTICAL MODELS")
        print(f"Models: {', '.join(sorted(names))}")
        
        # Show schema structure details
        print(f"\nSchema Type Details:")
        if schema_def.get('type') == 'object':
            if 'properties' in schema_def:
                props = list(schema_def['properties'].keys())
                print(f"  • Object with {len(props)} properties")
                print(f"  • Fields: {props[:8]}", end='')
                if len(props) > 8:
                    print(f" ... (+{len(props)-8} more)")
                else:
                    print()
            if 'required' in schema_def:
                print(f"  • Required: {schema_def['required']}")
        elif '$ref' in schema_def:
            print(f"  • Reference: {schema_def['$ref']}")
        else:
            print(f"  • Type: {schema_def.get('type', 'unknown')}")
        
        # Show schema definition preview
        schema_preview = json.dumps(schema_def, indent=2)
        lines = schema_preview.split('\n')[:12]
        print(f"\nSchema Definition (preview):")
        for line in lines:
            print(f"  {line}")
        if len(schema_preview.split('\n')) > 12:
            print(f"  ... ({len(schema_preview.split('\n')) - 12} more lines)")
        
        print("-" * 130)


def print_recommendations(duplicates: list) -> None:
    """Print consolidation recommendations."""
    if not duplicates:
        return
    
    print("\n" + "=" * 130)
    print("💡 CONSOLIDATION RECOMMENDATIONS")
    print("=" * 130)
    
    # Categorize by group size
    large_groups = [d for d in duplicates if len(d[0]) >= 5]
    medium_groups = [d for d in duplicates if 3 <= len(d[0]) < 5]
    small_groups = [d for d in duplicates if len(d[0]) == 2]
    
    if large_groups:
        print(f"\n🔴 HIGH PRIORITY (5+ duplicates):")
        for names, _ in large_groups:
            print(f"   • {len(names)} models can be consolidated: {names[0]}* (and {len(names)-1} others)")
    
    if medium_groups:
        print(f"\n🟡 MEDIUM PRIORITY (3-4 duplicates):")
        for names, _ in medium_groups:
            print(f"   • {len(names)} models: {', '.join(names[:2])}...")
    
    if small_groups:
        print(f"\n🟢 LOW PRIORITY (2 duplicates):")
        total_pairs = len(small_groups)
        print(f"   • {total_pairs} pairs of duplicate schemas")
    
    print("\n" + "=" * 130)


def print_grouped_by_pattern(duplicates: list) -> None:
    """Print duplicates grouped by response pattern."""
    if not duplicates:
        return
    
    print("\n" + "=" * 130)
    print("🎯 PATTERNS IDENTIFIED")
    print("=" * 130)
    
    patterns = {
        "Delete Operations": [],
        "Empty Wrapper": [],
        "Event Based": [],
        "Bulk Operations": [],
        "Token Responses": [],
        "List Responses": [],
        "Other": []
    }
    
    for names, schema_json in duplicates:
        schema_def = json.loads(schema_json)
        
        # Categorize by pattern
        if isinstance(schema_def.get('properties', {}).get('response'), dict):
            resp = schema_def['properties']['response']
            if resp.get('properties', {}).get('isDeleted'):
                patterns["Delete Operations"].append((len(names), names))
            elif resp.get('properties', {}).get('eventSent'):
                patterns["Event Based"].append((len(names), names))
            elif resp.get('properties', {}).get('affectedRows'):
                patterns["Bulk Operations"].append((len(names), names))
            elif resp.get('properties', {}).get('accessToken'):
                patterns["Token Responses"].append((len(names), names))
            elif not resp.get('properties'):
                patterns["Empty Wrapper"].append((len(names), names))
            elif isinstance(resp.get('items'), dict):
                patterns["List Responses"].append((len(names), names))
            else:
                patterns["Other"].append((len(names), names))
        else:
            patterns["Other"].append((len(names), names))
    
    for pattern_name, items in patterns.items():
        if items:
            total_models = sum(count for count, _ in items)
            print(f"\n{pattern_name}: {total_models} total models across {len(items)} groups")
            for count, names in sorted(items, key=lambda x: x[0], reverse=True):
                print(f"   [{count}] {', '.join(names[:3])}{'...' if len(names) > 3 else ''}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 find_duplicate_schemas.py <openapi_file.json>", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  python3 find_duplicate_schemas.py api-2-2-2.json", file=sys.stderr)
        print("  python3 find_duplicate_schemas.py openapi.json", file=sys.stderr)
        sys.exit(1)
    
    filepath = sys.argv[1]
    max_groups = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    try:
        # Load schemas
        schemas = load_schemas(filepath)
        
        # Find duplicates
        schema_groups, duplicates = find_duplicates(schemas)
        
        # Print results
        print_summary(schemas, schema_groups, duplicates)
        print_duplicates(duplicates, max_groups)
        print_recommendations(duplicates)
        print_grouped_by_pattern(duplicates)
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
