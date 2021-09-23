#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import requests
import argparse
from datetime import datetime
import dateutil.parser

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", help="Hostname or IP address of the node to check, e.g. 127.0.0.1:8841, domain.com:1234")
    args = parser.parse_args()
    if args.host is None:
        print ("Server is not set, exiting.")
        sys.exit(2)
    return args

def get_status(host):
    try:
        status = requests.get("http://" + host + "/status", timeout=5)
    except Exception as ex:
        print("CRITICAL - " + str(ex))
        sys.exit(2)
    return status.json()

def main():
    args = parse_args()
    status = get_status(args.host)

    latest_block_time=dateutil.parser.parse(datetime.strftime(dateutil.parser.parse(status['result']['sync_info']['latest_block_time']), '%Y-%m-%dT%H:%M:%S'))
    latest_block_height=status['result']['sync_info']['latest_block_height']
    catching_up=status['result']['sync_info']['catching_up']
    now = datetime.utcnow()
    delta = now - latest_block_time
    state=f'Is catching up: {catching_up}, Latest block: {latest_block_height}, Latest block time: {latest_block_time}, delta: {delta}'

    if delta.seconds >= 30:
        print("CRITICAL - Status: Delta is too big!, " + state)
        sys.exit(2)
    elif catching_up == False:
        print("OK - Status: " + state)
        sys.exit(0)
    else:
        print("CRITICAL - Status: " + state)
        sys.exit(2)

if __name__ == '__main__':
    main()
