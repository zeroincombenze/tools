.. toctree::
   :maxdepth: 2

Wok_Code
========


Various tools at your fingertips.

The available tools are:

* cvt_csv_2_rst.py: convert csv file into rst file
* cvt_csv_2_xml.py: convert csv file into xml file
* cvt_script: parse bash script and convert to meet company standard
* gen_readme.py: generate documentation files, mainly README.rst
* odoo_dependency.py: show odoo dependencies and/or Odoo module tree
* odoo_translation.py: manage Odoo translation
* arcangelo: parse source .py file to meet pep8 and convert across Odoo versions
* please: developer shell
* wget_odoo_repositories.py: get repository names from github.com
Digest of odoo_dependencies
===========================


odoo_dependecies.py: show odoo dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Show information about odoo dependencies and module tree.
Digest of arcangelo
===================


arcangelo: python edit utility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**arcangelo** is an automatic editor for transforming python source code.
**arcangelo** is used to perform basic text transformation based on user rules.
While in some ways similar to an editor which permits scripted edits (such as
ed or sed), **arcangelo** works by making editor command from rule files.
Rule files are simple yaml files, read by arcangelo which try to apply all rules
to all lines of files processed.

In this way migration workflow is very simple, accurate, precise and fast.
Digest of please
================


please is an interactive developer shell aim to help development and testing software.
It has no function integrated in it, it ids simply a hook for various commands.
Digest of macro
===============


+---------------------------+-----------------------------------------------------------------------+
| acknowledges              | Acknowledges list                                                     |
+---------------------------+-----------------------------------------------------------------------+
| authors                   | Authors list                                                          |
+---------------------------+-----------------------------------------------------------------------+
| available_addons          | N/D                                                                   |
+---------------------------+-----------------------------------------------------------------------+
| branch                    | Odoo version for this repository/module                               |
+---------------------------+-----------------------------------------------------------------------+
| certifications            | Certificates list                                                     |
+---------------------------+-----------------------------------------------------------------------+
| contact_us                | Contact informations                                                  |
+---------------------------+-----------------------------------------------------------------------+
| contributors              | Contributors list                                                     |
+---------------------------+-----------------------------------------------------------------------+
| configuration             | How to configure                                                      |
+---------------------------+-----------------------------------------------------------------------+
| copyright_notes           | Copyright notes                                                       |
+---------------------------+-----------------------------------------------------------------------+
| description               | English description of the repository/module (mandatory)              |
+---------------------------+-----------------------------------------------------------------------+
| descrizione               | Descrizione modulo/progetto in italiano (obbligatoria)                |
+---------------------------+-----------------------------------------------------------------------+
| doc-URL                   | URL for button documentation                                          |
+---------------------------+-----------------------------------------------------------------------+
| faq                       | Frequently asked questions                                            |
+---------------------------+-----------------------------------------------------------------------+
| features                  | Features of the repository/module                                     |
+---------------------------+-----------------------------------------------------------------------+
| GPL                       | same of gpl                                                           |
+---------------------------+-----------------------------------------------------------------------+
| git_orgid                 | Git organization                                                      |
+---------------------------+-----------------------------------------------------------------------+
| gpl                       | License name: may be A-GPL or L-GPL                                   |
+---------------------------+-----------------------------------------------------------------------+
| grymb_image_*             | Symbol imagae (suffix is a supported symbol name)                     |
+---------------------------+-----------------------------------------------------------------------+
| help-URL                  | URL for button help                                                   |
+---------------------------+-----------------------------------------------------------------------+
| history                   | Changelog history                                                     |
+---------------------------+-----------------------------------------------------------------------+
| known_issues              | Known issues                                                          |
+---------------------------+-----------------------------------------------------------------------+
| include                   | files included (space separated) to read before writing document      |
+---------------------------+-----------------------------------------------------------------------+
| installation              | How to install                                                        |
+---------------------------+-----------------------------------------------------------------------+
| name                      | Module name (must be a python name)                                   |
+---------------------------+-----------------------------------------------------------------------+
| now                       | Create timestamp                                                      |
+---------------------------+-----------------------------------------------------------------------+
| maintenance               | Maintenance information                                               |
+---------------------------+-----------------------------------------------------------------------+
| maturity                  | Maturity status (alpha, beta, etc.)                                   |
+---------------------------+-----------------------------------------------------------------------+
| module_name               | Module name                                                           |
+---------------------------+-----------------------------------------------------------------------+
| OCA-URL                   | URL to the same repository/module of OCA in github.com                |
+---------------------------+-----------------------------------------------------------------------+
| oca_diff                  | OCA comparation                                                       |
+---------------------------+-----------------------------------------------------------------------+
| odoo_fver                 | Odoo full version (deprecated)                                        |
+---------------------------+-----------------------------------------------------------------------+
| odoo_majver               | Odoo major version; internal use to set some values                   |
+---------------------------+-----------------------------------------------------------------------+
| odoo_layer                | Document layer, may be: ocb, module or repository                     |
+---------------------------+-----------------------------------------------------------------------+
| prerequisites             | Installation prerequisites                                            |
+---------------------------+-----------------------------------------------------------------------+
| prior_branch              | Previous Odoo version of this repository/module                       |
+---------------------------+-----------------------------------------------------------------------+
| prior2_branch             | Previous Odoo version of previous repository/module                   |
+---------------------------+-----------------------------------------------------------------------+
| proposals_for_enhancement | Proposals for enhancement text                                        |
+---------------------------+-----------------------------------------------------------------------+
| pypi_modules              | pypi module list (may be set in __manifest__.rst)                     |
+---------------------------+-----------------------------------------------------------------------+
| pypi_sects                | pypi section names to import (may be set in __manifest__.rst)         |
+---------------------------+-----------------------------------------------------------------------+
| repos_name                | Repository/project name                                               |
+---------------------------+-----------------------------------------------------------------------+
| sponsor                   | Sponsors list                                                         |
+---------------------------+-----------------------------------------------------------------------+
| sommario                  | Traduzione italiana di summary                                        |
+---------------------------+-----------------------------------------------------------------------+
| submodules                | Sub module list (space separated) to document (only in pypi projects) |
+---------------------------+-----------------------------------------------------------------------+
| summary                   | Repository/module summary (CR are translated into spaces)             |
+---------------------------+-----------------------------------------------------------------------+
| support                   | Support informations                                                  |
+---------------------------+-----------------------------------------------------------------------+
| today                     | Create date                                                           |
+---------------------------+-----------------------------------------------------------------------+
| translators               | Translators list                                                      |
+---------------------------+-----------------------------------------------------------------------+
| troubleshooting           | Troubleshooting information                                           |
+---------------------------+-----------------------------------------------------------------------+
| try_me-URL                | URL for button try-me                                                 |
+---------------------------+-----------------------------------------------------------------------+
| upgrade                   | How to upgrade                                                        |
+---------------------------+-----------------------------------------------------------------------+
| usage                     | How to usage                                                          |
+---------------------------+-----------------------------------------------------------------------+
Digest of gen_readme
====================


gen_readme.py: documentation generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use this software to generate the project or module documentation.
You can create the README.rst of OCB, repository and modules of Odoo projects.
You can also generate the index.html of Odoo module.

You can even create the README.rst of PYPI projects.
This document was generated by this tool itself.

The tool is supplied with follow templates:

* Odoo README.rst: to generare README of Odoo repository o module
* PYPI README.rst: to generate README of pypi package
* index.html: to generate Odoo module index.html
* __openerp__.py: to update __openerp__.py of Odoo < 8.0 with description


templates
~~~~~~~~~

This tool read a template and write the document (usually named README.rst).
The template can contains macro which format is \{\{macro_name\}\}.

Currently, the follow macros are recognized:

+---------------------------+-----------------------------------------------------------------------+
| acknowledges              | Acknowledges list                                                     |
+---------------------------+-----------------------------------------------------------------------+
| authors                   | Authors list                                                          |
+---------------------------+-----------------------------------------------------------------------+
| available_addons          | N/D                                                                   |
+---------------------------+-----------------------------------------------------------------------+
| branch                    | Odoo version for this repository/module                               |
+---------------------------+-----------------------------------------------------------------------+
| certifications            | Certificates list                                                     |
+---------------------------+-----------------------------------------------------------------------+
| contact_us                | Contact informations                                                  |
+---------------------------+-----------------------------------------------------------------------+
| contributors              | Contributors list                                                     |
+---------------------------+-----------------------------------------------------------------------+
| configuration             | How to configure                                                      |
+---------------------------+-----------------------------------------------------------------------+
| copyright_notes           | Copyright notes                                                       |
+---------------------------+-----------------------------------------------------------------------+
| description               | English description of the repository/module (mandatory)              |
+---------------------------+-----------------------------------------------------------------------+
| descrizione               | Descrizione modulo/progetto in italiano (obbligatoria)                |
+---------------------------+-----------------------------------------------------------------------+
| doc-URL                   | URL for button documentation                                          |
+---------------------------+-----------------------------------------------------------------------+
| faq                       | Frequently asked questions                                            |
+---------------------------+-----------------------------------------------------------------------+
| features                  | Features of the repository/module                                     |
+---------------------------+-----------------------------------------------------------------------+
| GPL                       | same of gpl                                                           |
+---------------------------+-----------------------------------------------------------------------+
| git_orgid                 | Git organization                                                      |
+---------------------------+-----------------------------------------------------------------------+
| gpl                       | License name: may be A-GPL or L-GPL                                   |
+---------------------------+-----------------------------------------------------------------------+
| grymb_image_*             | Symbol imagae (suffix is a supported symbol name)                     |
+---------------------------+-----------------------------------------------------------------------+
| help-URL                  | URL for button help                                                   |
+---------------------------+-----------------------------------------------------------------------+
| history                   | Changelog history                                                     |
+---------------------------+-----------------------------------------------------------------------+
| known_issues              | Known issues                                                          |
+---------------------------+-----------------------------------------------------------------------+
| include                   | files included (space separated) to read before writing document      |
+---------------------------+-----------------------------------------------------------------------+
| installation              | How to install                                                        |
+---------------------------+-----------------------------------------------------------------------+
| name                      | Module name (must be a python name)                                   |
+---------------------------+-----------------------------------------------------------------------+
| now                       | Create timestamp                                                      |
+---------------------------+-----------------------------------------------------------------------+
| maintenance               | Maintenance information                                               |
+---------------------------+-----------------------------------------------------------------------+
| maturity                  | Maturity status (alpha, beta, etc.)                                   |
+---------------------------+-----------------------------------------------------------------------+
| module_name               | Module name                                                           |
+---------------------------+-----------------------------------------------------------------------+
| OCA-URL                   | URL to the same repository/module of OCA in github.com                |
+---------------------------+-----------------------------------------------------------------------+
| oca_diff                  | OCA comparation                                                       |
+---------------------------+-----------------------------------------------------------------------+
| odoo_fver                 | Odoo full version (deprecated)                                        |
+---------------------------+-----------------------------------------------------------------------+
| odoo_majver               | Odoo major version; internal use to set some values                   |
+---------------------------+-----------------------------------------------------------------------+
| odoo_layer                | Document layer, may be: ocb, module or repository                     |
+---------------------------+-----------------------------------------------------------------------+
| prerequisites             | Installation prerequisites                                            |
+---------------------------+-----------------------------------------------------------------------+
| prior_branch              | Previous Odoo version of this repository/module                       |
+---------------------------+-----------------------------------------------------------------------+
| prior2_branch             | Previous Odoo version of previous repository/module                   |
+---------------------------+-----------------------------------------------------------------------+
| proposals_for_enhancement | Proposals for enhancement text                                        |
+---------------------------+-----------------------------------------------------------------------+
| pypi_modules              | pypi module list (may be set in __manifest__.rst)                     |
+---------------------------+-----------------------------------------------------------------------+
| pypi_sects                | pypi section names to import (may be set in __manifest__.rst)         |
+---------------------------+-----------------------------------------------------------------------+
| repos_name                | Repository/project name                                               |
+---------------------------+-----------------------------------------------------------------------+
| sponsor                   | Sponsors list                                                         |
+---------------------------+-----------------------------------------------------------------------+
| sommario                  | Traduzione italiana di summary                                        |
+---------------------------+-----------------------------------------------------------------------+
| submodules                | Sub module list (space separated) to document (only in pypi projects) |
+---------------------------+-----------------------------------------------------------------------+
| summary                   | Repository/module summary (CR are translated into spaces)             |
+---------------------------+-----------------------------------------------------------------------+
| support                   | Support informations                                                  |
+---------------------------+-----------------------------------------------------------------------+
| today                     | Create date                                                           |
+---------------------------+-----------------------------------------------------------------------+
| translators               | Translators list                                                      |
+---------------------------+-----------------------------------------------------------------------+
| troubleshooting           | Troubleshooting information                                           |
+---------------------------+-----------------------------------------------------------------------+
| try_me-URL                | URL for button try-me                                                 |
+---------------------------+-----------------------------------------------------------------------+
| upgrade                   | How to upgrade                                                        |
+---------------------------+-----------------------------------------------------------------------+
| usage                     | How to usage                                                          |
+---------------------------+-----------------------------------------------------------------------+



Documentation may contains some graphical symbols in format \|symbol\|.
Currently, follows symbols are recognized:

* check
* DesktopTelematico
* en
* exclamation
* FatturaPA
* halt
* info
* it
* late
* menu
* no_check
* right_do
* same
* warning
* xml_schema

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

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.7/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.7/man
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
