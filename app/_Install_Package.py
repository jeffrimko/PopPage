##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import auxly

##==============================================================#
## SECTION: Function Definitions                                #
##==============================================================#

def generate_readme():
    auxly.shell.call("asciidoctor -b docbook ../README.adoc")
    auxly.shell.call("pandoc -r docbook -w rst -o README.rst ../README.xml")
    auxly.filesys.delete("../README.xml")

def cleanup_readme():
    auxly.filesys.delete("README.rst")

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    generate_readme()
    auxly.shell.call("pip install -e .")
    cleanup_readme()
