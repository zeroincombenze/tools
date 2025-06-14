::

    $(please -h)


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
    Set various parameter editing with vim.
    Comments inside configuration file can aim to set values.

    Some variable are:

    * GBL_EXCLUDE=test_impex -> Module globally escluded by test because can fail locally
    * PYTHON_MATRIX="2.7 3.7" -> python version to use in tests

*docs*

    Prepare documentation to publish on readthedocs website (PYPI).
    Create / update README and index.html of Odoo module.
    Notice: README of repository history is tailored with last 60 days items;
    on README and index,html of module, history is tailored with last 180 days items;
    However max 12 items are added in README / index.html
    Summary showed to console are tailored with last 15 days.

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
