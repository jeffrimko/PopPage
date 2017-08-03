##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import os.path as op

import auxly.filesys as fsys
import requests

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

GHAPI = "https://api.github.com/repos/"
GHURL = "https://github.com/"
GHRAW = "https://raw.githubusercontent.com/"

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

def is_github(src):
    if src.startswith(GHAPI):
        return True
    if src.startswith(GHURL):
        return True
    if src.startswith(GHRAW):
        return True
    return False

def prep_url(url):
    """Preps the given URL and returns either an API URL (for directories) or a
    raw content URL (for files)."""
    if url.startswith(GHURL):
        tok = url.split("/")[3:]
        name = tok[-1]
        if "blob" == tok[2]:
            url = GHRAW
            url += "{0}/{1}/{3}/".format(*tok)
            url += "/".join(tok[4:])
        elif "tree" == tok[2]:
            url = GHAPI
            url += "{0}/{1}/contents/".format(*tok)
            url += "/".join(tok[4:])
            url += "?ref=" + tok[3]
    else:
        tok = url.split("/")
        name = tok[-1]
    return url,name

def is_file(url):
    """Checks if the given URL is for a file and returns the filename if so;
    returns None otherwise."""
    url,name = prep_url(url)
    if url.startswith(GHRAW):
        return name

def download(srcurl, dstpath=None):
    """Handles downloading files/dirs from the given GitHub repo URL to the
    given destination path."""
    def download_api(srcurl, dstdir):
        items = requests.get(srcurl).json()
        if op.isfile(dstdir):
            raise Exception("DestDirIsFile")
        fsys.makedirs(dstdir)
        for item in items:
            if "file" == item['type']:
                fpath = op.join(dstdir, item['name'])
                with open(fpath, "w") as fo:
                    fo.write(requests.get(item['download_url']).text)
            else:
                dstdir = op.join(dstdir, item['name'])
                download_api(item['url'], dstdir)
    def download_raw(srcurl, dstfile):
        fsys.makedirs(dstfile)
        if op.isdir(dstfile):
            dstfile = op.join(dstfile, srcurl.split("/")[-1])
        with open(dstfile, "w") as fo:
            fo.write(requests.get(srcurl).text)
    url,name = prep_url(srcurl)
    if not dstpath:
        dstpath = op.join(op.abspath("."), name)
    dstpath = op.abspath(dstpath)
    if url.startswith(GHAPI):
        download_api(url, dstpath)
    else:
        download_raw(url, dstpath)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    pass
