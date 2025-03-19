#!/usr/bin/env python3

import argparse, sys, requests, logging

assert sys.version_info >= (3, 6), "This script requires Python 3.6 or higher"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-H",
        "--host",
        default="127.1:28081",
        help="Hostname or IP address of the node to check, e.g. 127.0.0.1:28081, domain.com:28081, default value is 127.1:28081",
    )
    parser.add_argument(
        "-t",
        "--delta",
        "--delay",
        type=int,
        default=5,
        help="Delta between upstream block and current block, default value is 5 sec",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    return args


payload = {"jsonrpc": "2.0", "id": "0", "method": "get_block_count"}
headers = {"Content-Type": "application/json"}


def get_status(host):
    url = f"http://{host}/json_rpc"
    try:
        status = requests.get(url, json=payload, headers=headers, timeout=3)

    except Exception as ex:
        logging.info(f"CRITICAL - {ex}")
        sys.exit(2)

    return status.json()


def get_upstream_status():
    # https://xmr.ditatompel.com/remote-nodes
    url = "http://testnet.xmr-tw.org:28081/json_rpc"
    try:
        upstream_status = requests.get(url, json=payload, headers=headers, timeout=3)
    except Exception as ex:
        logging.info(f"CRITICAL - {ex}")
        sys.exit(2)

    return upstream_status.json()


def main():
    args = parse_args()

    if args.debug:
        logging.basicConfig(
            format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s",
            level=logging.DEBUG,
        )
    else:
        logging.basicConfig(
            format="%(message)s",
            level=logging.INFO,
        )

    host = args.host
    delta = args.delta
    upstream_status = get_upstream_status()
    logging.debug(upstream_status)
    upstream_block = int(upstream_status["result"]["count"])
    logging.debug(f"upstream_block:{upstream_block}")
    status = get_status(host)
    logging.debug(f"status:{status}")
    block = int(upstream_status["result"]["count"])
    logging.debug(f"block:{block}")
    delay = upstream_block - block
    state = f"Current block: {block}, Upstream block: {upstream_block}"

    if delay >= delta:
        logging.info(f"CRITICAL - delta is {delay} blocks. {state}")
        sys.exit(2)
    elif delay < delta:
        logging.info(f"OK - {state}, Delta: {delay}")
        sys.exit(0)
    else:
        logging.info(f"CRITICAL - {state}")
        sys.exit(2)


if __name__ == "__main__":
    main()
