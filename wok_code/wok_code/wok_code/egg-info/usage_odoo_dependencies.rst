odoo_dependecies.py usage
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    usage: odoo_dependencies.py [-h] [-A {dep,help,jrq,mod,rev,tree}] [-a]
                                [-b version] [-B DEPENDS_BY] [-c file] [-D file]
                                [-E] [-e] [-H] [-M MODULES_TO_MATCH] [-m] [-N]
                                [-n] [-o] [-P] [-q] [-R] [-S SEP_LIST] [-V] [-v]
                                [-x] [-1]
                                [path_list [path_list ...]]

    Odoo dependencies management

    positional arguments:
      path_list

    optional arguments:
      -h, --help            show this help message and exit
      -A {dep,help,jrq,mod,rev,tree}, --action {dep,help,jrq,mod,rev,tree}
      -a, --and-list
      -b version, --branch version
                            Odoo branch
      -B DEPENDS_BY, --depends-by DEPENDS_BY
      -c file, --config file
                            configuration command file
      -D file, --dbname file
                            DB name
      -E, --only-missed
      -e, --external-dependencies
      -H, --action-help
      -M MODULES_TO_MATCH, --modules-to-match MODULES_TO_MATCH
      -m, --action-modules
      -N, --only-count
      -n, --dry-run         do nothing (dry-run)
      -o, --or-list
      -P, --pure-list
      -q, --quiet           silent mode
      -R, --recurse
      -S SEP_LIST, --sep-list SEP_LIST
      -V, --version         show program's version number and exit
      -v, --verbose         verbose mode
      -x, --external-bin-dependencies
      -1, --no-depth
