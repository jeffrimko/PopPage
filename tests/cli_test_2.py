"""Tests script run CLI functionality."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from testlib import *

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class TestCase(BaseTest):

    def test_cli_1(test):
        """Check for basic run CLI functionality."""
        call('run --inpath ./templates/t5.jinja2 --outpath out.py --execute "python {{outpath}}" --string filename foo.txt --string text bar')
        test.assertTrue(op.isfile("__output__/foo.txt"))
        test.assertFalse(op.isfile("__output__/out.py"))
        test.assertEqual(File("__output__/foo.txt").read(), "bar")

    def test_cli_2(test):
        """Check for basic run CLI functionality with defaults."""
        call("run --defaults defaults/d4.yaml")
        test.assertTrue(op.isfile("__output__/foo.txt"))
        test.assertFalse(op.isfile("__output__/out.py"))
        test.assertEqual(File("__output__/foo.txt").read(), "bar")

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
