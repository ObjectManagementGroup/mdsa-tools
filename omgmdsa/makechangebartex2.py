#!/usr/bin/env python3
"""
Copyright Elemental Reasoning, LLC, 2019-2020
Copyright Object Management Group, 2021
All rights reserved unless otherwise specified in licensing agreement.
---------------"""

import sys
import os
import os.path
import argparse
import configparser
import unittest

from errutils import erlogging
logger = erlogging.setup(lambda depth: sys._getframe(depth))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Default python template')
    # Debugging and testing
    debugGroup = parser.add_argument_group('Debug', 'Commands to assist debugging')
    debugGroup.add_argument('--verbose', default=False, action='store_true')
    debugGroup.add_argument('--debug', default=False, action='store_true')
    debugGroup.add_argument('--test', default=False, action='store_true', help="Run unit tests")

    parser.add_argument('--config', default="", metavar="CONFIGFILE", help="Read from INI style config file.  CLI options override config file.")
    
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(erlogging.INFO)
    if args.debug:
        logger.setLevel(erlogging.DEBUG)

    if args.config != "":
        if os.path.exists(args.config):
            config = configparser.ConfigParser()
            config.read(args.config)
            options = [ optName for (optName, val) in args._get_kwargs() ]
            for opt in options:
                args.__setattr__(opt, config.get('DEFAULT', opt, fallback=args.__getattribute__(opt)) )
        else:
            logger.warning("No config file at: {}".format(args.config))
    
    if args.test:
        unittest.main(argv=[os.path.basename(__file__)])
    else:
        pass
        ### PUT RUNNER FOR CODE HERE
