"""PopPage is a utility for generating output from templates.

Usage:
    poppage INPATH [runargs]
    poppage make [options] [(--string KEY VAL) | (--file KEY PATH)]...
    poppage check [options]
    poppage run [options] [(--string KEY VAL) | (--file KEY PATH)]...
    poppage debug [options] [(--string KEY VAL) | (--file KEY PATH)]...
    poppage -h | --help
    poppage --version

Commands:
    check   Check the given INPATH template for variables.
    make    Generates directories and files based on the given INPATH template.
    run     Generates the OUTPATH, executes commands, then deletes OUTPATH.
    debug   Shows the state of the utility and template data structures.

Options:
    --inpath INPATH         Input Jinja2 template used to generate the output;
                            can be a single file or a directory.
    --defaults DFLTFILE     A YAML file with default template content.
    --outpath OUTPATH       Path of the generated output; either a file or
                            directory based on the input template.
    --execute EXECUTE       Commands to execute after rendering template. Only
                            applies to run command.
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
  - In a YAML defaults file, use a `command` key under `__opt__` to specify the
    default command.
  - When running using INPATH as first argument, additional arguments will be
    passed to the execute commands as RUNARGS. In this scenario, INPATH will
    typically be a YAML defaults file with an `__opt__` key.
"""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import collections
import io
import os
import os.path as op
import random
import sys
import tempfile
from string import ascii_lowercase
from pprint import pprint

import auxly.filesys as fsys
import auxly.shell as sh
import qprompt
from binaryornot.check import is_binary
from docopt import docopt
from jinja2 import FileSystemLoader, Template, Undefined, meta
from jinja2.environment import Environment
from jinja2schema import infer, model

import gitr
import utilconf

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
__version__ = "0.7.1"

#: Key separator.
KEYSEP = "::"

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class SkipUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return None
    def __getitem__(self, key):
        return self
    def __getattr__(self, key):
        return self

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

#: Random uppercase string of length x.
_getrands = lambda x: "".join(random.choice(ascii_lowercase) for _ in range(x))

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
                    if fname:
                        outpath = op.join(outpath, op.basename(fname))
                if dname:
                    outpath = op.join(outpath, op.basename(dname))
                if fname:
                    return op.join(tpath, op.basename(fname)), outpath, tpath
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
            if to_delete:
                if op.isdir(inpath):
                    # If using a temporary directory to hold the template (e.g.
                    # downloaded from Github), don't include that directory
                    # name in the output paths.
                    fkwargs['pathsubs'] = [[op.basename(to_delete), "."]]
            retval = func(*fargs, **fkwargs)
            if to_delete:
                fsys.delete(to_delete)
            return retval
        return inner
    return wrap

def check_template(tmplstr, tmpldict=None):
    """Checks the given template string against the given template variable
    dictionary. Returns a list of variables not provided in the given
    dictionary."""
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

def render_str(tmplstr, tmpldict, bail_miss=False):
    """Renders the given template string using the given template variable
    dictionary. Returns the rendered text as a string."""
    env = Environment(undefined=SkipUndefined, extensions=['jinja2_time.TimeExtension'])
    env.trim_blocks = True
    env.lstrip_blocks = True
    miss = check_template(tmplstr, tmpldict)
    if miss:
        qprompt.warn("Template vars `%s` were not supplied values!" % (
            "/".join(miss)))
    return env.from_string(tmplstr).render(**tmpldict)

def render_file(tmplpath, tmpldict, bail_miss=False):
    """Renders the template file and the given path using the given template
    variable dictionary. Returns the rendered text as a string."""
    tmplpath = op.abspath(tmplpath)
    env = Environment(undefined=SkipUndefined, extensions=['jinja2_time.TimeExtension'])
    env.trim_blocks = True
    env.lstrip_blocks = True
    for encoding in ["utf-8", "mbcs"]:
        try:
            env.loader = FileSystemLoader(op.dirname(tmplpath), encoding=encoding)
            tmpl = env.get_template(op.basename(tmplpath))
            break
        except UnicodeDecodeError:
            qprompt.warn("Issue while decoding template with `%s`!" % encoding)
    else:
        qprompt.fatal("Unknown issue while loading template!")
    with io.open(tmplpath) as fo:
        tmplstr = fo.read()
    miss = check_template(tmplstr, tmpldict)
    if miss:
        qprompt.warn("Template vars `%s` in `%s` were not supplied values!" % (
            "/".join(miss),
            op.basename(tmplpath)))
    return tmpl.render(**tmpldict)

@handle_paths(inpath=0,outpath=2)
def make(inpath, tmpldict, outpath=None, **kwargs):
    """Generates a file or directory based on the given input
    template/dictionary."""
    if op.isfile(inpath):
        return make_file(inpath, tmpldict, outpath=outpath, **kwargs)
    else:
        return make_dir(inpath, tmpldict, outpath=outpath, **kwargs)

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
        if inpath == outpath:
            qprompt.fatal("Output cannot overwrite input template!")
        fsys.makedirs(op.dirname(outpath))
        with io.open(outpath, "w", encoding="utf-8") as f:
            qprompt.status("Writing `%s`..." % (outpath), f.write, [text])
    else:
        qprompt.echo(text)
    return True

def make_dir(inpath, tmpldict, outpath=None, pathsubs=None):
    pathsubs = pathsubs or []
    inpath = op.abspath(inpath)
    bpath = op.basename(inpath)
    if not outpath:
        outpath = os.getcwd()
    dname = render_str(bpath, tmpldict)
    if not dname:
        return False
    mpath = op.abspath(op.join(outpath, dname))
    if not mpath:
        return False
    for sub in pathsubs:
        mpath = mpath.replace(*sub)
    if inpath == mpath:
        qprompt.fatal("Output cannot overwrite input template!")
    mpath = render_str(mpath, tmpldict)
    qprompt.status("Making dir `%s`..." % (mpath), fsys.makedirs, [mpath])

    # Iterate over files and directories IN PARENT ONLY.
    for r,ds,fs in os.walk(inpath):
        for f in fs:
            ipath = op.join(r,f)
            fname = render_str(f, tmpldict)
            opath = op.join(mpath, fname)
            if not make_file(ipath, tmpldict, opath):
                return False
        for d in ds:
            ipath = op.join(r, d)
            if not make_dir(ipath, tmpldict, mpath, pathsubs=pathsubs):
                return False
        break # Prevents from walking beyond parent.
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

def run(inpath, tmpldict, outpath=None, execute=None, runargs=None):
    """Handles logic for `run` command."""
    if not outpath:
        outpath = op.join(os.getcwd(), "__temp-poppage-" + _getrands(6))
    make(inpath, tmpldict, outpath=outpath)
    qprompt.hrule()
    if not execute:
        execute = outpath
    tmpldict.update({'outpath': outpath})
    tmpldict.update({'runargs': " ".join(runargs or [])})
    execute = render_str(execute, tmpldict)
    for line in execute.splitlines():
        sh.call(line.strip())
    fsys.delete(outpath)

def main():
    """This function implements the main logic."""
    if len(sys.argv) > 1 and op.isfile(sys.argv[1]):
        args = {}
        args['--defaults'] = sys.argv[1]
        args['--file'] = []
        args['--keysep'] = "::"
        args['--string'] = []
        args['PATH'] = []
        args['VAL'] = []
        args['runargs'] = sys.argv[2:] or ""
    else:
        args = docopt(__doc__, version="poppage-%s" % (__version__))
    utildict, tmpldict = utilconf.parse(args)

    # Check required conditions.
    if not utildict.get('inpath'):
        qprompt.fatal("Must supply INPATH!")

    # Handle command.
    if utildict['command'] == "check":
        check(utildict['inpath'][0], echo=True)
    elif utildict['command'] == "make":
        for inpath, outpath in zip(utildict['inpath'], utildict['outpath']):
            make(inpath, tmpldict, outpath=outpath)
    elif utildict['command'] == "run":
        run(
                utildict['inpath'][0],
                tmpldict,
                outpath=utildict['outpath'][0],
                execute=utildict.get('execute'),
                runargs=utildict.get('runargs'))
    elif utildict['command'] == "debug":
        qprompt.echo("Utility Dictionary:")
        pprint(utildict)
        qprompt.echo("Template Dictionary:")
        pprint(tmpldict)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    main()
