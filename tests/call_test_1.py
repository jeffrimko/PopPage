"""Tests script make CLI call."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from testlib import *

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class TestCase(BaseTest):

    def test_call_1(test):
        """Check for basic make call functionality."""
        call("make --inpath ./templates/t1.jinja2 --outpath %s --string name Mister" % (OUTFILE))
        test.assertEqual(File(OUTFILE).read(), "Hello Mister!")

    def test_call_2(test):
        """Check for basic make call functionality."""
        args = "--string name::first Mister --string name::last Bob"
        call("make --inpath ./templates/t2.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob!")

    def test_call_3(test):
        """Check for basic make call functionality."""
        args = "--string num five --string name::first Mister --string name::last Bob"
        call("make --inpath ./templates/t3.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob, high five!")

    def test_call_4(test):
        """Check for basic make call functionality."""
        args = "--defaults ./defaults/d1.yaml"
        call("make --inpath ./templates/t3.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob, high five!")

    def test_call_5(test):
        """Check for basic make call functionality."""
        args = "--defaults ./defaults/d2.yaml"
        call("make --inpath ./templates/t4.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(File(OUTFILE).read(), "foo,bar,baz")

    def test_call_6(test):
        """Check for basic make call functionality."""
        args = "--defaults ./defaults/d3.yaml"
        call("make --inpath ./templates/t2.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob!")

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
