"""Tests the check() function."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from testlib import *

import poppage
from poppage import check

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class TestCase(BaseTest):

    def test_check_1(test):
        """Check for basic check functionality."""
        tvars = check("./templates/t1.jinja2")
        test.assertEqual(sorted(tvars), ["name"])

    def test_check_2(test):
        """Check for basic check functionality."""
        tvars = check("./templates/t2.jinja2")
        test.assertEqual(sorted(tvars), ["name::first", "name::last"])

    def test_check_3(test):
        """Check for basic check functionality."""
        tvars = check("./templates/t3.jinja2")
        test.assertEqual(sorted(tvars), ["name::first", "name::last", "num"])

    def test_check_4(test):
        """Check for basic check functionality."""
        tvars = check("./templates/t4.jinja2")
        test.assertEqual(sorted(tvars), ["items"])

    def test_check_4(test):
        """Check for basic check functionality."""
        poppage.KEYSEP = "->"
        tvars = check("./templates/t3.jinja2")
        test.assertEqual(sorted(tvars), ["name->first", "name->last", "num"])

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
