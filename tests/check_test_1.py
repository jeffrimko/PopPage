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
        """Basic check functionality."""
        tvars = check("./templates/t1.jinja2")
        test.assertEqual(sorted(tvars), ["name"])

    def test_check_2(test):
        """Basic check functionality."""
        tvars = check("./templates/t2.jinja2")
        test.assertEqual(sorted(tvars), ["name::first", "name::last"])

    def test_check_3(test):
        """Basic check functionality."""
        tvars = check("./templates/t3.jinja2")
        test.assertEqual(sorted(tvars), ["name::first", "name::last", "num"])

    def test_check_4(test):
        """Basic check functionality."""
        tvars = check("./templates/t4.jinja2")
        test.assertEqual(sorted(tvars), ["items"])

    def test_check_5(test):
        """Basic check functionality."""
        poppage.KEYSEP = "->"
        tvars = check("./templates/t3.jinja2")
        test.assertEqual(sorted(tvars), ["name->first", "name->last", "num"])

    def test_check_6(test):
        """GitHub check functionality."""
        poppage.KEYSEP = "::"
        tvars = check("https://github.com/solarnz/cookiecutter-avr")
        if not tvars:
            print("Skipping check...")
            return
        evars = []
        evars.append("cookiecutter::full_name")
        evars.append("cookiecutter::repo_name")
        evars.append("cookiecutter::year")
        test.assertEqual(sorted(tvars), sorted(evars))

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
