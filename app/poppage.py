"""PopPage is a utility for generating static web pages.

Usage:
    poppage make INPATH [--defaults DFLTFILE] [options] [(--string KEY VAL) | (--file KEY PATH)]... [OUTPATH]
    poppage check INPATH
    poppage -h | --help
    poppage --version

Commands:
    make    Generates directories and files based on the given INPATH template.
    check   Check the given INPATH template for variables.

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
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import auxly.filesys as fsys
import qprompt
import yaml
from binaryornot.check import is_binary
from docopt import docopt
from jinja2 import FileSystemLoader, Template, meta
from jinja2.environment import Environment
from jinja2schema import infer, model

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

#: Application version string.
__version__ = "0.2.0"

#: Key separator.
KEYSEP = "->"

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

def check_template(tmplstr, tmpldict=None):
    tmpldict = tmpldict or {}
    missing = []
    for key, val in infer(tmplstr).items():
        if key not in tmpldict:
            missing.append(key)
        if type(val) == model.List:
            for subkey in val.item.keys():
                if subkey not in tmpldict[key][0]:
                    missing.append("%s%s%s" % (key, KEYSEP, subkey))
        elif type(val) == model.Dictionary:
            for subkey in val.keys():
                if subkey not in tmpldict.get(key,[]):
                    missing.append("%s%s%s" % (key, KEYSEP, subkey))
    return missing

def render_str(tmplstr, tmpldict):
    env = Environment()
    miss = check_template(tmplstr, tmpldict)
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
    tmplstr = open(tmplpath).read()
    miss = check_template(tmplstr, tmpldict)
    if miss:
        qprompt.error("Template vars `%s` in `%s` were not supplied values!" % (
            "/".join(miss),
            op.basename(tmplpath)))
        return
    return tmpl.render(**tmpldict)

def make(inpath, tmpldict, outpath=None):
    """Generates a file or directory based on the given input
    template/dictionary."""
    if op.isfile(inpath):
        make_file(inpath, tmpldict, outpath=outpath)
    else:
        make_dir(inpath, tmpldict, outpath=outpath)

def make_file(inpath, tmpldict, outpath=None):
    inpath = op.abspath(inpath)
    if is_binary(inpath):
        qprompt.status("Copying `%s`..." % (outpath), fsys.copy, [inpath,outpath])
        return
    text = render_file(inpath, tmpldict)
    if text == None:
        return False

    # A rendered output path will be used if no explicit path provided.
    if outpath == None:
        if inpath.find("{{") > -1 and inpath.find("}}") > -1:
            opath = render_str(inpath, tmpldict)
            if not opath:
                return False
            if opath != inpath:
                outpath = opath

    # Handle rendered output.
    if outpath:
        outpath = op.abspath(outpath)
        fsys.makedirs(op.dirname(outpath))
        with open(outpath, "w") as f:
            qprompt.status("Writing `%s`..." % (outpath), f.write, [text])
    else:
        qprompt.echo(text)
    return True

def make_dir(inpath, tmpldict, outpath=None, _roots=None):
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
    qprompt.status("Making dir `%s`..." % (mpath), fsys.makedirs, [mpath])

    # Iterate over files and directories in parent only.
    for r,ds,fs in os.walk(inpath):
        for f in fs:
            ipath = op.join(r,f)
            fname = render_str(f, tmpldict)
            opath = op.join(mpath, fname)
            if not make_file(ipath, tmpldict, opath):
                return False
        for d in ds:
            ipath = op.join(r, d)
            if not make_dir(ipath, tmpldict, _roots=_roots):
                return False
        break
    return True

def check(inpath, echo=False):
    """Checks the inpath template for variables."""
    tvars = check_template(op.basename(inpath))
    if op.isfile(inpath):
        with open(inpath) as fi:
            tvars += check_template(fi.read())
    else:
        for r,ds,fs in os.walk(inpath):
            for x in ds+fs:
                xpath = op.join(r,x)
                tvars += check(xpath)
    tvars = sorted(list(set(tvars)))
    if echo:
        qprompt.echo("Found variables:")
        for var in tvars:
            qprompt.echo("  " + var)
    return tvars

def main():
    """This function implements the main logic."""
    args = docopt(__doc__, version="poppage-%s" % (__version__))
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

    # Handle command.
    if args['check']:
        check(inpath, echo=True)
    elif args['make']:
        make(inpath, tmpldict, outpath=outpath)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    main()
