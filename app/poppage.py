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

import os
import os.path as op

import auxly.filesys as filesys
import qprompt
import yaml
from docopt import docopt
from jinja2 import FileSystemLoader, Template
from jinja2.environment import Environment

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

__version__ = "poppage 0.2.0-alpha"

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

def render_str(s, info):
    return Template(s).render(**info)

def render_file(tmplpath, tmpldict):
    tmplpath = op.abspath(tmplpath)
    env = Environment()
    env.loader = FileSystemLoader(op.dirname(tmplpath))
    tmpl = env.get_template(op.basename(tmplpath))
    return tmpl.render(**tmpldict)

def handle_file(inpath, tmpldict, outpath=None):
    text = render_file(inpath, tmpldict)

    # A rendered output path will be used if no explicit path provided.
    opath = render_str(inpath, tmpldict)
    if opath != inpath and outpath == None:
        outpath = opath

    # Handle rendered output.
    if outpath:
        with open(outpath, "w") as f:
            qprompt.status("Writing `%s`..." % (outpath), f.write, [text])
    else:
        print(text)
    return True

def handle_dir(inpath, tmpldict, outpath=None):
    inpath = op.abspath(inpath)
    dpath = op.dirname(inpath)
    bpath = op.basename(inpath)
    if not outpath:
        outpath = dpath
    if not outpath:
        return False
    outpath = render_str(outpath, tmpldict)
    dname = render_str(bpath, tmpldict)
    if not dname:
        return False
    mpath = op.join(outpath, dname)
    qprompt.status("Making dir `%s`..." % (mpath), filesys.makedirs, [mpath])

    # Iterate over files and directories in parent only.
    for r,ds,fs in os.walk(inpath):
        for f in fs:
            ipath = op.join(r,f)
            fname = render_str(f, tmpldict)
            opath = op.join(mpath, fname)
            if not handle_file(ipath, tmpldict, opath):
                return False
        for d in ds:
            ipath = op.join(r, d)
            if not handle_dir(ipath, tmpldict):
                return False
        break
    return True

def main():
    """This function implements the main logic."""
    args = docopt(__doc__, version=__version__)

    inpath = args['INPATH']
    outpath = args['OUTPATH']
    dfltfile = args['--defaults']
    tmpldict = {}

    if dfltfile:
        defaults = yaml.load(open(dfltfile, "r").read())
        tmpldict.update(defaults.get('string',{}))
        tmpldict.update({k:open(v).read() for k,v in defaults.get('file',{}).iteritems()})
    tmpldict.update({k:v for k,v in zip(args['--string'], args['VAL'])})
    tmpldict.update({k:open(v).read() for k,v in zip(args['--file'], args['PATH'])})

    if op.isfile(inpath):
        handle_file(inpath, tmpldict, outpath=outpath)
    else:
        handle_dir(inpath, tmpldict, outpath=outpath)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    main()
