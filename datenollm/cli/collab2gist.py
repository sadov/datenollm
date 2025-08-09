#!/usr/bin/env python3
"""
CLI utility that reads JSON from stdin, removes metadata.widgets and writes to stdout.
Useful for converting Jupyter notebooks from Google Colab to properly displayed GitHub Gist format.

Usage:
    cat input.json | python collab2gist.py > output.json
    python collab2gist.py < input.json > output.json
"""

import json
import sys
from datenollm.jupiter_nb import collab2gist


def main():
    """
    CLI function that reads JSON from stdin, processes it with collab2gist and writes to stdout
    """
    try:
        # Read JSON from stdin
        json_data = sys.stdin.read()
        
        # Parse JSON
        data = json.loads(json_data)
        
        # Process data using collab2gist function
        processed_data = collab2gist(data)
        
        # Write processed JSON to stdout
        json.dump(processed_data, sys.stdout, indent=2, ensure_ascii=False)
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
