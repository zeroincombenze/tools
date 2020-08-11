Zeroincombenze® continuous testing framework for python and bash programs
-------------------------------------------------------------------------

This library can run unit test of target package software.
Supported languages are *python* (through z0testlib.py) and *bash* (through z0testrc)

*zerobug* supports test automation, aggregation of tests into collections
and independence of the tests from the reporting framework.
The *zerobug* module provides all code that make it easy to support testing
both for python programs both for bash scripts.
*zerobug* differs from pytest standard library because show execution test with
a message like "n/tot message" where *n* is current unit test and *tot* is the
total unit test to execute, that is a sort of advancing test progress.

*zerobug* is built on follow concepts:

* test main - it is a main program to executes all test runners
* test runner - it is a program to executes one or more test suites
* test suite - it is a collection of test cases
* test case -it is a smallest unit test

You can you z0bug_odoo that is teh odoo integration to test Odoo modules.


