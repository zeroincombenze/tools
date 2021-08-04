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


Tree directory
~~~~~~~~~~~~~~

While travis is running this is the tree directory:

::

    ${HOME}
    ┣━━ build                       # build root (by TravisCI)
    ┃    ┣━━ ${TRAVIS_BUILD_DIR}    # testing project repository (by TravisCI)
    ┃    ┗━━ ${ODOO_REPO}           # Odoo or OCA/OCB repository to check with    (1) (2)
    ┃
    ┣━━ ${ODOO_REPO}-${VERSION}     # symlnk of ${HOME}/build/{ODOO_REPO}         (1)
    ┃
    ┣━━ dependencies                # Odoo dependencies                           (3)
    ┃
    ┗━━ tools                       # clone of Zeroincombenze tools               (3) (4)
         ┃
         ┣━━ zerobug                # testing library
         ┃       ┗━━ _travis        # testing commands
         ┗━━ z0bug_odoo             # Odoo testing library
                 ┗━━ _travis        # testing commands

    (1) Directory with Odoo or OCA/OCB repository to check compatibility of testing project
    (2) If testing project is OCB, travis_install_env ignore this directory
    (3) Done by then following statements in .travis.yml:
        - travis_install_env
        Above statements replace the OCA statements:
        - travis_install_nightly
    (4) Done by following statements in .travis.yml::
        - git clone https://github.com/zeroincombenze/tools.git ${HOME}/tools --depth=1
        - \${HOME}/tools/install_tools.sh -qp
        - source ${HOME}/dev/activate_tools
        Above statements replace OCA following statements:
        - git clone https://github.com/OCA/maintainer-quality-tools.git ${HOME}/maintainer-quality-tools --depth=1
        - export PATH=${HOME}/maintainer-quality-tools/travis:${PATH}


Configuration file
~~~~~~~~~~~~~~~~~~

Values in configuration file are:

.. $include usage_config.csv
