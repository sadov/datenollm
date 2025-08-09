# Utility: collab2gist - Remove metadata.widgets from JSON

## Description
This utility removes the `metadata.widgets` field from JSON data. Useful for converting Jupyter notebooks from Google Colab to properly displayed GitHub Gist format.

## Usage

### Method 1: CLI - Using pipe
```bash
cat input.json | dateno-collab2gist.py > output.json
```

### Method 2: CLI - Using input redirection
```bash
dateno-collab2gist.py < input.json > output.json
```

### Method 3: Using the function in code
```python
from datenollm.jupiter_nb import collab2gist
import json

# Load JSON data
with open('input.json', 'r') as f:
    data = json.load(f)

# Process data
processed_data = collab2gist(data)

# Save processed data
with open('output.json', 'w') as f:
    json.dump(processed_data, f, indent=2)
```

## Example

### Input JSON:
```json
{
  "name": "example",
  "metadata": {
    "widgets": {
      "some": "data"
    },
    "other": "info"
  },
  "content": "test"
}
```

### Output JSON:
```json
{
  "name": "example",
  "metadata": {
    "other": "info"
  },
  "content": "test"
}
```

## Features
- ✅ Reads JSON from stdin
- ✅ Removes `metadata.widgets` if it exists
- ✅ Removes empty `metadata` object if it becomes empty
- ✅ Writes formatted JSON to stdout
- ✅ Handles errors gracefully with proper exit codes
- ✅ Supports Unicode characters (ensure_ascii=False)

## Error Handling
- Invalid JSON input → Error message to stderr, exit code 1
- Other errors → Error message to stderr, exit code 1
