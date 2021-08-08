#!/usr/bin/env python
"""
Copyright Elemental Reasoning, LLC, 2019-2021
Copyright Object Management Group, 2021
All rights reserved unless otherwise specified in licensing agreement.
---------------"""
import click
import sys
import os
import tempfile
from click import command, option, Option, UsageError


class MutuallyExclusiveOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        help = kwargs.get('help', '')
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = help + (
                ' NOTE: This argument is mutually exclusive with '
                ' arguments: [' + ex_str + '].'
            )
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                "Illegal usage: `{}` is mutually exclusive with "
                "arguments `{}`.".format(
                    self.name,
                    ', '.join(self.mutually_exclusive)
                )
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx,
            opts,
            args
        )
# flatex = '~/bin/flatex/flatex.py'
unomgtool = './removeomgmarkup.pl'
latexdiff = '~/bin/latexdiff/latexdiff'

verbose = False
debug = False

stylefile = None

# def flatten(texfile):
#     # flatfile = tf + ".flat"
#     global debug
#     tempflat = tempfile.NamedTemporaryFile(suffix='.flat', dir=os.path.dirname(texfile), delete=(not debug))
#     flatfile = os.path.join(tempfile.gettempdir(), tempflat.name)
#     if verbose:
#         print("flatten: " + flatfile)
#
#     cmd = ' '.join(['python', flatex, tf, flatfile])
#     if debug:
#         print (cmd)
#     os.system(cmd)
    # return tempflat, flatfile
    
def getStyle(stylepath, oldStyle=False):
    global debug
    if oldStyle:
        stylefilename=None
        style = "-t CCHANGEBAR"
    else:
        # stylefile = tempfile.NamedTemporaryFile(suffix='txt', prefix='omg_', delete=(not debug))
        # stylefilename = os.path.join(tempfile.gettempdir(), stylefile.name)
        stylefilename = os.path.join(stylepath,"omg_changebar_preamble.txt")
        stylefile = open(stylefilename, 'w')
        if debug:
            print (stylefilename)
        style = "-p " + stylefilename

        # We are overriding the built in latexdiff styles instead of modifying the code in-place, for future-proofing
        # against latexdiff updates.  This is obviously based off of CCHANGEBAR, SAFE, FLOATSAFE, LISTINGS
        stylefile.write("""
\RequirePackage[dvips,leftbars]{changebar}
\changebarsep=\marginparwidth 
\changebarwidth=2pt
\deletebarwidth=8pt
\RequirePackage{color}\definecolor{RED}{rgb}{1,0,0}\definecolor{BLUE}{rgb}{0,0,1}
\providecommand{\DIFadd}[1]{\protect\cbstart{\protect\color{blue}#1}\protect\cbend}
\providecommand{\DIFdel}[1]{\protect\cbdelete{\protect\color{red}#1}\protect\cbdelete}
\providecommand{\DIFaddbegin}{}
\providecommand{\DIFaddend}{}
\providecommand{\DIFdelbegin}{}
\providecommand{\DIFdelend}{}
\providecommand{\DIFaddFL}[1]{\DIFadd{#1}}
\providecommand{\DIFdelFL}[1]{\DIFdel{#1}}
\providecommand{\DIFaddbeginFL}{}
\providecommand{\DIFaddendFL}{}
\providecommand{\DIFdelbeginFL}{}
\providecommand{\DIFdelendFL}{}
\lstdefinelanguage{codediff}{
  moredelim=**[is][\color{red}]{*!----}{----!*},
  moredelim=**[is][\color{blue}]{*!++++}{++++!*}
}
\lstdefinestyle{codediff}{
	belowcaptionskip=.25\\baselineskip,
	language=codediff,
	basicstyle=\\ttfamily,
	columns=fullflexible,
	keepspaces=true,
}
""")
        stylefile.flush()
        os.fsync(stylefile)
        stylefile.close()
    return stylefilename, style
    

@click.command()
@click.option('-v', is_flag=True, default=False, help="Verbose")
@click.option('-d', is_flag=True, default=False, help="Debug")
@click.option('--revision', '-r', multiple=True, help="Once to compare against, twice to compare between ", cls=MutuallyExclusiveOption, mutually_exclusive=["original_file"])
@click.option('--original_file', '-R', type = click.Path(), help="If given, will be used as older version of file", cls=MutuallyExclusiveOption, mutually_exclusive=["revision"])
@click.argument('file_to_diff', type = click.Path())
@click.argument('diff_output_file', type = click.Path())
def main(file_to_diff, original_file, diff_output_file, flatex, v, d):
    global verbose, debug, stylefile
    verbose = v
    debug = d
    verbosity = ""
    
    if verbose:
        verbosity = '--verbose'
        print("makechangebartex: \n\tbase: '" + file_to_diff + "'\n\trev:  '" + original_file + "'\n\tdiff: '" + diff_output_file + "'\n")
        
    file_to_diff = os.path.abspath(file_to_diff).replace(' ', '\ ')
    diff_output_file = os.path.abspath(diff_output_file).replace(' ', '\ ')
    
    filelist = ""
    if len(revision) > 0:
        revisions = "--git "
        latexdiff += '-vc'  # Use the version control version of latexdiff
        for rev in revision:
            revisions += "-r " + rev + " "
        filelist = revisions + file_to_diff
    else:
        if original_file != "":
            original_file = os.path.abspath(original_file).replace(' ', '\ ')
            filelist = original_file + " " + file_to_diff
        else:
            print("ERROR: must provide one of --original-file or --revision")

    # if oldStyle is TRUE, defaults to using latexdiff's CHANGEBAR style. Use only for debugging Very Bad Things
    oldStyle = False
    stylefilename, style = getStyle(os.path.dirname(diff_output_file), oldStyle)
    if not oldStyle and not os.path.exists(style[3:]):
        print("Error: style file is missing:", style)
    
    cmd = ' '.join([latexdiff, '--append-safecmd="mycomment" --flatten --driver=pdftex', filterscript, verbosity, style, filelist, '> ', diff_output_file])

    if debug:
        print(cmd)
    os.system(cmd)
    
    if stylefilename:
        if debug:
            print(stylefilename)
        else:
            os.remove(stylefilename)

if __name__ == '__main__':
    main()

