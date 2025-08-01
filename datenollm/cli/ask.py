#!/usr/bin/env python3

import argparse

from datenollm.client import DatenoClient

def main():
    parser = argparse.ArgumentParser(
        description='Generate structured queries for Dateno from user input using LLM')
    parser.add_argument('addr',
                        help='Client address (e.g. http://127.0.0.1:7861/)')
    parser.add_argument('query', help='Initial user request')
    parser.add_argument('--history', type=str, required=False, default=None,
                        help='Path to file containing dialog history in JSON format')
    parser.add_argument('--prompt', type=str, required=False, default=None,
                        help='Path to file containing system prompt')
    parser.add_argument('--model', type=str, required=False, default=None,
                        help='LLM model identifier')
    parser.add_argument('--max-tokens', type=int, required=False, default=None,
                        help='Maximum number of tokens in response')
    parser.add_argument('--temperature', type=float, required=False,
                        default=None, help='Generation temperature')
    parser.add_argument('--top-p', type=float, required=False,
                        default=None, help='Nucleus sampling parameter')
    
    args = parser.parse_args()

    client = DatenoClient(args.addr)
    result = client.ask(args.query, args.history, args.prompt, args.model,
                        args.max_tokens, args.temperature, args.top_p)

    print(result)

if __name__ == "__main__":
    main()
