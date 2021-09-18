::

    usage: zerobug [-h] [-B] [-C] [-e] [-J] [-k] [-l file] [-N] [-n] [-O]
                   [-p file_list] [-q] [-r number] [-s number] [-V] [-v] [-x] [-X]
                   [-z number] [-0] [-1] [-3]

    Regression test on z0bug_odoo

    optional arguments:
      -h, --help            show this help message and exit
      -B, --debug           trace msgs in zerobug.tracehis
      -C, --no-coverage     run tests without coverage
      -e, --echo            enable echoing even if not interactive tty
      -J                    load travisrc
      -k, --keep            keep current logfile
      -l file, --logname file
                            set logfile name
      -N, --new             create new logfile
      -n, --dry-run         count and display # unit tests
      -O                    load odoorc
      -p file_list, --search-pattern file_list
                            test file pattern
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
