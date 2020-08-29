Travis emulator usage
---------------------

::

    Usage: travis [-hBC][-c file][-D number][-EFfjk][-L number][-l dir][-Mmn][-O git-org][-pqr][-S false|true][-Vv][-X 0|1][-Y file][-y pyver][-Z] action sub sub2
    Travis-ci emulator for local developer environment
    Action may be: [force-]lint, [force-]test, emulate (default), (new|chk|cp|mv|merge)_vm, chkconfig or parseyaml
     -h                      this help
     -B                      debug mode: do not create log
     -C                      do not use stored PYPI
     -c file                 configuration file (def .travis.conf)
     -D number               travis_debug_mode: may be 0,1,2 or 9 (def yaml dependents)
     -E                      save virtual environment as ~/VME/VME{version}
     -F                      run final travis with full features
     -f                      force yaml to run w/o cmd subst
     -j                      execute tests in project dir rather in test dir (or expand macro if parseyaml)
     -k                      keep DB and virtual environment after tests
     -L number               lint_check_level: may be minimal,reduced,average,nearby,oca; def value from .travis.yml
     -l dir                  log directory (def=~/travis_log)
     -M                      use local MQT (deprecated)
     -m                      show missing line in report coverage
     -n                      do nothing (dry-run)
     -O git-org              git organization, i.e. oca or zeroincombenze
     -p                      prefer python test over bash test when avaiable
     -q                      silent mode
     -r                      run restricted mode (def parsing travis.yml file)
     -S false|true           use python system packages (def yaml dependents)
     -V                      show version
     -v                      verbose mode
     -X 0|1                  enable translation test (def yaml dependents)
     -Y file                 file yaml to process (def .travis.yml)
     -y pyver                test with specific python versions (comma separated)
     -Z                      use local zero-tools


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
        - \${HOME}/tools/install_tools.sh -qopt
        - source ${HOME}/dev/activate_tools
        Above statements replace OCA following statements:
        - git clone https://github.com/OCA/maintainer-quality-tools.git ${HOME}/maintainer-quality-tools --depth=1
        - export PATH=${HOME}/maintainer-quality-tools/travis:${PATH}


Configuration file
~~~~~~~~~~~~~~~~~~

Values in configuration file are:

.. $include usage_config.csv
