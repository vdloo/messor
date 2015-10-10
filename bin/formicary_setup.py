#!/usr/bin/env python
from messor.log import setup_logging
from messor.formicary import setup_formicary

def main():
    setup_logging()
    setup_formicary()

if __name__ == '__main__':
    main()
