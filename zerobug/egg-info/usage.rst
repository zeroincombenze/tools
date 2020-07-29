
Test main file (usually is called `all_tests`) execute the test suite declared
in source file. If no test list declared, it searches for test runner files
named 'test_[0-9]\*' executed in sorted order.

Test suite is a collection of test case named 'test_[0-9]\*'
executed in sorted order.

Because *zerobug* can show total number of unit test to execute, it run tests
in 2 passes. In the first pass it counts tests, in second pass executes really
it.

::

    usage: zerobug [-h] [-b] [-C] [-e] [-J] [-k] [-l file] [-N] [-n] [-O] [-q]
                   [-r number] [-s number] [-V] [-v] [-x] [-X] [-z number] [-0]
                   [-1] [-3]

    Regression test on clodoo

    optional arguments:
      -h, --help            show this help message and exit
      -b, --debug           trace msgs in zerobug.tracehis
      -C, --no-coverage     run tests without coverage
      -e, --echo            enable echoing even if not interactive tty
      -J                    load travisrc
      -k, --keep            keep current logfile
      -l file, --logname file
                            set logfile name
      -N, --new             create new logfile
      -n, --dry-run         count and display # unit tests
      -O                    load odoorc
      -q, --quiet           run tests without output (quiet mode)
      -r number, --restart number
                            set to counted tests, 1st one next to this
      -s number, --start number
                            deprecated
      -V, --version         show program's version number and exit
      -v, --verbose         verbose mode
      -x, --qsanity         like -X but run silently
      -X, --esanity         execute test library sanity check and exit
      -z number, --end number
                            display total # tests when execute them
      -0, --no-count        no count # unit tests
      -1, --coverage        run tests for coverage (obsolete)
      -3, --python3         use python3
