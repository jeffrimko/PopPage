##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import collections
import io
import os
import os.path as op

import yaml
import qprompt
import auxly.filesys as fsys
import auxly.shell as sh

#: TODO: This is a bit hacky and will be cleaned up in the future.
_DFLTFILE = None

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

##--------------------------------------------------------------#
## Custom YAML Tag Classes                                      #
##--------------------------------------------------------------#

class CmdExec(str):
    def __new__(cls, cmd):
        return str.__new__(cls, sh.strout(cmd))
    def __repr__(self):
        return self

class FileReader(str):
    def __new__(cls, fpath):
        if not op.isabs(fpath):
            global _DFLTFILE
            fpath = op.normpath(op.join(op.dirname(_DFLTFILE), fpath))
        with io.open(fpath) as fi:
            return str.__new__(cls, fi.read().strip())
    def __repr__(self):
        return self

class OptLoader(object):
    def __new__(cls, fpath):
        if not op.isabs(fpath):
            global _DFLTFILE
            fpath = op.normpath(op.join(op.dirname(_DFLTFILE), fpath))
        with io.open(fpath) as fi:
            opt = yaml.load(fi.read(), Loader=yaml.Loader)
        # TODO: Clean up, perhaps make function that can be called by get_defopts.
        if "inpath" in opt.keys():
            if not opt['inpath'].startswith("http"):
                opt['inpath'] = op.abspath(op.normpath(op.join(op.dirname(fpath), opt['inpath'])))
        return opt
    def __repr__(self):
        return str(self)

class IncLoader(object):
    def __new__(cls, fpath):
        if not op.isabs(fpath):
            global _DFLTFILE
            fpath = op.normpath(op.join(op.dirname(_DFLTFILE), fpath))
        with io.open(fpath) as fi:
            return yaml.load(fi.read(), Loader=yaml.Loader)
    def __repr__(self):
        return str(self)

class AskPrompter(str):
    def __new__(cls, msg):
        return str.__new__(cls, qprompt.ask_str(msg))
    def __repr__(self):
        return self

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

def _tolist_no_none(val):
    return [v for v in [val] if v != None]

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

##--------------------------------------------------------------#
## Custom YAML Tag Functions                                    #
##--------------------------------------------------------------#

def ctor_cmd(loader, node):
    value = loader.construct_scalar(node)
    return CmdExec(value)

def ctor_file(loader, node):
    value = loader.construct_scalar(node)
    return FileReader(value)

def ctor_py(loader, node):
    seq = loader.construct_sequence(node)
    cmd = seq.pop(0).format(*seq)
    return eval(cmd)

def ctor_yaml(loader, node):
    value = loader.construct_scalar(node)
    return IncLoader(value)

def ctor_opt(loader, node):
    value = loader.construct_scalar(node)
    return OptLoader(value)

def ctor_ask(loader, node):
    value = loader.construct_scalar(node)
    return AskPrompter(value)

##--------------------------------------------------------------#
## Configuration Functions                                      #
##--------------------------------------------------------------#

def get_cliopts(args):
    opts = {}
    for key in ['inpath', 'outpath', 'execute']:
        val = args.get("--" + key)
        if val:
            opts[key] = val
    cmd = [c for c in ['check','debug','make','run'] if args.get(c)]
    if cmd:
        opts['command'] = cmd[0]
    opts['runargs'] = args.get('runargs', [])
    return opts

def get_defopts(dfltdict):
    opts = {}
    if "__opt__" in dfltdict.keys():
        for key in ['execute', 'command']:
            opts[key] = (dfltdict.get('__opt__', {}) or {}).get(key)
        for key in ['outpath']:
            val = (dfltdict.get('__opt__', {}) or {}).get(key)
            if type(val) != list:
                val = _tolist_no_none(val)
            opts[key] = val
        # TODO: Clean up, perhaps make function that can be called by OptLoader.
        for key in ['inpath']:
            # Make paths absolute based on the location of the defaults file.
            # opts[key] = (dfltdict.get('__opt__', {}) or {}).get(key)
            val = (dfltdict.get('__opt__', {}) or {}).get(key)
            if type(val) != list:
                val = [val]
            opts[key] = []
            for v in val:
                if v != None and not op.isabs(v) and not v.startswith("http"):
                    global _DFLTFILE
                    v = op.abspath(op.normpath(op.join(op.dirname(_DFLTFILE), v)))
                opts[key].append(v)
        dfltdict.pop('__opt__')
    return opts

def get_tmpldict(args):
    # Setup custom YAML tags.
    yaml.add_constructor(u'!file', ctor_file)
    yaml.add_constructor(u'!cmd', ctor_cmd)
    yaml.add_constructor(u'!yaml', ctor_yaml)
    yaml.add_constructor(u'!opt', ctor_opt)
    yaml.add_constructor(u'!ask', ctor_ask)
    yaml.add_constructor(u'!py', ctor_py)

    # Prepare template dictionary.
    tmpldict = {}
    dfltfile = args['--defaults']
    if dfltfile:
        global _DFLTFILE
        _DFLTFILE = op.abspath(dfltfile)
        data = fsys.File(dfltfile).read()
        tmpldict = yaml.load(data, Loader=yaml.Loader)
    tmpldict = update(tmpldict, {k:v for k,v in zip(args['--string'], args['VAL'])})
    tmpldict = update(tmpldict, {k:fsys.File(v).read().strip() for k,v in zip(args['--file'], args['PATH'])})

    # Handle nested dictionaries.
    topop = []
    tmplnest = {}
    global KEYSEP
    KEYSEP = args['--keysep']
    if type(tmpldict) != dict:
        qprompt.fatal("Template dictionary is not correct type (%s)!" % (type(tmpldict)))
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

def parse(args):
    """Parses the given arguments into a template dictionary."""
    if args.get('INPATH'):
        args['--defaults'] = args['INPATH']
        if not op.isfile(args['--defaults']):
            qprompt.fatal("Given path could not be found: `%s`" % (args['--defaults']))
    tmpldict = get_tmpldict(args)
    utildict = get_defopts(tmpldict)
    utildict.update(get_cliopts(args))
    if args.get('--defaults') and not utildict.get('command'):
        utildict['command'] = "run"
    for key in ["inpath", "outpath"]:
        if key not in utildict.keys():
            utildict[key] = []
        elif type(utildict[key]) != list:
            utildict[key] = _tolist_no_none(utildict[key])
    while len(utildict['outpath']) < len(utildict['inpath']):
        utildict['outpath'].append(None)
    return utildict, tmpldict

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    pass
