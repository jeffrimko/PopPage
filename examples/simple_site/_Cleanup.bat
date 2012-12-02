:: Removes generated project files.
:: __Dependencies__: None.

:: Set up environment.
@set TITLE=%~n0 "%~dp0"
@cd /d %~dp0 && title %TITLE% && echo off

rm -rf _output
