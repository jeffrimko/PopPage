"""Tests script CLI arguments."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from testlib import *
from utilconf import parse

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class TestCase(BaseTest):

    def test_args_1(test):
        args = get_args()
        args['--inpath'] = "foo.txt"
        utildict, tmpldict = parse(args)
        test.assertEqual(utildict['inpath'], ["foo.txt"])
        test.assertEqual(tmpldict, {})

    def test_args_2(test):
        args = get_args()
        args['--defaults'] = "defaults/d4.yaml"
        args['--inpath'] = "foo.txt"
        args['--execute'] = "bar"
        utildict, tmpldict = parse(args)
        test.assertEqual(utildict['inpath'], ["foo.txt"])
        test.assertEqual(utildict['execute'], "bar")
        test.assertEqual(utildict['outpath'], ["__output__/out.py"])

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
