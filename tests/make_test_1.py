"""Tests the make() function."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from testlib import *

from poppage import make

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class TestCase(BaseTest):

    def test_make_1(test):
        """Check for basic make functionality."""
        make("./templates/t1.jinja2", {'name':"Mister"}, OUTFILE)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister!")

    def test_make_2(test):
        """Check for basic make functionality."""
        make("./templates/t2.jinja2", {'name':{'first':"Mister",'last':"Bob"}}, OUTFILE)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob!")

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
