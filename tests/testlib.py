"""Provides a library to aid testing."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#


import os
import os.path as op
import random
from string import ascii_uppercase
import subprocess
import sys
import unittest
from time import sleep

from auxly.filesys import File, delete, makedirs, countfiles
import auxly.shell as sh

# Allows development version of library to be used instead of installed.
appdir = op.normpath(op.join(op.abspath(op.dirname(__file__)), r"../app"))
sys.path.insert(0, appdir)

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

OUTDIR = "./__output__"
OUTFILE = OUTDIR + "/outfile.txt"

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class BaseTest(unittest.TestCase):
    def setUp(test):
        makedirs(OUTDIR)
    def tearDown(test):
        super(BaseTest, test).tearDown()
        while op.exists("./__output__"):
            # NOTE: This is a hacky fix to avoid Dropbox related error.
            try: delete("./__output__")
            except: pass

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

#: Random uppercase string of length x.
getrands = lambda x: "".join(random.choice(ascii_uppercase) for _ in range(x))

def call(args):
    sh.call("python ../app/poppage.py " + args)
