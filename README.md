OMG MDSA - TOOLS
================
Collection of tools to produce OMG specification process related documents in LaTeX directly from models created in modeling tools.

This is an example of what OMG terms Model-Driven Specification Authoring (MDSA).  The expectation is that this toolkit will grow to incorporate any modeling tool that users or vendors wish to bring into the OMG MDSA environment.  

The LaTeX document rendering system gives us a common platform that produces professional results, a text-based system that works well with version control, and gives us the ability to alleviate our authors from the burden of document formatting, letting them focus on the technical aspects of the specifications.

Primary deployment platform is assumed to be a Unix variant (Linux, macOS, etc) but may work on Windows with proper configuration.

There are currently two tools:

* `md2LaTeX.py`

  Converts documentation strings from a MagicDraw created model file into a LaTeX document set suitable for inclusion in an OMG document. Extensively uses the OMG LaTeX macros.

* `makechangebartex.py`

  Takes any two LaTeX documents and creates a changebar version appropriate for submittal for OMG review. Can also take as input two revisions in a git repository. 
  
  Has two helper tools:

	* `removeomgmarkup.pl`
	
	  Removes OMG specific markup where it may interfere with latexdiff or other LaTeX parsing tools.  Used by `makechangebartex.py`.
	  
	* `replaceUserfiles.py`
	
	  May be needed in some situations. Fixes up file path macros used by OMG system. Not for regular expected use.


To Install
==========
1. Clone this repository from github: `git clone https://github.com/ObjectManagementGroup/MDSATools.git`
2. Install contents of `./MDSATools/md2LaTeX-templates/` folder into MagicDraw as Report templates as per MagicDraw documentation for ReportWizard

If you want to install most simply, `cd MDSATools; python setup.py` and it will take care of the dependencies, and create a proper executable wrapper around each of the tools for you.

If you want to evoke the scripts more manually, you will need to install two modules into Python: click, and errutils.  Click is available via pip, and errutils can be obtained from https://github.com/jasonmccsmith/errutils .

Of course, these tools are of little use without at least one supported modeling tool, and a recent LaTeX installation for producing a changebar version.

Requirements
------------

* Python3
* Perl5
* Installed by pip install: errutils, click

md2LaTeX

* *MagicDraw*

	Supported for MagicDraw 19 and newer, but it may work with the 18.x versions.

makechangebartex.py

* *latexdiff*

	Bundled with every major LaTeX distro, requires version 1.3.1 or newer. (`latexdiff --version` to confirm on your system)


md2LaTeX
============

To Configure
------------

To use `md2LaTeX` to produce OMG specification process documents, you need to specify what MagicDraw file it needs to process, what packages it should process, and where the output should go.


	usage: md2LaTeX.py [-h] [--verbose] [--debug] [--test] [--nowrite]
	                   [--app APPPATH] [--template TEMPLATE_NAME]
	                   [--config CONFIGFILE] [--model MODELFILE]
	                   [--pkgs [PACKAGE [PACKAGE ...]]] [--texoutput DIR]
	                   [--imgoutput DIR]

	optional arguments:
	  -h, --help            show this help message and exit
	  --app APPPATH         Path of MagicDraw generate.sh script
	  --template TEMPLATE_NAME
	                        Name of the report template registered in MagicDraw to
	                        use to generate LaTeX
	  --config CONFIGFILE   Read from INI style config file. CLI options override
	                        config file.
	  --model MODELFILE     The MagicDraw model file to convert to LaTeX (may be
	                        .mdzip or .xml)
	  --pkgs [PACKAGE [PACKAGE ...]]
	                        Add a package to the to-be-processed list
	  --texoutput DIR       Directory to place generated .tex files into.
	  --imgoutput DIR       Directory to place generated images into.

The simplest way to use `md2LaTeX` is to create an INI style config file and add it to your version control for the document you are producing. Note that `--template` is not required for normal operation, but is useful for debugging specific workflows.

Copy the `SampleMD2LaTeX.config` file to a convenient location, and edit it as documented within the file.  The configuration points are analogous to the command line options.



To Generate LaTeX
-----------------

`md2LaTeX` will be installed in your executable paths by Python's `setuptools`, so this should be runnable from any location.  It is often convenient to do so while in the directory that contains the model's .mdzip file, the MyModel.config file, and the directory for LaTeX output.

`md2LaTeX --config MyModel.config`

The results will be in the output directories specified in MyModel.config.


makechangebartex
================

NOTE: The standard latexdiff tool has been enhanced to provide much of the behavior that is performed in makechangebartex.py.  If you are using a latexdiff that is version 1.3.0 or higher, you can instead use the following in most cases to produce an OMG-ready changebar document:

	latexdiff --append-safecmd="mycomment" --flatten --driver=pdftex -p omg_changebar_preamble.txt --filterscript "removeomgmarkup.pl | replaceUserfiles.py" [files or revisions] > [outputfile]

See the documentation that comes with latexdiff for further details.  `omg_changebar_preamble.txt` is included in this repository for convenience.  During normal operation of `makechangebartex.pl` it is created and deleted as needed.


To Extend
=========
This toolkit is intended to be open to anyone to extend to add support for additional modeling environments, to broaden the availability of authoring an OMG specification process document using the MDSA approach.

Additions will need to emit the LaTeX macros defined in `omg_modelgen.sty`, provided in the MDSA package from OMG. A brief description follows:

omgclass
--------
Simple class name

	\omgclass{ClassName}

omggeneralizations
------------------
List environment. Generalizations of `ClassName`.

	\begin{omggeneralizations}
		\item [BaseClassName]
		...
	\end{omggeneralizations}

omgassocreq
-----------
List environment.  Required associations from `ClassName`.

	\begin{omgassocreq}
		\item [assocName : assocTarget {cardinality}] assocName's documentation text
		...
	\end{omgassocreq}

omgassocopt
-----------
List environment.  Optional associations from `ClassName`.

	\begin{omgassocopt}
		\item [assocName : assocTarget {cardinality}] assocName's documentation text
		...
	\end{omgassocopt}

omgattrreq
----------
List environment.  Required attributes from `ClassName`.

	\begin{omgattrreq}
		\item [attributeName : attributeType] attributeName's documentation text
		...
	\end{omgattrreq}

omgattropt
----------
List environment.  Optional attributes from `ClassName`.

	\begin{omgattropt}
		\item [attributeName : attributeType] attributeName's documentation text
		...
	\end{omgattropt}

omgconstraints
--------------
List environment.  Constraints on enclosing element.

	\begin{omgconstraints}
		\item [{constraintName : [constraintExpression]}] constraintName's documentation text
		...
	\end{omgconstraints}
