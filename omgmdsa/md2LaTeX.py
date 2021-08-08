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

# Installed by pip
from errutils import erlogging
logger = erlogging.setup(lambda depth: sys._getframe(depth))

import tempfile
import shutil

class MagicDraw2LaTeX(object):
    
    ###  Putting these file contents here in this class, so there's only one file to pass around, this script.
    propsFileContent = \
"""project = {model}
output = {output}/{pkg}.tex
package = {pkg}
template = {template}
autoImage = 0
imageFormat = svg
"""
    xmlPropsFileContent = \
"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties>
      <entry key = "project">{model}</entry>
      <entry key = "output">{output}/{pkg}.tex</entry>
      <entry key = "package">{pkg}</entry>
      <entry key = "template">{template}</entry>
      <entry key = "autoImage">0</entry>
      <entry key = "imageFormat">svg</entry>
</properties>
"""
    
    def __init__(self, app, modelFile, packages=[], outputDir="", propsDir="", imageDir="", template="OMGPackage"):
        self.mdApp = app
        self.modelFile = modelFile
        self.packages = packages
        self.outputDir = outputDir
        self.propsDir = propsDir
        self.imageDir = imageDir
        self.template = template
        
        modelDir, modelFilename = os.path.split(self.modelFile)
        
        self.specName = os.path.splitext(modelFilename)[0]
        self.modelFile = os.path.realpath(self.modelFile)        

        # if modelDir == "":
        #     logger.debug("modelFile has no path, finding path")
        #     if os.path.exists(self.modelFile):
        #         self.modelFile =
        
        if self.outputDir == "":
            self.outputDir = os.path.join(os.path.dirname(self.modelFile), self.specName + "Submission", "GeneratedContent")
        else:
            self.outputDir = os.path.realpath(self.outputDir)
        
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
        
        if self.imageDir == "":
            self.imageDir = self.outputDir
        else:
            self.imageDir = os.path.realpath(self.imageDir)
        
        if not os.path.exists(self.imageDir):
            os.makedirs(self.imageDir)

        # if self.propsDir == "":
        #     self.propsDir = os.path.join(self.outputDir, "tmpProps")
        # if not os.path.exists(self.propsDir):
        #     os.makedirs(self.propsDir)
        
        self.noWrite = False
        
    
    def generate(self, xmlProps=False):
        propsFiles = []
        with tempfile.TemporaryDirectory() as tmpDir:
            
            for pkg in self.packages:
                if xmlProps:
                    ext = '.xml'
                    contents = MagicDraw2LaTeX.xmlPropsFileContent
                else:
                    ext = '.props'
                    contents = MagicDraw2LaTeX.propsFileContent
            
                propsFile = os.path.join(tmpDir, pkg + ext)
                propsFiles.append('"' + propsFile + '"')
            
                propFileContents = contents.format(model=self.modelFile, pkg=pkg, output=tmpDir, template=self.template)
                logger.debug(propsFile + ":\n" + propFileContents)
                if not self.noWrite:
                    with open(propsFile, encoding='ascii', mode='w') as pf:
                        pf.write(propFileContents)
        
            cmd = [self.mdApp, "-properties", ' '.join(propsFiles)]
            logger.debug(' '.join(cmd))
            if not self.noWrite:
                ## subprocess would be preferred here, but if it's run through subprocess, it fails in Java with 
                ## "Error: Malformed \uxxxx encoding." but this works.  *flips desk*
                os.system(' '.join(cmd))
                # subprocess.run(cmd)
            
            # Move the generated files
            imageTypes = ['.svg', '.pdf', '.jpg', '.png']
            propsTypes = ['.props', '.xml']
            for f in os.listdir(tmpDir):
                fPath = os.path.join(tmpDir, f)
                ext = os.path.splitext(f)[1]
                # print(fPath, os.path.isdir(fPath))
                if os.path.isdir(fPath) and f.endswith("_files"):
                    logger.debug("Skipping _files dir '{}'".format(f))
                    continue
                elif ext.lower() in propsTypes:
                    logger.debug("Skipping property file '{}'".format(f))
                    continue

                if ext.lower() == '.tex':
                    dest = os.path.join(self.outputDir, f)
                    with open(fPath, 'r') as texFile:
                        output = ""
                        for line in texFile:
                            cleanline = line
                            # Remove colons from fully qualified names
                            while "--FQN-" in cleanline:
                                start = cleanline.index("--FQN-")
                                end = cleanline.index("-FQN--", start)
                                pre = cleanline[:start]
                                fqn = cleanline[start+6:end]
                                post = cleanline[end+6:]
                                print (fqn)
                                cleanfqn = ''.join( c for c in fqn if c not in ':' )
                                print (cleanfqn)
                                cleanline = pre + cleanfqn + post
                            output += cleanline
                    # Replace file with new contents
                    os.remove(fPath)
                    with open(fPath, 'w') as texFile:
                        texFile.write(output)
                        
                elif ext.lower() in imageTypes:
                    dest = os.path.join(self.imageDir, f)
                else:
                    logger.warning("Unknown file type: '{}'".format(f))
                    continue
                logger.debug("Moving {} to {}".format(fPath, dest))
                shutil.move(fPath, dest)
    
         
    
        
        
def main():
    parser = argparse.ArgumentParser(description = 'Default python template')
    # Debugging and testing
    debugGroup = parser.add_argument_group('Debug', 'Commands to assist debugging')
    debugGroup.add_argument('--verbose', default=False, action='store_true')
    debugGroup.add_argument('--debug', default=False, action='store_true')
    debugGroup.add_argument('--test', default=False, action='store_true', help="Run unit tests")
    debugGroup.add_argument('--nowrite', default=False, action='store_true', help="Don't write files or run converter through MagicDraw")

    parser.add_argument('--app', default="generate.sh", metavar="APPPATH", help="Path of MagicDraw generate.sh script")
    parser.add_argument('--template', default="OMGPackage", metavar="TEMPLATE_NAME", help="Name of the report template registered in MagicDraw to use to generate LaTeX")
    parser.add_argument('--config', default="", metavar="CONFIGFILE", help="Read from INI style config file.  CLI options override config file.")
    parser.add_argument('--model', default="", metavar="MODELFILE", help="The MagicDraw model file to convert to LaTeX (may be .mdzip or .xml)")
    parser.add_argument('--pkgs', default="", nargs="*", metavar="PACKAGE", help="Add a package to the to-be-processed list")
    parser.add_argument('--texoutput', default="", metavar="DIR", help="Directory to place generated .tex files into.")
    parser.add_argument('--imgoutput', default="", metavar="DIR", help="Directory to place generated images into.")
    
    # parser.add_argument('--xml', default=False, action='store_true', help="Emit XML properties files for MagicDraw report generator")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(erlogging.INFO)
    if args.debug:
        logger.setLevel(erlogging.DEBUG)

    if args.config != "":
        config = configparser.ConfigParser()
        config.read(args.config)
        options = [ optName for (optName, val) in args._get_kwargs() ]
        for opt in options:
            args.__setattr__(opt, config.get('DEFAULT', opt, fallback=args.__getattribute__(opt)) )
    
    if args.model == "":
        logger.error("--model is a required flag, please provide a model file to convert")
        exit(0)
    
    if type(args.pkgs) == str:
        # Came from config file, need to convert to list
        args.pkgs = args.pkgs.split(' ')

    
    if args.test:
        unittest.main(argv=[os.path.basename(__file__)])
    else:
        converter = MagicDraw2LaTeX(app=args.app, modelFile=args.model, packages=args.pkgs, outputDir=args.texoutput, imageDir=args.imgoutput, template=args.template)
        converter.noWrite = args.nowrite
        converter.generate(xmlProps=True)



if __name__ == "__main__":
    main()