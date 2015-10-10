#!/usr/bin/env python
import logging
import argparse

from messor.log import setup_logging
from messor.forager.pick_up import pick_up

def main():
    pick_up()

if __name__ == '__main__': 
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=level)

    main()
