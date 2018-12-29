"""Tests the make() function."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from testlib import *

from poppage import make

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class TestCase(BaseTest):

    def test_make_1(test):
        make("./templates/t1.jinja2", {'name':"Mister"}, OUTFILE)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister!" + os.linesep)

    def test_make_2(test):
        make("./templates/t2.jinja2", {'name':{'first':"Mister",'last':"Bob"}}, OUTFILE)
        test.assertEqual(File(OUTFILE).read(), "Hello Mister Bob!" + os.linesep)

    def test_make_3(test):
        makedirs("mytemp")
        test.assertFalse(op.isfile("mytemp/t2.jinja2"))
        make("./templates/t2.jinja2", {'name':{'first':"Mister",'last':"Bob"}}, "mytemp")
        test.assertTrue(op.isfile("mytemp/t2.jinja2"))
        delete("mytemp")

    def test_make_4(test):
        test.assertFalse(op.isfile("mytemp"))
        make("./templates/t2.jinja2", {'name':{'first':"Mister",'last':"Bob"}}, "mytemp")
        test.assertTrue(op.isfile("mytemp"))
        delete("mytemp")

    def test_make_5(test):
        makedirs("Mister")
        test.assertFalse(op.isfile("Mister/t2.jinja2"))
        make("./templates/t2.jinja2", {'name':{'first':"Mister",'last':"Bob"}}, "{{name.first}}")
        test.assertTrue(op.isfile("Mister/t2.jinja2"))
        delete("Mister")

    def test_make_6(test):
        test.assertFalse(op.isfile("Bob.txt"))
        make("./templates/t2.jinja2", {'name':{'first':"Mister",'last':"Bob"}}, "{{name.last}}.txt")
        test.assertTrue(op.isfile("Bob.txt"))
        delete("Bob.txt")

    def test_make_7(test):
        makedirs("Mister")
        test.assertFalse(op.isfile("Mister/Bob.txt"))
        make("./templates/t2.jinja2", {'name':{'first':"Mister",'last':"Bob"}}, "{{name.first}}/{{name.last}}.txt")
        test.assertTrue(op.isfile("Mister/Bob.txt"))
        delete("Mister")

    def test_make_8(test):
        make("./templates/t2.jinja2", {'name':{'first':"Mister",'last':"Bob"}}, "{{name.first}}/{{name.last}}.txt")
        test.assertTrue(op.isfile("Mister/Bob.txt"))
        delete("Mister")

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    unittest.main()
