#!/usr/bin/env python3

import argparse, redis, logging, sys


assert sys.version_info >= (3, 6), "This script requires Python 3.6 or higher"


def parse_args():
    parser = argparse.ArgumentParser(description="Check redis script")
    parser.add_argument("--warn", "-w", type=float, required=True, help="Warning level")
    parser.add_argument(
        "--crit", "-c", type=float, required=True, help="Critical level"
    )
    parser.add_argument(
        "-H",
        "--host",
        help="hostname and port of the Redis server, e.g. 127.0.1:6379, domain.com:6379",
        default="127.0.1:6379",
    )
    parser.add_argument("--password", "-P", help="Password")
    parser.add_argument(
        "--timeout", "-t", type=int, default=5, help="Connection timeout in seconds"
    )
    parser.add_argument("--metric", "-m", required=True, help="Metric to check")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    return args


def check_metric(stats, metric):
    if metric in stats:
        logging.debug(f"metric={metric}")
        value = stats[metric]
        logging.debug(f"value={value}")
        return value
    else:
        logging.info(f"Available metrics are {str(list(stats.keys()))}")
        sys.exit(1)


def check_threshold(value, args):
    state = f"{args.metric} is {value}"
    logging.debug(f"state={state}")
    if not isinstance(value, float):
        try:
            value = float(value)
        except Exception as ex:
            logging.debug(f"can't convert {value} to float")
            return ("CRITICAL", f"Error: can't convert {value} to float")
    if value >= args.warn and value < args.crit:
        logging.debug(f"WARNING - {state}")
        return ("WARNING", f"{state}")
    elif value >= args.crit:
        logging.debug(f"CRITICAL - {state}")
        return ("CRITICAL", f"{state}")
    elif value < args.warn:
        logging.debug(f"OK - {state}")
        return ("OK", f"{state}")
    elif value < args.crit:
        logging.debug(f"Value {value} is less than critical threshold {args.crit}")
        return (
            "CRITICAL",
            f"Value {value} is less than critical threshold {args.crit}",
        )
    else:
        logging.debug(f"UNKNOWN - {state}")
        return ("CRITICAL", f"{state}")


def main():
    args = parse_args()

    if args.debug:
        logging.basicConfig(
            format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s",
            stream=sys.stdout,
            level=logging.DEBUG,
        )
    else:
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=logging.INFO,
        )

    host = args.host.split(":")
    if len(host) == 2:
        host, port = host
    else:
        host = host[0]
        port = 6379
    logging.debug(f"host={host},port={port}")

    if args.password:
        client = redis.Redis(host=host, port=port, password=args.password)
    else:
        client = redis.Redis(host=host, port=port)

    stats = client.info()
    logging.debug(f"stats={stats}")
    value = check_metric(stats, args.metric)
    logging.debug(f"value={value}")
    check_threshold(value, args)
    status, message = check_threshold(value, args)
    logging.info(f"{status}: {message}")
    if status == "OK":
        sys.exit(0)
    elif status == "WARNING":
        sys.exit(1)
    elif status == "CRITICAL":
        sys.exit(2)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
