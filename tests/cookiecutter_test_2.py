"""Tests for cookiecutter compatibility."""

##==============================================================#
## SECTION: Imports                                             #
##==============================================================#

from testlib import *

import poppage
from poppage import check, make

##==============================================================#
## SECTION: Global Definitions                                  #
##==============================================================#

URLS = [
        # "https://github.com/avelino/cookiecutter-bottle",
        # "https://github.com/openstack-dev/cookiecutter",
        # "https://github.com/sloria/cookiecutter-docopt",
        # "https://github.com/pythonhub/cookiecutter-quokka-module",
        # "https://github.com/hackebrot/cookiecutter-kivy",
        # "https://github.com/hackebrot/cookiedozer",
        # "https://github.com/ionelmc/cookiecutter-pylibrary",
        # "https://github.com/robinandeer/cookiecutter-pyvanguard",
        # "https://github.com/pybee/Python-iOS-template",
        # "https://github.com/pybee/Python-Android-template",
        # "https://github.com/fulfilio/cookiecutter-tryton",
        # "https://github.com/pytest-dev/cookiecutter-pytest-plugin",
        # "https://github.com/vintasoftware/cookiecutter-tapioca",
        # "https://github.com/drgarcia1986/cookiecutter-muffin",
        # "https://github.com/OctoPrint/cookiecutter-octoprint-plugin",
        # "https://github.com/tokibito/cookiecutter-funkload-friendly",
        # "https://github.com/mdklatt/cookiecutter-python-app",
        # "https://github.com/morepath/morepath-cookiecutter",
        # "https://github.com/Springerle/hovercraft-slides",
        # "https://github.com/xguse/cookiecutter-snakemake-analysis-pipeline",
        # "https://github.com/ivanlyon/cookiecutter-py3tkinter",
        # "https://github.com/mandeepbhutani/cookiecutter-pyqt5",
        # "https://github.com/aeroaks/cookiecutter-pyqt4",
        # "https://github.com/laerus/cookiecutter-xontrib",
        # "https://github.com/conda/cookiecutter-conda-python",
        # "https://github.com/mckaymatt/cookiecutter-pypackage-rust-cross-platform-publish",
        # "https://github.com/pydanny/cookiecutter-django",
        # "https://github.com/agconti/cookiecutter-django-rest",
        "https://github.com/marcofucci/cookiecutter-simple-django",
        # "https://github.com/legios89/django-docker-bootstrap",
        # "https://github.com/pydanny/cookiecutter-djangopackage",
        # "https://github.com/palazzem/cookiecutter-django-cms",
        "https://github.com/wildfish/cookiecutter-django-crud",
        # "https://github.com/lborgav/cookiecutter-django",
        # "https://github.com/pbacterio/cookiecutter-django-paas",
        # "https://github.com/jpadilla/cookiecutter-django-rest-framework",
        # "https://github.com/dolphinkiss/cookiecutter-django-aws-eb",
        # "https://github.com/torchbox/cookiecutter-wagtail",
        # "https://github.com/chrisdev/wagtail-cookiecutter-foundation",
        "https://github.com/solarnz/cookiecutter-avr"]

##==============================================================#
## SECTION: Class Definitions                                   #
##==============================================================#

class TestCase(BaseTest):

    def test_cookiecutter_1(test):
        """GitHub check functionality."""
        for url in URLS:
            print("URL = {0}".format(url))
            tvars = check(url)
            if not tvars:
                return
            rvars = {t.split("::")[1]:getrands(6) for t in tvars}
            print("vars = {0}".format(rvars))
            makedirs(OUTDIR)
            test.assertTrue(0 == countfiles(OUTDIR, recurse=True))
            test.assertTrue(make(url, {'cookiecutter':rvars}, OUTDIR))
            test.assertTrue(0 < countfiles(OUTDIR, recurse=True))
            delete(OUTDIR)

##==============================================================#
## SECTION: Main Body                                           #
##==============================================================#

if __name__ == '__main__':
    # unittest.main()
    print("SKIPPING TEST FOR NOW.")
