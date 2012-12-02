:: Generates the example website.
:: __Dependencies__: Python on PATH.

::=============================================================::
:: SECTION: Environment Setup                                  ::
::=============================================================::

@set TITLE=%~n0 "%~dp0"
@cd /d %~dp0 && echo off && title %TITLE%

::=============================================================::
:: SECTION: Global Definitions                                 ::
::=============================================================::

:: Define directory variables.
set OUTDIR=_output

:: Command used to generate a page.
set GENCMD=python ..\..\app\poppage.py

:: Command used to generate timestamp string.
set TSCMD=python -c "import time; print time.strftime('%%d %%B %%Y %%I:%%M%%p')"

::=============================================================::
:: SECTION: Main Body                                          ::
::=============================================================::

:: Make output directory.
md %OUTDIR% 2>NUL

:: Get the timestamp for this build.
for /f "delims=" %%a in ('%TSCMD%') do set TIMESTAMP=%%a

:: Generate pages.
call:GenPageMarkdown ^
    "Foo" ^
    content/foo.md ^
    templates/page-html.jinja2 ^
    foo.html
call:GenPageMarkdown ^
    "Bar" ^
    content/bar.md ^
    templates/page-html.jinja2 ^
    bar.html

exit /b 0

::=============================================================::
:: SECTION: Function Definitions                               ::
::=============================================================::

::-------------------------------------------------------------::
:: Generates a page from a Markdown source.
::-------------------------------------------------------------::
:GenPageMarkdown
set TITLE=%~1
set SRC=%~2
set NAME=%~n2
set TMPL=%~3
set URL=%~4
echo Generating %URL%...
pandoc %SRC% > %OUTDIR%/%NAME%.temp
%GENCMD% %TMPL% ^
    --string="%TITLE%" title ^
    --string="%TIMESTAMP%" timestamp ^
    --file=%OUTDIR%/%NAME%.temp content ^
    > %OUTDIR%/%URL%
del /S /Q *.temp 1>NUL
goto:eof
