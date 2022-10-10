#!/usr/bin/python3 -W ignore
# -*- coding: utf-8 -*-

import sys
import requests
import argparse
import logging


logging.basicConfig(format='[%(asctime)s] %(levelname)s:%(name)s:%(message)s', datefmt='%X', level=logging.ERROR)
parser = argparse.ArgumentParser()
parser.add_argument("-H", "--host", help="Hostname or IP address of the node to check, e.g. 127.0.0.1, domain.com")
parser.add_argument("-v", "--verbose", help="Set verbosity level", action='count')
args = parser.parse_args()
if args.host is None:
    logging.error("Server is not set, exiting.")
    sys.exit(2)
if args.verbose:
    logger = logging.getLogger()
    levels = {
        0 : logging.ERROR,
        1 : logging.WARNING,
        2 : logging.INFO,
        3 : logging.DEBUG,
        }
    try:
        level = levels[args.verbose]
    except KeyError:
        level = logging.DEBUG
    logger.setLevel(level)
    logging.info('Setting logging level to %s', logging.getLevelName(level))

host=args.host

URL_prizmNodeState = 'https://'+host+':9976/prizm?requestType=getState&includeCounts=false&random=0.461040019'
try:
    response = requests.get(URL_prizmNodeState, verify=False, timeout=2)
except Exception as ex:
    logging.exception('Failed to get response from %s', URL_prizmNodeState)
    print("CRITICAL - %s" % str(ex))
    sys.exit(2)

try:
    result_host=response.json()
    blockchainState=result_host['blockchainState']
    numberOfBlocks=result_host['numberOfBlocks']
    logging.info('%s: blockchainState: %s', host, blockchainState)
    logging.info('%s: numberOfBlocks: %d', host, numberOfBlocks)
except Exception as ex:
    logging.exception('Failed to parse output from host %s', host)
    print('CRITICAL - %s', str(ex))
    sys.exit(2)

host_prizmApi = 'blockchain.prizm.space'
URL_prizmState = 'https://' + host_prizmApi + '/prizm?requestType=getState&includeCounts=false&random=0.461040019047640'
try:
    response = requests.get(URL_prizmState, verify=False)
except Exception as ex:
    logging.exception('Failed to get response from %s', URL_prizmNodeState)
    print("CRITICAL - " + host_prizmApi + str(ex))
    sys.exit(2)

try:
    result_api=response.json()
    apinumberOfBlocks=result_api['numberOfBlocks']
    logging.info('%s: numberOfBlocks: %d', host_prizmApi, numberOfBlocks)
except:
    logging.exception('Failed to parse output from host %s', host)
    print('CRITICAL - %s', str(ex))
    sys.exit(2)

DIFF=apinumberOfBlocks - numberOfBlocks

if apinumberOfBlocks > numberOfBlocks:
    logging.info('%s: lagging behind, diff is %d', host, DIFF)
    if blockchainState != 'UP_TO_DATE':
        if DIFF >= 20:
            print("CRITICAL - BlockState:" + str(blockchainState) + ", " + str(DIFF) + " blocks missed!")
            sys.exit(2)
        if DIFF >= 10 or DIFF < 19:
            print("WARNING - BlockState:" + str(blockchainState) + ", " + str(DIFF) + " blocks missed!")
            sys.exit(1)
    else:
        print("OK - BlockState:" + str(blockchainState) + ", " + str(DIFF) + " blocks missed!")
        sys.exit(0)
    logging.info('%s: blockchainState: %s', host, blockchainState)
else:
    logging.info('%s: diff is %d', host, DIFF)
    print("OK - " + str(DIFF) + " blocks missed")
    sys.exit(0)

