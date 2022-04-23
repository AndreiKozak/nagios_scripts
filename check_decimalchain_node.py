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
    parser.add_argument("-t", "--delta", "--delay", type=int, help="Time Delay (Delta) between server's time and latest block time.")
    args = parser.parse_args()
    if args.host is None:
        print ("Server is not set, exiting.")
        sys.exit(2)
    if args.delta is None:
        args.delta = 30
    return args

def get_status(host):
    try:
        status = requests.get("http://" + host + "/status", timeout=5)
    except Exception as ex:
        print("CRITICAL - " + str(ex))
        sys.exit(2)

    return status.json()

def get_netinfo(host):
    try:
        netinfo = requests.get("http://" + host + "/net_info", timeout=5)
    except Exception as ex:
        print("CRITICAL - " + str(ex))
        sys.exit(2)

    return netinfo.json()

def main():
    args = parse_args()
    status = get_status(args.host)
    netinfo = get_netinfo(args.host)
    delay = args.delta

    npeers=int(netinfo['result']['n_peers'])
    latest_block_time=dateutil.parser.parse(datetime.strftime(dateutil.parser.parse(status['result']['sync_info']['latest_block_time']), '%Y-%m-%dT%H:%M:%S'))
    latest_block_height=status['result']['sync_info']['latest_block_height']
    now = datetime.utcnow().replace(microsecond=0)
    delta = now - latest_block_time
    state=f'Latest block: {latest_block_height}, Latest block time: {latest_block_time}, delta: {delta}, Peers connected: {npeers}'

    if npeers <= 3:
        print("CRITICAL - Status: " + state)
        sys.exit(2)
    elif delta.seconds >= delay:
        print("CRITICAL - Status: Delta is too big!," + state)
        sys.exit(2)
    elif delta.seconds < delay:
        print("OK - Status: " + state)
        sys.exit(0)
    else:
        print("CRITICAL - Status: " + state)
        sys.exit(2)

if __name__ == '__main__':
    main()
