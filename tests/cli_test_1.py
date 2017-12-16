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
        errcode = call("make --inpath ./templates/t1.jinja2 --outpath %s --string name Mister" % (OUTFILE))
        test.assertEqual(0, errcode)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister!")

    def test_cli_2(test):
        args = "--string name::first Mister --string name::last Bob"
        errcode = call("make --inpath ./templates/t2.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(0, errcode)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob!")

    def test_cli_3(test):
        args = "--string num five --string name::first Mister --string name::last Bob"
        errcode = call("make --inpath ./templates/t3.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(0, errcode)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob, high five!")

    def test_cli_4(test):
        args = "--defaults ./defaults/d1.yaml"
        errcode = call("make --inpath ./templates/t3.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(0, errcode)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob, high five!")

    def test_cli_5(test):
        args = "--defaults ./defaults/d2.yaml"
        errcode = call("make --inpath ./templates/t4.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(0, errcode)
        test.assertEqual(File(OUTFILE).read(), "foo,bar,baz")

    def test_cli_6(test):
        args = "--defaults ./defaults/d3.yaml"
        errcode = call("make --inpath ./templates/t2.jinja2 --outpath %s %s" % (OUTFILE, args))
        test.assertEqual(0, errcode)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob!")

    def test_cli_7(test):
        errcode = call("make --defaults ./defaults/d4.yaml")
        test.assertEqual(0, errcode)
        test.assertTrue(op.isfile("./__output__/out.py"))

    def test_cli_8(test):
        errcode = call("make")
        test.assertEqual(1, errcode)

    def test_cli_9(test):
        errcode = call("make --defaults ./defaults/d5.yaml")
        test.assertEqual(0, errcode)
        test.assertTrue(op.isfile("./__output__/out.py"))

    def test_cli_10(test):
        errcode = call("make --defaults defaults-d1.yaml")
        test.assertEqual(0, errcode)
        test.assertTrue(op.isfile("./__output__/out.py"))

    def test_cli_11(test):
        errcode = call("make --defaults defaults/d6.yaml")
        test.assertEqual(0, errcode)
        test.assertTrue(op.isdir("./__output__/foo"))
        test.assertTrue(op.isfile("./__output__/foo/bar.txt"))

    def test_cli_12(test):
        errcode = call("make --defaults defaults/d6.yaml --string mydir baz")
        test.assertEqual(0, errcode)
        test.assertTrue(op.isdir("./__output__/baz"))
        test.assertTrue(op.isfile("./__output__/baz/bar.txt"))

    def test_cli_13(test):
        errcode = call("make --defaults defaults/d6.yaml --outpath __output__/baz")
        test.assertEqual(0, errcode)
        test.assertTrue(op.isdir("./__output__/baz/foo"))
        test.assertTrue(op.isfile("./__output__/baz/foo/bar.txt"))

    def test_cli_14(test):
        with Cwd("__output__"):
            errcode = call("make --defaults ../defaults/d7.yaml", app_path="../../app")
            test.assertEqual(0, errcode)
            test.assertTrue(op.isdir("./foo"))
            test.assertTrue(op.isfile("./foo/bar.txt"))
            test.assertEqual(File("./foo/bar.txt").read(), "hello baz!")

    def test_cli_15(test):
        with Cwd("__output__"):
            errcode = call("../defaults/d7.yaml", app_path="../../app")
            test.assertEqual(0, errcode)
            test.assertTrue(op.isdir("./foo"))
            test.assertTrue(op.isfile("./foo/bar.txt"))
            test.assertEqual(File("./foo/bar.txt").read(), "hello baz!")

    def test_cli_16(test):
        errcode = call("defaults/d8.yaml")
        test.assertEqual(0, errcode)

    def test_cli_17(test):
        errcode = call("defaults/d9.yaml")
        test.assertEqual(0, errcode)

    def test_cli_18(test):
        with Cwd("templates"):
            errcode = call("make --inpath foo", app_path="../../app")
            test.assertEqual(1, errcode)

    def test_cli_19(test):
        with Cwd("templates"):
            errcode = call("make --inpath t1.jinja2", app_path="../../app")
            test.assertEqual(0, errcode)

    def test_cli_20(test):
        with Cwd("templates"):
            errcode = call("make --inpath t1.jinja2 --outpath t1.jinja2", app_path="../../app")
            test.assertEqual(1, errcode)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
