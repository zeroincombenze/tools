topep8 usage
~~~~~~~~~~~~

::

    Usage: topep8 [-haAB][-b version][-c][-C org][-Dde][-F ver][-fGiLnN][-o file][-O][-R file][-quVvX01] fullname
    PEP8 source python file
    full path name maybe supplied or a single file

     -h              this help
     -a              enable non-whitespace changes (may issue multiple -a)
     -A              do not execute autoflake (-A) neither autopep8 (-AA)
     -B              activate debug statements
     -b version      odoo branch; may be 6.1 7.0 8.0 9.0 10.0 11.0 or 12.0
     -c              change class name to CamelCase
     -C org          add developers Copyright (def zero)
     -D              show debug informations
     -d              show diff
     -e              do not apply enhance update
     -F ver          from odoo branch, value like -b switch
     -f              futurize
     -G              Write GPL info into header
     -i              sort import statements
     -L              set file excluded by lint parse
     -n              do nothing (dry-run)
     -N              do not add newline at the EOF
     -o file         output filename, leave source unchanged rather than source becomes .bak
     -O              change copyright from openerp to odoo
     -R file         use specific rule file
     -q              silent mode
     -u              use old api odoo<8.0 or create yaml old style
     -V              show version
     -v              verbose mode
     -X              make file.py executable
     -0              create yaml file from zero
     -1              do not recurse travese directories

