"""Tests for cookiecutter compatibility."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from testlib import *

import poppage
from poppage import check, make

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class TestCase(BaseTest):

    def test_cookiecutter_1(test):
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

    def test_cookiecutter_2(test):
        test.assertFalse(op.isfile("MyTest.c"))
        url = "https://github.com/solarnz/cookiecutter-avr/blob/master/%7B%7Bcookiecutter.repo_name%7D%7D/%7B%7Bcookiecutter.repo_name%7D%7D.c"
        test.assertTrue(make(url, {'cookiecutter':{'repo_name':"MyTest"}}))
        test.assertTrue(op.isfile("MyTest.c"))
        delete("MyTest.c")

    def test_cookiecutter_3(test):
        test.assertFalse(op.isfile("AnotherName.c"))
        url = "https://github.com/solarnz/cookiecutter-avr/blob/master/%7B%7Bcookiecutter.repo_name%7D%7D/%7B%7Bcookiecutter.repo_name%7D%7D.c"
        test.assertTrue(make(url, {'cookiecutter':{'repo_name':"MyTest"}}, "AnotherName.c"))
        test.assertTrue(op.isfile("AnotherName.c"))
        delete("AnotherName.c")

    def test_cookiecutter_4(test):
        url = "https://github.com/solarnz/cookiecutter-avr/tree/master/%7B%7Bcookiecutter.repo_name%7D%7D"
        if not check(url):
            print("Skipping check...")
            return
        tvars = {'cookiecutter':{}}
        tvars['cookiecutter']['full_name'] = "Mister Bob"
        tvars['cookiecutter']['repo_name'] = "MyRepo"
        tvars['cookiecutter']['year'] = 2017
        test.assertFalse(op.isdir("MyRepo"))
        test.assertTrue(make(url, tvars))
        test.assertTrue(op.isdir("MyRepo"))
        delete("MyRepo")

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    # unittest.main()
    print("SKIPPING TEST FOR NOW.")
