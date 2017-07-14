from os.path import isfile
from setuptools import setup, find_packages

setup(
    name = "poppage",
    version = "0.2.0-alpha",
    author = "Jeff Rimko",
    author_email = "jeffrimko@gmail.com",
    description = "TODO",
    license = "MIT",
    keywords = "TODO",
    url = "https://github.com/jeffrimko/PopPage",
    py_modules=["poppage"],
    scripts=["poppage.py","poppage.bat"],
    long_description=open("README.rst").read() if isfile("README.rst") else "",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3"
    ],
)
