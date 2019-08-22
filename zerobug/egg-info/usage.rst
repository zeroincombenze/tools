
Test main file (usually is called 'all_tests') execute the test suite declared
in source file. If no test list declared, it searches for test runner files
named 'test_[0-9]\*' executed in sorted order.

Test suite is a collection of test case named 'test_[0-9]\*'
executed in sorted order.

Because *zerobug* can show total number of unit test to execute, it run tests
in 2 passes. In the first pass it counts tests, in second pass executes really
it.

Every unit test file may be called with follows switches:

  -h, --help            show this help message and exit
  -b, --debug           run tests in debug mode
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
                        set to counted tests, 1st one next to this
  -V, --version         show program's version number and exit
  -v, --verbose         verbose mode
  -x, --qsanity         like -X but run silently
  -X, --esanity         execute test library sanity check and exit
  -z number, --end number
                        display total # tests when execute them
  -0, --no-count        no count # unit tests
  -1, --coverage        run tests for coverage
  -3, --python3         use python3

  (w/o switches) do run test and return test result


Package, test environment and deployment are:

    ./                  Package directory
                        inside python test program is self.pkg_dir
                        inside bash test script is $RUNDIR
    ./tests             Unit test directory
                        should contains one of 'all_tests' or 'test_PKGNAME'
                        inside python test program is self.test_dir
                        inside bash test script is $TESTDIR
    ./tests/z0testlib   Python file unit test library from zerobug package
                        may be not present if zerobug python package installed
    ./tests/z0testrc    Bash file unit test library from zerobug package
                        may be not present if zerobug python package installed
                        inside bash test script is $Z0TLIBDIR
    ./tests/z0librc     Local bash script library for bash scripts;
                        Could be in user root directory or in /etc directory
                        inside bash test script is $Z0LIBDIR
    ./_travis           Interface to travis emulator if present (obsolete);
                        it used in local host to emulate some travis functions
                        inside bash test script is $TRAVISDIR

Unit test can run in package directory or in ./tests directory of package.


Every test can inquire internal context.

    this_fqn      parent caller full qualified name (i.e. /opt/odoo/z0bug.pyc)
    this          parent name, w/o extension (i.e. z0bug)
    ctr;          test counter [both bash and python tests]
    dry_run       dry-run (do nothing) [opt_dry_run in bash test]          "-n"
    esanity       True if required sanity check with echo                  "-X"
    max_test      # of tests to execute [both bash and python tests]       "-z"
    min_test      # of test executed before this one                       "-r"
    on_error      behavior after error, 'continue' or 'raise' (default)
    opt_echo      True if echo test result onto std output                 "-e"
    opt_new       new log file [both bash and python tests]                "-N"
    opt_noctr     do not count # tests [both bash and python tests]        "-0"
    opt_verbose   show messages during execution                           "-v"
    logfn         real trace log file name from switch                     "-l"
    qsanity       True if required sanity check w/o echo                   "-x"
    run4cover     Run tests for coverage (use coverage run rather python)  "-1"
    python3       Execute test in python3                                  "-3"
    run_daemon    True if execution w/o tty as stdio
    run_on_top    Top test (not parent)
    run_tty       Opposite of run_daemon
    tlog          default tracelog file name
    _run_autotest True if running auto-test
    _parser       cmd line parser
    _opt_obj      parser obj, to acquire optional switches
    WLOGCMD       override opt_echo; may be None, 'echo', 'echo-1', 'echo-0'
    Z0            this library object

Environment read:

DEV_ENVIRONMENT Name of package; if set test is under travis emulator control

COVERAGE_PROCESS_START
                Name of coverage conf file; if set test is running for coverage

