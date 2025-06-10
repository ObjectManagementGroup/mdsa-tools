#!/usr/bin/env python3
import os
import sys
import argparse
import configparser

from errutils import erlogging
# erlogging.preSetupEmailFromConfig('omgEmailSetup.config')
logger = erlogging.setup(lambda depth: sys._getframe(depth))
# Set ER_EMAIL_CONFIG to path to omgPlanningTeamEmailSetup.config

class SpecSetup:
    def __init__(self): #, *args, **kwargs):
        self.fields = ['specacro', 'specname', 'version', 'subtitle', 'docnum', 'subdate']
        for field in self.fields:
            self.__dict__[field] = "NOT SET"
    
    def get(self, field):
        return self.__getitem__(field)

class LaTeXFileSpecSetup (SpecSetup):
    def __init__(self, setupFile):
        super().__init__()
        with open(setupFile) as setup:
            for line in setup:
                if not line.strip().startswith('%'):
                    for field in self.fields:
                        if ('\\' + field) in line:
                            value = line.strip().split('{\\' + field + '}{')[1][:-1]
                            if not value.startswith("\\REPLACEME"):
                                self.__dict__[field] = value

class DBSpecSetup(SpecSetup):
    def __init__(self, host, port):
        self.super().__init__()
        print ("DB Spec Setup not yet implemented")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    # Debugging and testing
    debugGroup = parser.add_argument_group('Debug', 'Commands to assist debugging')
    debugGroup.add_argument('--verbose', default=False, action='store_true')
    debugGroup.add_argument('--debug', default=False, action='store_true')
    parser.add_argument("--setupFile", default="")
    parser.add_argument("--host", default="")
    parser.add_argument("--port", default="")
    
    args = parser.parse_args()

    if args.setupFile == "" and args.host == "" and args.port == "":
        print("Error, must provide either --setupFile or --host / --port")
        exit(-1)
    
    setup = LaTeXFileSpecSetup(args.setupFile) # if args.setupFile != "" else DBSpecSetup(args.host, args.port)
    # print (setup.get(args.field))
    print (setup.specacro)
    print (setup.__dict__)
