import json
import sys

def read_json_file(file_path, encoding='utf-8'):
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

def read_text_file(file_path, encoding='utf-8'):
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Error reading text file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

def save_json_file(data, file_path, encoding='utf-8'):
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
