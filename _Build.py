##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import os.path as op
from xml.etree import ElementTree

import auxly
import auxly.filesys as fsys
from auxly import shell
from ubuild import main, menu
from qprompt import Menu

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

@menu
def cleanup():
    with fsys.Cwd("app"):
        shell.call("_Cleanup.py")

@menu("v")
def check_version():
    with fsys.Cwd(".", __file__):
        shell.call("_Check_Versions.py")

@menu("t")
def run_tests():
    with fsys.Cwd("tests", __file__):
        shell.call("_Run_Tests.py")

@menu
def package_menu():
    Menu(install_package_locally, upload_to_pypi).main(header="Package")

@menu
def browse_menu():
    def github(): auxly.open("https://github.com/jeffrimko/PopPage")
    def pypi(): auxly.open("https://pypi.org/project/PopPage/")
    def travis(): auxly.open("https://travis-ci.org/jeffrimko/PopPage")
    Menu(github, pypi, travis).main(header="Browse")

def install_package_locally():
    with fsys.Cwd("app", __file__):
        shell.call("_Install_Package.py")

def upload_to_pypi():
    with fsys.Cwd("app", __file__):
        shell.call("_Upload_PyPI.py")

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    main()
