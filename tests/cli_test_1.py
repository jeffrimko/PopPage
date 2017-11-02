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
        retval = call("make --inpath ./templates/t1.jinja2 --outpath %s --string name Mister" % (OUTFILE))
        test.assertEqual(0, retval)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister!")

    def test_cli_2(test):
        """Check for basic make CLI functionality."""
        args = "--string name::first Mister --string name::last Bob"
        retval = call("make --inpath ./templates/t2.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(0, retval)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob!")

    def test_cli_3(test):
        """Check for basic make CLI functionality."""
        args = "--string num five --string name::first Mister --string name::last Bob"
        retval = call("make --inpath ./templates/t3.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(0, retval)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob, high five!")

    def test_cli_4(test):
        """Check for basic make CLI functionality."""
        args = "--defaults ./defaults/d1.yaml"
        retval = call("make --inpath ./templates/t3.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(0, retval)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob, high five!")

    def test_cli_5(test):
        """Check for basic make CLI functionality."""
        args = "--defaults ./defaults/d2.yaml"
        retval = call("make --inpath ./templates/t4.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(0, retval)
        test.assertEqual(File(OUTFILE).read(), "foo,bar,baz")

    def test_cli_6(test):
        """Check for basic make CLI functionality."""
        args = "--defaults ./defaults/d3.yaml"
        retval = call("make --inpath ./templates/t2.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(0, retval)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob!")

    def test_cli_7(test):
        """Check for basic make CLI functionality with defaults."""
        retval = call("make --defaults ./defaults/d4.yaml")
        test.assertEqual(0, retval)
        test.assertTrue(op.isfile("./__output__/out.py"))

    def test_cli_8(test):
        """Check for basic make CLI functionality with defaults."""
        retval = call("make")
        test.assertEqual(1, retval)

    def test_cli_9(test):
        """Check for basic make CLI functionality with defaults."""
        retval = call("make --defaults ./defaults/d5.yaml")
        test.assertEqual(0, retval)
        test.assertTrue(op.isfile("./__output__/out.py"))

    def test_cli_10(test):
        """Check for basic make CLI functionality with defaults."""
        retval = call("make --defaults defaults-d1.yaml")
        test.assertEqual(0, retval)
        test.assertTrue(op.isfile("./__output__/out.py"))

    def test_cli_11(test):
        """Check for basic make CLI functionality with defaults."""
        retval = call("make --defaults defaults/d6.yaml")
        test.assertEqual(0, retval)
        test.assertTrue(op.isdir("./__output__/foo"))
        test.assertTrue(op.isfile("./__output__/foo/bar.txt"))

    def test_cli_12(test):
        """Check for basic make CLI functionality with defaults."""
        retval = call("make --defaults defaults/d6.yaml --string mydir baz")
        test.assertEqual(0, retval)
        test.assertTrue(op.isdir("./__output__/baz"))
        test.assertTrue(op.isfile("./__output__/baz/bar.txt"))

    def test_cli_13(test):
        """Check for basic make CLI functionality with defaults."""
        retval = call("make --defaults defaults/d6.yaml --outpath __output__/baz")
        test.assertEqual(0, retval)
        test.assertTrue(op.isdir("./__output__/baz/foo"))
        test.assertTrue(op.isfile("./__output__/baz/foo/bar.txt"))

    def test_cli_14(test):
        """Check for basic make CLI functionality with defaults."""
        with Cwd("__output__"):
            retval = call("make --defaults ../defaults/d7.yaml", app_path="../../app")
            test.assertEqual(0, retval)
            test.assertTrue(op.isdir("./foo"))
            test.assertTrue(op.isfile("./foo/bar.txt"))
            test.assertEqual(File("./foo/bar.txt").read(), "hello baz!")

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
