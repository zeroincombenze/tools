.. toctree::
   :maxdepth: 2

Usage
=====


::

    usage: please.py [-h] [-H PATH] [-n] [-Q FILE] [-q] [-v] [-V] [action]
    
    Zeroincombenze® developer shell.
    obj after action may be on of apache, cwd, python, z0bug, zerobug, travis
    
    positional arguments:
      action
    
    options:
      -h, --help            show this help message and exit
      -H PATH, --home-devel PATH
                            Home devel directory
      -n, --dry-run         do nothing (dry-run)
      -Q FILE, --tools-config FILE
                            Configuration file
      -q, --quiet           silent mode
      -v, --verbose         verbose mode
      -V, --version         show program's version number and exit
    
    Help available issuing: please help ACTION
    © 2015-2023 by SHS-AV s.r.l.
    Author: antoniomaria.vigliotti@gmail.com
    Full documentation at: https://zeroincombenze-tools.readthedocs.io/
    



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

|
|

.. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.22/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.22/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg
    :target: https://erp2.zeroincombenze.it
    :alt: Try Me
.. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4
   :target: https://www.zeroincombenze.it/
   :alt: Zeroincombenze
.. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png
   :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png
   :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/check.png
.. |no_check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/no_check.png
.. |menu| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/menu.png
.. |right_do| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/right_do.png
.. |exclamation| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/exclamation.png
.. |warning| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/warning.png
.. |same| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/same.png
.. |late| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/late.png
.. |halt| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/halt.png
.. |info| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/info.png
.. |xml_schema| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/iso/icons/xml-schema.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md
.. |DesktopTelematico| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/DesktopTelematico.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md
.. |FatturaPA| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/fatturapa.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md
.. |chat_with_us| image:: https://www.shs-av.com/wp-content/chat_with_us.gif
   :target: https://t.me/Assitenza_clienti_powERP
