#!/usr/bin/env python3

import argparse, sys, os

assert sys.version_info >= (3, 6), "This script requires Python 3.6 or higher"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mountpoint",
        type=str,
        action="append",
        required=True,
        help="Specify a mountpoint to check. This option can be specified multiple times to check multiple mountpoints, e.g. -m /home --mountpoint /mnt -m /",
    )
    args = parser.parse_args()

    return args


def main():
    args = parse_args()
    mountpoint = args.mountpoint
    status_ok = ""
    status_critical = ""

    for element in mountpoint:
        if os.path.ismount(element):
            status_ok += f"{element} is mounted "
        else:
            status_critical += f"{element} is not mounted "
    if len(status_critical) == 0:
        print(f"OK - {status_ok}")
        sys.exit(0)
    else:
        print(f"CRITICAL - {status_critical} {status_ok}")
        sys.exit(1)


if __name__ == "__main__":
    main()
