Travis emulator usage
---------------------

::

    Usage: travis [-hBC][-c file][-D number][-dEFfjk][-L number][-l dir][-Mmn][-O git-org][-pqr][-S false|true][-Vv][-X 0|1][-Y file][-y pyver][-Z] action sub sub2
    Travis-ci emulator for local developer environment
    Action may be: [force-]lint, [force-]test, emulate (default), (new|chk|cp|mv|merge)_vm, chkconfig or parseyaml
     -h --help            this help
     -B --debug           debug mode: do not create log
     -C --no-cache        do not use stored PYPI
     -c --conf file
                          configuration file (def .travis.conf)
     -D --debug-level number
                          travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)
     -d --osx             emulate osx-darwin
     -E --no-savenv       do not save virtual environment into ~/VME/... if does not exist
     -F --full            run final travis with full features
     -f --force           force yaml to run w/o cmd subst
     -j                   execute tests in project dir rather in test dir (or expand macro if parseyaml)
     -k --keep            keep DB and virtual environment after tests
     -L --lint-level number
                          lint_check_level: may be minimal,reduced,average,nearby,oca; def value from .travis.yml
     -l --logdir dir
                          log directory (def=/home/antoniomaria/odoo/travis_log)
     -M                   use local MQT (deprecated)
     -m --missing         show missing line in report coverage
     -n --dry-run         do nothing (dry-run)
     -O --org git-org
                          git organization, i.e. oca or zeroincombenze
     -p --pytest          prefer python test over bash test when avaiable
     -q --quiet           silent mode
     -r                   run restricted mode (deprecated)
     -S --syspkg false|true
                          use python system packages (def yaml dependents)
     -V --version         show version
     -v --verbose         verbose mode
     -X 0|1               enable translation test (def yaml dependents)
     -Y --yaml-file file
                          file yaml to process (def .travis.yml)
     -y --pyver pyver
                          test with specific python versions (comma separated)
     -Z --zero            use local zero-tools

Configuration file
~~~~~~~~~~~~~~~~~~

Values in configuration file are:

.. $include usage_config.csv