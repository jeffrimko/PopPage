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
    --nestdelim=DELIM       Delimiter to use for specifying nested KEYs. [default: ::]
    -h --help               Show this help message and exit.
    --version               Show version and exit.
"""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import collections
import os
import os.path as op
import sys

import auxly.filesys as fsys
import qprompt
import yaml
from binaryornot.check import is_binary
from docopt import docopt
from jinja2 import FileSystemLoader, Template, meta
from jinja2.environment import Environment
from jinja2schema import infer, model
from auxly import shell as sh

##==============================================================#
## SECTION: Setup                                               #
##==============================================================#

reload(sys)
sys.setdefaultencoding("utf-8")

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

#: Application version string.
__version__ = "0.2.2"

#: Key separator.
KEYSEP = "::"

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

def update(d, u):
    """Updates a dictionary without replacing nested dictionaries. Code found
    from `https://stackoverflow.com/a/3233356`."""
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

def check_template(tmplstr, tmpldict=None):
    def check_tmplitems(items, tmpldict, topkey=""):
        missing = []
        for key,val in items:
            if type(val) == model.Dictionary:
                missing += check_tmplitems(
                        val.items(),
                        tmpldict.get(key, {}),
                        key if not topkey else "%s%s%s" % (topkey, KEYSEP, key))
            else:
                name = key if not topkey else "%s%s%s" % (topkey, KEYSEP, key)
                try:
                    if key not in tmpldict.keys():
                        missing.append(name)
                except:
                    qprompt.warn("Issue checking var `%s`!" % (name))
        return missing

    tmpldict = tmpldict or {}
    missing = check_tmplitems(infer(tmplstr).items(), tmpldict)
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
        if not is_binary(inpath):
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

def parse_dict(args):
    """Parses the given arguments into a template dictionary."""
    class FileReader(str):
        def __new__(cls, fpath):
            with open(fpath) as fi:
                return str.__new__(cls, fi.read())
        def __repr__(self):
            return self
    class CmdExec(str):
        def __new__(cls, cmd):
            return str.__new__(cls, sh.strout(cmd))
        def __repr__(self):
            return self
    def cmd_ctor(loader, node):
        value = loader.construct_scalar(node)
        return CmdExec(value)
    def file_reader_ctor(loader, node):
        value = loader.construct_scalar(node)
        return FileReader(value)
    yaml.add_constructor(u'!file', file_reader_ctor)
    yaml.add_constructor(u'!cmd', cmd_ctor)

    # Prepare template dictionary.
    tmpldict = {}
    dfltfile = args['--defaults']
    if dfltfile:
        tmpldict = yaml.load(open(dfltfile, "r").read())
    tmpldict = update(tmpldict, {k:v for k,v in zip(args['--string'], args['VAL'])})
    tmpldict = update(tmpldict, {k:open(v).read() for k,v in zip(args['--file'], args['PATH'])})

    # Handle nested dictionaries.
    topop = []
    tmplnest = {}
    delim = args['--nestdelim']
    for k,v in tmpldict.iteritems():
        if k.find(delim) > -1:
            level = tmplnest
            ks = k.split(delim)
            for ln,sk in enumerate(ks):
                level[sk] = {}
                if len(ks)-1 == ln:
                    level[sk] = v
                else:
                    level = level[sk]
            topop.append(k)
    for k in topop:
        tmpldict.pop(k)
    tmpldict = update(tmpldict, tmplnest)

    return tmpldict

def main():
    """This function implements the main logic."""
    args = docopt(__doc__, version="poppage-%s" % (__version__))
    inpath = args['INPATH']
    outpath = args['OUTPATH']
    tmpldict = parse_dict(args)

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
