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
        retval = call('run --inpath ./templates/t5.jinja2 --outpath out.py --execute "python {{outpath}}" --string filename foo.txt --string text bar')
        test.assertEqual(0, retval)
        test.assertTrue(op.isfile("__output__/foo.txt"))
        test.assertFalse(op.isfile("__output__/out.py"))
        test.assertEqual(File("__output__/foo.txt").read(), "bar")

    def test_cli_2(test):
        retval = call("run --defaults defaults/d4.yaml")
        test.assertEqual(0, retval)
        test.assertTrue(op.isfile("__output__/foo.txt"))
        test.assertFalse(op.isfile("__output__/out.py"))
        test.assertEqual(File("__output__/foo.txt").read(), "bar")

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
