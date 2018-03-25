"""Tests script debug CLI call."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from testlib import *

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class TestCase(BaseTest):

    def test_cli_debug_1(test):
        errcode = call("defaults/d8.yaml")
        test.assertEqual(0, errcode)

    def test_cli_debug_2(test):
        errcode = call("defaults/d9.yaml")
        test.assertEqual(0, errcode)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
