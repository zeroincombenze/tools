please: developer shell
~~~~~~~~~~~~~~~~~~~~~~~

please is an interactive developer shell aim to help development and testing software.

    Usage: please [-hB][-b branch][-c file][-d diff][-fjk][-L logfile][-mn][-o prj_id][-O][-p path][-qr][-s files][-tuVv] actions sub1 sub2 sub3
    Developer shell
    Action may be on of:
    help|build|chkconfig|commit|config|distribution|docs|download_rep|duplicate|edit|export|import|list|lsearch|publish|push|pythonhosted|synchro|replace|replica|show|status|test|translate|version|wep
    -h                   this help, type 'please help' for furthermore info
    -B                   debug mode
    -b branch            branch: must be 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 or 14.0
    -c file              configuration file (def .travis.conf)
    -d diff              date to search in log
    -f                   force copy (of commit/push) | build (of register/publish) | dup doc (of distribution/synchro) | full (status)
    -j                   execute tests in project dir rather in test dir/old style synchro
    -k                   keep coverage statistics in annotate test/keep original repository | tests/ in publish
    -L logfile           log file name
    -m                   show missing line in report coverage
    -n                   do nothing (dry-run)
    -o prj_id            push only external project ids (of push)
    -O                   pull original README (and docs) in distribution (deprecated)
    -p path              declare local destination path
    -q                   silent mode
    -r                   run restricted mode (w/o parsing travis.yml file) | recurse distribution OCB
    -s files             files to include in annotate test
    -t                   test mode (implies dry-run)
    -u                   check for unary operator W503 or no OCA/zero module translation
    -V                   show version end exit
    -v                   verbose mode

Action is one of:

* help
* build
* chkconfig
* config
* docs
* duplicate
* export MODULE DB
* import
* list
* lsearch
* publish
* push
* pythonhosted
* replace
* replica
* show
* status
* test
* translate MODULE DB
* version
* wep

*build*

    Build a tar file for current PYPI project

*chkconfig*

    Display various values of current project.

*config global|local*

    Set various parameter by edit with vim.

*docs*

    Prepare documentation to publish on readthedocs website.

*export MODULE DB [-bBRANCH]*

    Export po file of Odoo project.
    If current directory is a module directory you can use '.' (dot) for module name.

    To declare specific version use -b switch

*import MODULE DB*

    Import po file of Odoo project.

    To declare target version use \fB-b\fR switch

*publish docs|download|pypi|svg|testpypi*

    Publish documentation or package.

    * publish docs     -> publish generate docs to website (require system privileges)
    * publish download -> publish tarball to download (require system privileges)
        type \fBplease build\fR to generate tarball file
    * publish pypi     -> publish package to pypi website (from odoo user)
    * publish svg      -> publish test result svg file (require system privileges)
    * publish tar      -> write a tarball with package files
