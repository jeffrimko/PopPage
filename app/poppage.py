"""PopPage is a utility for generating static web pages.

Usage:
    poppage INPATH [--defaults=DFLTFILE] [(--string KEY VAL) | (--file KEY PATH)]... [OUTPATH]
    poppage -h | --help
    poppage --version

Arguments:
    INPATH      Input Jinja2 template used to generate the output; can be a single file or a directory.
    OUTPATH     Path of the generated output; either a file or directory based on the input template.

Options:
    --defaults=DFLTFILE     A YAML file with default template content.
    --string=KEY            Use the given string in VAR for the given template variable KEY.
    --file=KEY              Use the given file contents in PATH for the given template variable KEY.
    -h --help               Show this help message and exit.
    --version               Show version and exit.
"""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import os.path as op
import sys

import auxly.filesys as fs
import yaml
from docopt import docopt
from jinja2 import FileSystemLoader
from jinja2.environment import Environment

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

__version__ = "poppage 0.2.0-alpha"

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

def main():
    """This function implements the main logic."""
    args = docopt(__doc__, version=__version__)

    inpath = args['INPATH']
    outpath = args['OUTPATH']
    dfltfile = args['--defaults']
    tmpldict = {}

    # Extract default values from YAML file, if given.
    if dfltfile:
        defaults = yaml.load(open(dfltfile, "r").read())
        tmpldict.update(defaults.get('string',{}))
        tmpldict.update({k:open(v).read() for k,v in defaults.get('file',{}).iteritems()})
    tmpldict.update({k:v for k,v in zip(args['--string'], args['VAL'])})
    tmpldict.update({k:open(v).read() for k,v in zip(args['--file'], args['PATH'])})

    # Render template.
    env = Environment()
    env.loader = FileSystemLoader(".")
    tmpl = env.get_template(inpath)
    rndr = tmpl.render(**tmpldict)

    # Handle rendered output.
    if outpath:
        with open(outpath, "w") as f:
            f.write(rndr)
    else:
        print(rndr)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    main()
