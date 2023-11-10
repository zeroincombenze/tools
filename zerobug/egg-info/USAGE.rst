::

    usage: zerobug [-h] [-B] [-C] [-e] [-f] [-J] [-k] [-l file] [-N] [-n] [-O] [-p file_list] [-Q] [-q] [-R] [-r number]
                   [-s number] [-V] [-v] [-x] [-X] [-z number] [-0] [-1] [-2] [-3]

    Regression test on zerobug

    optional arguments:
      -h, --help            show this help message and exit
      -B, --debug           run tests in debug mode
      -C, --no-coverage     run tests without coverage
      -e, --echo            enable echoing even if not interactive tty (deprecated)
      -f, --failfast        Stop on first fail or error
      -J                    load travisrc (deprecated)
      -k, --keep            keep current logfile (deprecated)
      -l file, --logname file
                            set logfile name (deprecated)
      -N, --new             create new logfile (deprecated)
      -n, --dry-run         count and display # unit tests (deprecated)
      -O                    load odoorc (deprecated)
      -p file_list, --search-pattern file_list
                            Pattern to match tests, comma separated ('test*.py' default)
      -Q, --count           count # unit tests (deprecated)
      -q, --quiet           run tests without output (quiet mode)
      -R, --run-inner       inner mode w/o final messages
      -r number, --restart number
                            restart count next to number
      -s number, --start number
                            deprecated
      -V, --version         show program's version number and exit
      -v, --verbose         verbose mode
      -x, --qsanity         like -X but run silently (deprecated)
      -X, --esanity         execute test library sanity check and exit (deprecated)
      -z number, --end number
                            display total # tests when execute them
      -0, --no-count        no count # unit tests (deprecated)
      -1, --coverage        run tests for coverage (deprecated)
      -2, --python2         use python2 (deprecated)
      -3, --python3         use python3 (deprecated)

    © 2015-2023 by SHS-AV s.r.l. - https://zeroincombenze-tools.readthedocs.io/en/latest/zerobug