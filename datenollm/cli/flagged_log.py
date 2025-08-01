#!/usr/bin/env python3

import sys
from langchain.schema import AIMessage, HumanMessage

from datenollm.client import read_flagged_log_csv

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <flagged_log_csv_file>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        messages = read_flagged_log_csv(file_path)
        for i, msg in enumerate(messages):
            if isinstance(msg, HumanMessage):
                print('====================================')
                print(f"Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                print('------------------------------------')
                print(f"AI: {msg.content}")
                # Print all options if present
                if hasattr(msg, 'additional_kwargs') and msg.additional_kwargs:
                    print(f"Options: {msg.additional_kwargs}")
            else:
                print(f"Message: {getattr(msg, 'content', str(msg))}")
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
