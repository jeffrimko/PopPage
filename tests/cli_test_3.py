"""Tests script check CLI functionality."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from testlib import *

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class TestCase(BaseTest):

    def test_cli_1(test):
        """Check for basic check CLI functionality."""
        retval = call('check --inpath ./templates/t5.jinja2')
        test.assertEqual(0, retval)

        retval = call('check')
        test.assertEqual(1, retval)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
