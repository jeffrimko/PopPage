:: Builds a Windows EXE from the Python scripts.
:: **Dependencies**:
:: PyInstaller must be installed and on the PATH.

::=============================================================::
:: DEVELOPED 2015, REVISED 2015, Jeff Rimko.                   ::
::=============================================================::

:: Set up environment.
@set TITLE=%~n0 "%~dp0"
@cd /d %~dp0 && echo off && title %TITLE%

::=============================================================::
:: SECTION: Global Definitions                                 ::
::=============================================================::

:: Output directory for build.
set OUTDIR=__output__

::=============================================================::
:: SECTION: Main Body                                          ::
::=============================================================::

mkdir %OUTDIR% 2>NUL
pyinstaller poppage.spec
mv build %OUTDIR% 2>NUL
mv dist %OUTDIR% 2>NUL
mv *.log %OUTDIR% 2>NUL
exit /b 0
