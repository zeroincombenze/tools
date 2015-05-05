@echo off
rem Regression tests for os0 module
rem Version running Windows platform 
set tf=os0_win.rst
set td=tests\
if "%1"=="-h" goto shhelp
if "%1"=="/?" goto shhelp
if "%1"=="/h" goto shhelp
if "%1"=="--help" goto shhelp
if "%1"=="-V" goto shver
if "%1"=="--version" goto shver
if "%1"=="/V" goto shver
if "%1"=="/v" goto shver
goto xec
:shhelp
echo os0 regression tests based on doctest python module
echo Tests end without output; it means worked.
echo Pass -v (not /v) to the script for a detailed log
echo To execute tests, from os0 directory, type:
echo > tests/all_tests [-v] [-V][/V] [-h][/h] [--version] [--help]
echo  where
echo  /h -h --help     this help
echo  -v               verbose mode (lowercase)
echo  /V -V --version  show version (uppercase)
echo.
echo (C) SHS-AV s.r.l. - http://www.shs-av.com
goto xit
:shver
echo Module os0 tests V1.2.1
find "version =" os0.py
goto xit
:xec
python -m doctest %1 %td%\%tf%
python %td%\os0_test.py
:xit
