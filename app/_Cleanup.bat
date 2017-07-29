:: Removes all generated project files.
:: **Dependencies**: None

::=============================================================::
:: COPYRIGHT 2015, REVISED 2015, Jeff Rimko.                   ::
::=============================================================::

:: Set up environment.
@set TITLE=%~n0 "%~dp0"
@cd /d %~dp0 && echo off && title %TITLE%

::=============================================================::
:: SECTION: Main Body                                          ::
::=============================================================::

rd /S /Q __output__
rd /S /Q poppage.egg-info
rd /S /Q dist
rd /S /Q build
del /S /Q *.log
del /S /Q *.pyc
