"""PopPage is a utility for generating static web pages.

Usage:
    poppage INPATH [--defaults=DFLTFILE] [options] [(--string KEY VAL) | (--file KEY PATH)]... [OUTPATH]
    poppage -h | --help
    poppage --version

Arguments:
    INPATH      Input Jinja2 template used to generate the output; can be a single file or a directory.
    OUTPATH     Path of the generated output; either a file or directory based on the input template.

Options:
    --defaults=DFLTFILE     A YAML file with default template content.
    --string=KEY            Use the given string in VAR for the given template variable KEY.
    --file=KEY              Use the given file contents in PATH for the given template variable KEY.
    --nestdelim=DELIM       Delimiter to use for specifying nested KEYs. [default: :#:]
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
from binaryornot.check import is_binary
from docopt import docopt
from jinja2 import FileSystemLoader, Template, meta
from jinja2.environment import Environment

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

__version__ = "poppage 0.2.0-alpha"

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

def render_str(tmplstr, tmpldict):
    env = Environment()
    tvar = meta.find_undeclared_variables(env.parse(tmplstr))
    miss = tvar - set(tmpldict.keys())
    if miss:
        qprompt.error("Template vars `%s` were not supplied values!" % (
            "/".join(miss)))
        return
    return Template(tmplstr).render(**tmpldict)

def render_file(tmplpath, tmpldict):
    tmplpath = op.abspath(tmplpath)
    env = Environment()
    env.loader = FileSystemLoader(op.dirname(tmplpath))
    tmpl = env.get_template(op.basename(tmplpath))
    tvar = meta.find_undeclared_variables(env.parse(open(tmplpath).read()))
    miss = tvar - set(tmpldict.keys())
    if miss:
        qprompt.error("Template vars `%s` in `%s` were not supplied values!" % (
            "/".join(miss),
            op.basename(tmplpath)))
        return
    return tmpl.render(**tmpldict)

def pop(inpath, tmpldict, outpath=None):
    """Generates a file or directory based on the given input
    template/dictionary."""
    if op.isfile(inpath):
        pop_file(inpath, tmpldict, outpath=outpath)
    else:
        pop_dir(inpath, tmpldict, outpath=outpath)

def pop_file(inpath, tmpldict, outpath=None):
    inpath = op.abspath(inpath)
    if is_binary(inpath):
        qprompt.status("Copying `%s`..." % (outpath), filesys.copy, [inpath,outpath])
        return
    text = render_file(inpath, tmpldict)
    if text == None:
        return False

    # A rendered output path will be used if no explicit path provided.
    if outpath == None:
        opath = render_str(inpath, tmpldict)
        if not opath:
            return False
        if opath != inpath:
            outpath = opath

    # Handle rendered output.
    if outpath:
        with open(outpath, "w") as f:
            qprompt.status("Writing `%s`..." % (outpath), f.write, [text])
    else:
        qprompt.echo(text)
    return True

def pop_dir(inpath, tmpldict, outpath=None, _roots=None):
    inpath = op.abspath(inpath)
    dpath = op.dirname(inpath)
    bpath = op.basename(inpath)
    if not outpath:
        outpath = render_str(dpath, tmpldict)
        dname = render_str(bpath, tmpldict)
        if not dname:
            return False
        mpath = op.join(outpath, dname)
    else:
        mpath = op.abspath(outpath)
    if not mpath:
        return False
    if _roots:
        mpath = mpath.replace(*_roots)
    else:
        _roots = (render_str(inpath, tmpldict), mpath)
    qprompt.status("Making dir `%s`..." % (mpath), filesys.makedirs, [mpath])

    # Iterate over files and directories in parent only.
    for r,ds,fs in os.walk(inpath):
        for f in fs:
            ipath = op.join(r,f)
            fname = render_str(f, tmpldict)
            opath = op.join(mpath, fname)
            if not pop_file(ipath, tmpldict, opath):
                return False
        for d in ds:
            ipath = op.join(r, d)
            if not pop_dir(ipath, tmpldict, _roots=_roots):
                return False
        break
    return True

def main():
    """This function implements the main logic."""
    args = docopt(__doc__, version=__version__)

    inpath = args['INPATH']
    outpath = args['OUTPATH']
    dfltfile = args['--defaults']

    # Prepare template dictionary.
    tmpldict = {}
    if dfltfile:
        defaults = yaml.load(open(dfltfile, "r").read())
        tmpldict.update(defaults.get('string',{}))
        tmpldict.update({k:open(v).read() for k,v in defaults.get('file',{}).iteritems()})
    tmpldict.update({k:v for k,v in zip(args['--string'], args['VAL'])})
    tmpldict.update({k:open(v).read() for k,v in zip(args['--file'], args['PATH'])})

    # Handle nested dictionaries.
    tmplnest = {}
    topop = []
    delim = args['--nestdelim']
    for k,v in tmpldict.iteritems():
        if k.find(delim) > -1:
            sk,sv = k.split(delim)
            tmplnest.setdefault(sk, {})
            tmplnest[sk][sv] = v
            topop.append(k)
    for k in topop:
        tmpldict.pop(k)
    tmpldict.update(tmplnest)

    pop(inpath, tmpldict, outpath=outpath)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    main()
