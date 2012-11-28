"""PopPage is a utility for generating static web pages.

Usage:
    poppage TMPLFILE [--defaults=DFLTFILE] [--output=OUTFILE] [((--string=STRING | --file=FILE) VAR)]...
    poppage -h | --help
    poppage --version

Arguments:
    TMPLFILE    A Jinja2 template file used to generate the output.
    VAR         The template variable to target for the given content.

Options:
    --defaults=DFLTFILE     A YAML file with default template content.
    --output=OUTFILE        The output file to create.
    --string=STRING         Use the given string for the template variable content.
    --file=FILE             Use the given file contents for the template variable content.
    -h --help               Show this help message and exit.
    --version               Show version and exit.
"""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import sys

import yaml
from docopt import docopt
from jinja2 import FileSystemLoader
from jinja2.environment import Environment

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

__version__ = "poppage 0.1.0-alpha"

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

def main():
    """This function implements the main logic."""
    args = docopt(__doc__, version=__version__)

    tmplfile = args['TMPLFILE']
    dfltfile = args['--defaults']
    tmpldict = {}

    # Extract default values from YAML file, if given.
    if dfltfile:
        tmpldict = yaml.load(open(dfltfile, "r").read())

    # Parse template dictionary info from command line.
    i = 0
    for arg in sys.argv:
        if arg.startswith("--string"):
            tmpldict[sys.argv[i+1]] = arg.split("=")[1]
        elif arg.startswith("--file"):
            tmpldict[sys.argv[i+1]] = open(arg.split("=")[1], "r").read()
        i += 1

    # Render template.
    env = Environment()
    env.loader = FileSystemLoader('.')
    tmpl = env.get_template(tmplfile)
    print tmpl.render(**tmpldict)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    main()
