"""PopPage is a utility for generating static web pages.

Usage:
    poppage make INPATH [options] [(--string KEY VAL) | (--file KEY PATH)]... [OUTPATH]
    poppage check INPATH
    poppage -h | --help
    poppage --version

Commands:
    make    Generates directories and files based on the given INPATH template.
    check   Check the given INPATH template for variables.

Arguments:
    INPATH      Input Jinja2 template used to generate the output; can be a
                single file or a directory.
    OUTPATH     Path of the generated output; either a file or directory based
                on the input template.

Options:
    --defaults DFLTFILE     A YAML file with default template content.
    --string KEY VAL        Use the given string VAL for the given template
                            variable KEY.
    --file KEY PATH         Use the given file contents in PATH for the given
                            template variable KEY.
    --keysep KEYSEP         Delimiter to use for separating nested KEYs.
                            [default: ::]
    -h --help               Show this help message and exit.
    --version               Show version and exit.

Notes:
  - Template file/directory names can contain template variables (e.g.
    `{{foo}}.txt`). The provided key/values will be used for the output file
    generation unless an explicit OUTPATH is provided.
  - The output will be passed to `stdout` if INPATH is a file (rather than a
    directory) and INPATH does not contain a template variable and no OUTPATH
    is specified.
"""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import collections
import io
import os
import os.path as op
import sys
import tempfile

import auxly.filesys as fsys
import auxly.shell as sh
import qprompt
import yaml
from binaryornot.check import is_binary
from docopt import docopt
from jinja2 import FileSystemLoader, Template, meta
from jinja2.environment import Environment
from jinja2schema import infer, model

import gitr

##==============================================================#
## SECTION: Setup                                               #
##==============================================================#

# Handle Python 2/3 differences.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding("utf-8")

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

#: Application version string.
__version__ = "0.3.3"

#: Key separator.
KEYSEP = "::"

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

def handle_paths(**dkwargs):
    def wrap(func):
        def handler(inpath, outpath):
            if gitr.is_github(inpath):
                tpath = tempfile.mkdtemp(prefix="poppage-")
                gitr.download(inpath, tpath)
                fname = gitr.is_file(inpath)
                dname = gitr.is_dir(inpath)
                if outpath == None:
                    outpath = os.getcwd()
                    if dname:
                        outpath = op.join(outpath, dname)
                    elif fname:
                        outpath = op.join(outpath, fname)
                if fname:
                    return op.join(tpath, fname), outpath, tpath
                return tpath, outpath, tpath
            return inpath, outpath, None
        def inner(*fargs, **fkwargs):
            inpath = fkwargs.get('inpath') or (
                    fargs[dkwargs['inpath']] if (
                        'inpath' in dkwargs.keys() and dkwargs['inpath'] < len(fargs))
                    else None)
            outpath = fkwargs.get('outpath') or (
                    fargs[dkwargs['outpath']] if (
                        'outpath' in dkwargs.keys() and dkwargs['outpath'] < len(fargs))
                    else None)
            inpath, outpath, to_delete = handler(inpath, outpath)
            fargs = list(fargs)
            # The following tries to intelligently handle function arguments so
            # that this decorator can be generalized. Need to handle conditions
            # where arguments may positional or keyword.
            for var,key in ((inpath,"inpath"),(outpath,"outpath")):
                if key in dkwargs.keys():
                    if not var:
                        continue
                    if key in fkwargs.keys():
                        fkwargs[key] = var
                    elif dkwargs[key] < len(fargs):
                        fargs[dkwargs[key]] = var
                    else:
                        fkwargs[key] = var
            retval = func(*fargs, **fkwargs)
            if to_delete:
                fsys.delete(to_delete)
            return retval
        return inner
    return wrap

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
    try:
        missing = check_tmplitems(infer(tmplstr).items(), tmpldict)
    except:
        missing = []
    return missing

def render_str(tmplstr, tmpldict):
    env = Environment(extensions=['jinja2_time.TimeExtension'])
    miss = check_template(tmplstr, tmpldict)
    if miss:
        qprompt.error("Template vars `%s` were not supplied values!" % (
            "/".join(miss)))
        return
    return Template(tmplstr).render(**tmpldict)

def render_file(tmplpath, tmpldict):
    tmplpath = op.abspath(tmplpath)
    env = Environment(extensions=['jinja2_time.TimeExtension'])
    for encoding in ["utf-8", "mbcs"]:
        try:
            env.loader = FileSystemLoader(op.dirname(tmplpath), encoding=encoding)
            tmpl = env.get_template(op.basename(tmplpath))
            break
        except UnicodeDecodeError:
            qprompt.warn("Issue while decoding template with `%s`!" % encoding)
    else:
        qprompt.error("Unknown issue while loading template!")
        exit()
    with io.open(tmplpath) as fo:
        tmplstr = fo.read()
    miss = check_template(tmplstr, tmpldict)
    if miss:
        qprompt.error("Template vars `%s` in `%s` were not supplied values!" % (
            "/".join(miss),
            op.basename(tmplpath)))
        return
    return tmpl.render(**tmpldict)

@handle_paths(inpath=0,outpath=2)
def make(inpath, tmpldict, outpath=None, **kwargs):
    """Generates a file or directory based on the given input
    template/dictionary."""
    if op.isfile(inpath):
        return make_file(inpath, tmpldict, outpath=outpath)
    else:
        return make_dir(inpath, tmpldict, outpath=outpath)

def make_file(inpath, tmpldict, outpath=None):
    inpath = op.abspath(inpath)
    if outpath:
        outpath = render_str(outpath, tmpldict)
        if op.isdir(outpath):
            outpath = op.join(outpath, op.basename(inpath))
            outpath = render_str(outpath, tmpldict)
    if is_binary(inpath):
        qprompt.status("Copying `%s`..." % (outpath), fsys.copy, [inpath,outpath])
        return
    text = render_file(inpath, tmpldict)
    if text == None:
        return False

    # Handle rendered output.
    if outpath:
        outpath = op.abspath(outpath)
        fsys.makedirs(op.dirname(outpath))
        with io.open(outpath, "w", encoding="utf-8") as f:
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
        outpath = render_str(outpath, tmpldict)
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

@handle_paths(inpath=0)
def check(inpath, echo=False, **kwargs):
    """Checks the inpath template for variables."""
    tvars = check_template(op.basename(inpath))
    if op.isfile(inpath):
        if not is_binary(inpath):
            with io.open(inpath) as fi:
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
            with io.open(fpath) as fi:
                return str.__new__(cls, fi.read().strip())
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
    def update(d, u):
        """Updates a dictionary without replacing nested dictionaries. Code
        found from `https://stackoverflow.com/a/3233356`."""
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                r = update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d
    yaml.add_constructor(u'!file', file_reader_ctor)
    yaml.add_constructor(u'!cmd', cmd_ctor)

    # Prepare template dictionary.
    tmpldict = {}
    dfltfile = args['--defaults']
    if dfltfile:
        tmpldict = yaml.load(open(dfltfile, "r").read())
    tmpldict = update(tmpldict, {k:v for k,v in zip(args['--string'], args['VAL'])})
    tmpldict = update(tmpldict, {k:open(v).read().strip() for k,v in zip(args['--file'], args['PATH'])})

    # Handle nested dictionaries.
    topop = []
    tmplnest = {}
    global KEYSEP
    KEYSEP = args['--keysep']
    for k,v in tmpldict.items():
        if k.find(KEYSEP) > -1:
            level = tmplnest
            ks = k.split(KEYSEP)
            for ln,sk in enumerate(ks):
                level[sk] = level.get(sk, {})
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
    # print(check("https://github.com/Ars2014/cookiecutter-telegram-bot/blob/master/cookiecutter.json"))
