#!/usr/bin/env python3

import argparse, sys, requests, logging

assert sys.version_info >= (3, 6), "This script requires Python 3.6 or higher"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-H",
        "--host",
        default="127.1:8545",
        help="Hostname or IP address of the node to check, e.g. 127.0.0.1:8545, domain.com:8080, default value is 127.1:8545",
    )

    parser.add_argument(
        "-U",
        "--upstream",
        default="https://bsc-dataseed2.binance.org",
        help="Hostname or IP address of the upstream node to check against, e.g. 127.0.0.1:8545, domain.com:8080, default value is https://bsc-dataseed2.binance.org",
    )

    parser.add_argument(
        "-t",
        "--delta",
        "--delay",
        type=int,
        default=5,
        help="Delta between upstream block and current block, default value is 5 sec",
    )

    parser.add_argument(
        "-p",
        "--peers",
        type=int,
        default=3,
        help="Minimal amount of connected peers, default value is 3",
    )

    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    return args


def get_status(host, command):
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"
    try:
        status = requests.post(
            f"{host}",
            headers={"Content-Type": "application/json"},
            json={"jsonrpc": "2.0", "method": command, "params": [], "id": 56},
            timeout=3,
        )
    except Exception as ex:
        logging.info(f"CRITICAL - {ex}")
        sys.exit(2)

    return status.json()


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
    upstream_host = args.upstream
    delta = args.delta
    is_catching_up = get_status(host, "eth_syncing")["result"]
    logging.debug(f"is_catching_up:{is_catching_up}")
    upstream_is_catching_up = get_status(upstream_host, "eth_syncing")["result"]
    logging.debug(f"upstream_is_catching_up:{upstream_is_catching_up}")
    peers = int(get_status(host, "net_peerCount")["result"], 16)
    logging.debug(f"peers:{peers}")
    block = int(get_status(host, "eth_blockNumber")["result"], 16)
    logging.debug(f"block:{block}")
    upstream_block = int(get_status(upstream_host, "eth_blockNumber")["result"], 16)
    logging.debug(f"upstream_block:{upstream_block}")
    delay = upstream_block - block
    state = f"Current block: {block}, Upstream block: {upstream_block}"
    peers_state = f"Only {peers} peers connected! "

    if delay >= delta:
        logging.info(f"CRITICAL - delta is {delay} blocks. {state}")
        sys.exit(2)
    elif peers < args.peers:
        logging.info(f"CRITICAL - {peers_state}, {state}")
        sys.exit(2)
    elif delay < delta:
        logging.info(f"OK - {state}, Delta: {delay}")
        sys.exit(0)
    elif is_catching_up != False:
        logging.info(
            f"CRITICAL - Node is catching up: {is_catching_up}, current block: {block}, upstream block: {upstream_block}, Delta: {delay}"
        )
    else:
        logging.info(f"CRITICAL - {state}")
        sys.exit(2)


if __name__ == "__main__":
    main()
