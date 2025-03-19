#!/usr/bin/env python3

import argparse, sys, requests, logging

assert sys.version_info >= (3, 6), "This script requires Python 3.6 or higher"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-H",
        "--host",
        default="127.1:8090",
        help="Hostname or IP address of the node to check, e.g. 127.0.0.1:8090, domain.com:8080, default value is 127.1:8090",
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


def get_status(host):
    try:
        status = requests.get(f"http://{host}/wallet/getnodeinfo", timeout=3)
    except Exception as ex:
        logging.info(f"CRITICAL - {ex}")
        sys.exit(2)

    return status.json()


def get_upstream_status():
    # https://tronprotocol.github.io/documentation-en/developers/official-public-nodes/
    node = "18.139.193.235:8090"
    try:
        upstream_status = requests.get(f"http://{node}/wallet/getnodeinfo", timeout=8)
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
    upstream_block = int(upstream_status["block"].split(",")[0].split(":")[1])
    logging.debug(f"upstream_block:{upstream_block}")
    status = get_status(host)
    logging.debug(f"status:{status}")
    block = int(status["block"].split(",")[0].split(":")[1])
    logging.debug(f"block:{block}")
    peers = status["peerList"]
    logging.debug(f"peers:{peers}")
    npeers = 0
    for peer in peers:
        if peer["active"]:
            npeers += 1
    logging.debug(f"peer:{peer}")
    delay = upstream_block - block
    state = f"Current block: {block}, Upstream block: {upstream_block}"
    npeers_state = f"Only {npeers} peers connected! "

    if delay >= delta:
        logging.info(f"CRITICAL - delta is {delay} blocks. {state}")
        sys.exit(2)
    elif npeers < args.peers:
        logging.info(f"CRITICAL - {npeers_state}, {state}")
        sys.exit(2)
    elif delay < delta:
        logging.info(f"OK - {state}, Delta: {delay}")
        sys.exit(0)
    else:
        logging.info(f"CRITICAL - {state}")
        sys.exit(2)


if __name__ == "__main__":
    main()
