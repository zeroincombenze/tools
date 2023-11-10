This library can run unit test of target package software.
Supported languages are *python* (through z0testlib.py) and *bash* (through z0testrc)

*zerobug* supports test automation, aggregation of tests into collections
and independence of the tests from the reporting framework.
The *zerobug* module provides all code that make it easy to support testing
both for python programs both for bash scripts.
*zerobug* shows execution test with a message like "n/tot message"
where *n* is current unit test and *tot* is the total unit test to execute,
that is a sort of advancing test progress.

You can use z0bug_odoo that is the odoo integration to test Odoo modules.

*zerobug* is built on follow concepts:

* test main - it is a main program to executes all test runners
* test runner - it is a program to executes one or more test suites
* test suite - it is a collection of test cases
* test case - it is a smallest unit test

The main file is the command **zerobug** of this package; it searches for test runner
files named `[id_]test_` where 'id' is the shor name of testing package.

Test suite is a collection of test case named `test_[0-9]+` inside the runner file,
executed in sorted order.

Every suit can contains one or more test case, the smallest unit test;
every unit test terminates with success or with failure.
