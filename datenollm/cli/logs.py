#!/usr/bin/env python3

import argparse

from datenollm.client import DatenoClient

def main():
    parser = argparse.ArgumentParser(description='Download logs from the app')
    parser.add_argument('addr',
                        help='Client address (e.g. http://127.0.0.1:7861/ or hf_space)')
    args = parser.parse_args()
    
    client = DatenoClient(args.addr)
    result = client.get_logs()

    print(result)

if __name__ == "__main__":
    main()
