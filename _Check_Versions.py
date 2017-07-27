##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

import verace

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

VERCHK = verace.VerChecker("PopPage", __file__)
VERCHK.include(r"app\setup.py", match="version = ", splits=[('"',1)])
VERCHK.include(r"app\poppage.py", match="__version__ = ", splits=[('"',1)])
VERCHK.include(r"CHANGELOG.adoc", match="poppage-", splits=[("-",1),(" ",0)], updatable=False)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    VERCHK.prompt()
