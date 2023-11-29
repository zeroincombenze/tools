This library can run unit test of software target package.
Supported languages are *python* (through z0testlib.py) and *bash* (through z0testrc)

*zerobug* was born to supports test automation, aggregation of tests into collections
and independence of the tests from the reporting framework.
Currently is becoming an improvements of *python unittest2* but still run bash tests.

The command **zerobug** of this package runs tests: it searches for test runner
files named ``test_`` (see -p switch).

Test suite is a collection of test case named ``test_[0-9]+`` inside the runner file,
executed in sorted order.

Every suite can contains one or more test case, the smallest unit test;
every unit test terminates with success or with failure.

*zerobug* is full integrated with coverage and travis-ci.
