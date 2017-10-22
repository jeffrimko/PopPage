"""Tests script make CLI call."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from testlib import *

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class TestCase(BaseTest):

    def test_cli_1(test):
        """Check for basic make CLI functionality."""
        call("make --inpath ./templates/t1.jinja2 --outpath %s --string name Mister" % (OUTFILE))
        test.assertEqual(File(OUTFILE).read(), "Hello Mister!")

    def test_cli_2(test):
        """Check for basic make CLI functionality."""
        args = "--string name::first Mister --string name::last Bob"
        call("make --inpath ./templates/t2.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob!")

    def test_cli_3(test):
        """Check for basic make CLI functionality."""
        args = "--string num five --string name::first Mister --string name::last Bob"
        call("make --inpath ./templates/t3.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob, high five!")

    def test_cli_4(test):
        """Check for basic make CLI functionality."""
        args = "--defaults ./defaults/d1.yaml"
        call("make --inpath ./templates/t3.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob, high five!")

    def test_cli_5(test):
        """Check for basic make CLI functionality."""
        args = "--defaults ./defaults/d2.yaml"
        call("make --inpath ./templates/t4.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(File(OUTFILE).read(), "foo,bar,baz")

    def test_cli_6(test):
        """Check for basic make CLI functionality."""
        args = "--defaults ./defaults/d3.yaml"
        call("make --inpath ./templates/t2.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob!")

    def test_cli_7(test):
        """Check for basic make CLI functionality with defaults."""
        call("make --defaults ./defaults/d4.yaml")
        test.assertTrue(op.isfile("./__output__/out.py"))

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
