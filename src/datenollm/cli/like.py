#!/usr/bin/env python3

import json
import argparse
import sys

from datenollm.client import DatenoClient, get_conversation_from_csv

def main():
    parser = argparse.ArgumentParser(description='Flag logs in the app')
    parser.add_argument('addr', type=str, help='URL or Hugging Face space name')
    parser.add_argument('index', type=int, help='Index of the log entry')
    parser.add_argument('flag', type=str, help='Flag to mark the log entry (like/dislike)')
    parser.add_argument('csv_path', type=str, help='Path to the flagged_log CSV file')
    args = parser.parse_args()

    if args.flag.lower() == 'like':
        flag = True
    elif args.flag.lower() == 'dislike':
        flag = False
    else:
        print("Invalid flag. Use 'like' or 'dislike'.", file=sys.stderr)
        sys.exit(1)

    index, conversation = get_conversation_from_csv(args.csv_path, args.index)
    if conversation is None:
        print(f"Conversation with index {args.index} not found in {args.csv_path}", file=sys.stderr)
        sys.exit(1)

    client = DatenoClient(args.addr)
    result = client.like(index, conversation, flag)

if __name__ == "__main__":
    main()
