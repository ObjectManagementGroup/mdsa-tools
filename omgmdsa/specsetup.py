#!/usr/bin/env python3
import os
import sys
import argparse
import configparser
import datetime

from errutils import erlogging
# erlogging.preSetupEmailFromConfig('omgEmailSetup.config')
logger = erlogging.setup(lambda depth: sys._getframe(depth))
# Set ER_EMAIL_CONFIG to path to omgPlanningTeamEmailSetup.config

class SpecSetup:
    """Container for specification details that could potentially be managed by a central database. Currently they are defined in Specification_Setup.tex"""
    def __init__(self):
        self.fields = ['specacro', 'specname', 'version', 'subtitle', 'docnum', 'subdate']
        for field in self.fields:
            self.__dict__[field] = "NOTSET"
    
    def get(self, field):
        return self.__dict__[field]

    def copyTo(self, target):
        for field in self.fields:
            target.__dict__[field] = self.__dict__[field]

class LaTeXFileSpecSetup (SpecSetup):
    """A setup that is parsed from or written to a LaTeX file."""
    def __init__(self, setupFile=""):
        super().__init__()
        if setupFile == "":
            return
        with open(setupFile) as setup:
            for line in setup:
                if not line.strip().startswith('%'):
                    for field in self.fields:
                        if ('\\' + field) in line:
                            value = line.strip().split('{\\' + field + '}{')[1].split('}')[0]
                            if not value.startswith("\\REPLACEME"):
                                self.__dict__[field] = value

    def write(self, setupFile):
        with open(setupFile, 'w') as setup:
            setup.write("%%%%\n")
            setup.write("%%\n")
            setup.write("%% OMG Specification Setup for OMG MDSA - LaTeX\n")
            setup.write("%%\n")
            setup.write("%% Generated: " + str(datetime.datetime.now(datetime.timezone.utc)) + "\n")
            setup.write("%%\n")
            setup.write("%%%%\n")
            setup.write("\n")
            for field in self.fields:
                setup.write("\\setvalue\\{" + field + "}{" + self.__dict__[field] + "}\n")
        
class DBSpecSetup(SpecSetup):
    """A SpecSetup that is read from or written to a database"""
    def __init__(self, host="", port=""):
        super().__init__()
        print ("DBSpecSetup not yet implemented")
    
    def write(self, host, port):
        print ("DBSpecSetup not yet implemented")
    
def main():
    parser = argparse.ArgumentParser(description='Test script to exercise SpecSetup subclasses for LaTeX files and DB storage')
    # Debugging and testing
    debugGroup = parser.add_argument_group('Debug', 'Commands to assist debugging')
    debugGroup.add_argument('--verbose', default=False, action='store_true')
    debugGroup.add_argument('--debug', default=False, action='store_true')
    debugGroup.add_argument('--test', default=False, action='store_true')
    parser.add_argument("--setupFile", default="")
    parser.add_argument("--host", default="")
    parser.add_argument("--port", default="")
    parser.add_argument("--lookup", default="")
    
    args = parser.parse_args()

    if args.setupFile == "" and args.host == "" and args.port == "":
        print("Error, must provide either --setupFile or --host / --port")
        exit(-1)

    if args.test:
        print ("Reading LaTeX file for data")    
        setup = LaTeXFileSpecSetup(args.setupFile)
        print ("specacro = " + setup.specacro)
        print (setup.__dict__)

        print ("Creating DBSpecSetup - UNIMPLEMENTED")
        setup2 = DBSpecSetup(args.host, args.port)

        print ("Copying parsed LaTeX setup to empty DBSpecSetup")
        setup.copyTo(setup2)
        print ("Writing to DB - UNIMPLEMENTED")
        setup2.write(args.host, args.port)
        print(setup.__dict__)

        print ("Copying parsed LaTeX setup to another LaTeX setup, then writing to 'foo.txt'")
        setup3 = LaTeXFileSpecSetup()
        setup.copyTo(setup3)
        setup3.write("foo.txt")

    setup = None 

    if args.setupFile != "":
        setup = LaTeXFileSpecSetup(args.setupFile)
    else:
        setup = DBSpecSetup(args.host, args.port)
    
    if args.lookup != "":
        print(setup.get(args.lookup))
        exit(0)
    

if __name__ == '__main__':
    main()
