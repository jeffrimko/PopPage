##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from os.path import isfile
from setuptools import setup, find_packages
from platform import system

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

SCRIPTS = []
if "Windows" == system():
    SCRIPTS = ["poppage.bat", "poppage.py"]
if "Linux" == system():
    SCRIPTS = ["poppage"]

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

setup(
    name = "poppage",
    version = "0.6.5",
    author = "Jeff Rimko",
    author_email = "jeffrimko@gmail.com",
    description = "Utility for generating files and directories from templates.",
    license = "MIT",
    keywords = "project-templates file-templates file-generation",
    url = "https://github.com/jeffrimko/PopPage",
    py_modules=["poppage","gitr","utilconf"],
    scripts=SCRIPTS,
    long_description=open("README.rst").read() if isfile("README.rst") else "",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3"
    ],
    install_requires=[
        "auxly",
        "binaryornot",
        "docopt",
        "jinja2",
        "jinja2_time",
        "jinja2schema",
        "pyyaml",
        "qprompt",
        "requests",
   ],
)
