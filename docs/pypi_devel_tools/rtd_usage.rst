.. toctree::
   :maxdepth: 2

Usage
-----
Module usage
------------


gen_readme.py usage
~~~~~~~~~~~~~~~~~~~

::

    usage: gen_readme.py [-h] [-b ODOO_VID] [-B] [-G GIT_ORGID] [-H]
                         [-l ODOO_LAYER] [-m MODULE_NAME] [-n] [-o OUTPUT_FILE]
                         [-P PRODUCT_DOC] [-p PATH_NAME] [-q] [-R] [-r REPOS_NAME]
                         [-t TEMPLATE_NAME] [-V] [-v] [-W] [-w]

    Generate README

    optional arguments:
      -h, --help            show this help message and exit
      -b ODOO_VID, --odoo-branch ODOO_VID
      -B, --debug-template
      -G GIT_ORGID, --git-org GIT_ORGID
      -H, --write-index_html
      -l ODOO_LAYER, --layer ODOO_LAYER
                            ocb|module|repository
      -m MODULE_NAME, --module-name MODULE_NAME
                            filename
      -n, --dry-run         do nothing (dry-run)
      -o OUTPUT_FILE, --output-file OUTPUT_FILE
                            filename
      -P PRODUCT_DOC, --product-doc PRODUCT_DOC
                            may be odoo or pypi
      -p PATH_NAME, --path-name PATH_NAME
                            pathname
      -q, --quiet           silent mode
      -R, --rewrite-manifest
      -r REPOS_NAME, --repos_name REPOS_NAME
                            dirname
      -t TEMPLATE_NAME, --template_name TEMPLATE_NAME
                            filename
      -V, --version         show program's version number and exit
      -v, --verbose         verbose mode
      -W, --set_website
      -w, --suppress-warning

Examples:

::

    # Update Odoo module documentation
    cd ~/odoo_12/axitec/l10n_it_balance     # Odoo project directory
    dir egg-info
    >>> authors.txt contributors.txt description.rst __init__.txt known_issues.rst
    gen_readme.py                           # Generate README.rst of project
    gen_readme.py -H                        # Generate index.html of project

    # Create index.rst of pypi module
    cd ~/dev/pypi/devel_tools/devel_tools/docs
    gen_readme.py -t module_index.rst -o index.rst -B

    # Create README.rst of pypi module
    cd ~/dev/pypi/devel_tools/devel_tools
    gen_readme.py


Files and directories
~~~~~~~~~~~~~~~~~~~~~

Document structure is:

::

    docs                              (1)
    ┣━ index rst
    ┣━ logozero_180x46.png
    ┗━ rtd*  #                        (2)

    egg-info                          (3)
    ┣━ __init__.txt
    ┣━ description.rst
    ┣━ descrizione.rst
    ┣━ features.rst
    ┣━ oca_diff.rst
    ┣━ certifications.rst
    ┣━ prerequisites.rst
    ┣━ installation.rst
    ┣━ configuration.rst
    ┣━ upgrade.rst
    ┣━ support.rst
    ┣━ usage.rst
    ┣━ maintenance.rst
    ┣━ troubleshooting.rst
    ┣━ known_issues.rst
    ┣━ proposals_for_enhancement.rst
    ┣━ history.rst
    ┣━ faq.rst
    ┣━ sponsor.rst
    ┣━ copyright_notes.rst
    ┣━ available_addons.rst
    ┣━ contact_us.rst
    ┣━ authors.txt
    ┣━ contributors.txt
    ┣━ translators.txt
    ┗━ acknowledges.txt

    readme                            (4)
    ┣━ CONTRIBUTORS.rst
    ┣━ DESCRIPTION.rst
    ┗━ *.rst  # (Other OCA docs)      (5)

    Notes:
    (1) Directory for Sphynx (PYPI projects)
    (2) Files generated from egg-info directory
    (3) Zeroincombenze document root
    (4) Oca document root
    (5) See OCA documentation

Predefined template structure is:

::

    templates
        ┣━ Odoo
        ┃    ┣━ contact_us.rst
        ┃    ┣━ default_authors.txt
        ┃    ┣━ default_contributors.txt
        ┃    ┣━ default_copyright_notes.rst
        ┃    ┣━ default_description.rst
        ┃    ┣━ default_descrizione.rst
        ┃    ┣━ default_installation.rst
        ┃    ┣━ default_maintenance.rst
        ┃    ┣━ default_oca_diff.rst
        ┃    ┣━ default_proposals_for_enhancement.rst
        ┃    ┣━ default_quality
        ┃    ┣━ endorsement.rst
        ┃    ┣━ default_support.rst
        ┃    ┣━ default_troubleshooting.rst
        ┃    ┣━ default_upgrade.rst
        ┃    ┣━ header_acknowledges.txt
        ┃    ┣━ header_troubleshooting.rst
        ┃    ┣━ ocb_description.rst
        ┃    ┣━ ocb_descrizione.rst
        ┃    ┣━ readme_footer.rst
        ┃    ┣━ readme_header.rst
        ┃    ┣━ readme_index.html
        ┃    ┣━ readme_main_module.rst
        ┃    ┣━ readme_main_ocb.rst
        ┃    ┣━ readme_main_repository.rst
        ┃    ┗━ readme_manifest.rst
        ┃
        ┗━ pypi
             ┣━ default_contributors.txt
             ┣━ default_installation.rst
             ┣━ module_index.rst
             ┣━ module_mainpage.rst
             ┣━ readme_footer.rst
             ┣━ readme_header.rst
             ┣━ readme_main_module.rst
             ┣━ readme_main_repository.rst
             ┗━ repository_mainpage.rst



Statements
~~~~~~~~~~

Every document or template can contains some control statement.
A statement starts with ".. $" (dot dot space and dollar).

Current supported statements are:

::

    .. $if CONDITION
    .. $elif CONDITION
    .. $else
    .. $fi

    .. $include FILENAME
    .. $set VAR EXPRESSION
    .. $merge_docs

Notes: MACRO and VAR are the same object.
In this documentation VAR means the name of the macro while MACRO is the name of the macro enclosed by doubel bracets.

::

    i.e.  .. $if branch == '12.0'
          Current branch is 1.0.0.4

In above example then word branch after statement $if ia the VAR branch.
The word branch in the second line is a text. The item 1.0.0.4 is the macro, replaced by the value of varaibale branch.

CONDITION may be a python condition or one of follow special condition:

::

    VAR in LIST
    where VAR is a variable to test and LIST is value list space separated
    i.e.
    .. $if branch in '10.0' '11.0' '12.0'

FILE may be a file name. SUpported file types are .rst and .csv

::

    i.e.
        .. $include my_description.rst
        .. $include my_table.csv



Macro
~~~~~

Macro currently supported:

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
Currently follows symbols are supported:

+-------------------+---------------------+
| check             | |check|             |
+-------------------+---------------------+
| DesktopTelematico | |DesktopTelematico| |
+-------------------+---------------------+
| en                | |en|                |
+-------------------+---------------------+
| exclamation       | |exclamation|       |
+-------------------+---------------------+
| FatturaPA         | |FatturaPA|         |
+-------------------+---------------------+
| halt              | |halt|              |
+-------------------+---------------------+
| info              | |info|              |
+-------------------+---------------------+
| it                | |it|                |
+-------------------+---------------------+
| late              | |late|              |
+-------------------+---------------------+
| menu              | |menu|              |
+-------------------+---------------------+
| no_check          | |no_check|          |
+-------------------+---------------------+
| right_do          | |right_do|          |
+-------------------+---------------------+
| same              | |same|              |
+-------------------+---------------------+
| warning           | |warning|           |
+-------------------+---------------------+
| xml_schema        | |xml_schema|        |
+-------------------+---------------------+



Macro used in documentation templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following macroes may be declared in package documentation, mainly in __init__.txt or in __manifest__.rst file with $set statement.

+---------------------+-----------------------------------------------+
| include             | Document to include                           |
+---------------------+-----------------------------------------------+
| no_pypi             | Value 1 means module is not a pypi package    |
+---------------------+-----------------------------------------------+
| no_section_oca_diff | If value is 1 the section oca_diff is skipped |
+---------------------+-----------------------------------------------+
| submodules          | Declare sub-documents                         |
+---------------------+-----------------------------------------------+


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


topep8 usage
~~~~~~~~~~~~

::

    Usage: topep8 [-haAB][-b version][-c][-C org][-Dde][-F ver][-f][-G gpl][-iLnN][-o file][-O][-R file][-quVvX01] fullname
    PEP8 source python file
    full path name maybe supplied or a single file

     -h                      this help
     -a                      enable non-whitespace changes (may issue multiple -a)
     -A                      do not execute autoflake (-A) neither autopep8 (-AA)
     -B                      activate debug statements
     -b version              odoo branch; may be 6.1 7.0 8.0 9.0 10.0 11.0 12.0 or 13.0
     -c                      change class name to CamelCase
     -C org                  add developers Copyright (def zero)
     -D                      show debug informations
     -d                      show diff
     -e                      do not apply enhance update
     -F ver                  from odoo branch, value like -b switch
     -f                      futurize
     -G gpl                  Write GPL info into header (agpl,lgpl,gpl)
     -i                      sort import statements
     -L                      set file excluded by lint parse
     -n                      do nothing (dry-run)
     -N                      do not add newline at the EOF
     -o file                 output filename, leave source unchanged rather than source becomes .bak
     -O                      change copyright from openerp to odoo
     -R file                 use specific rule file
     -q                      silent mode
     -u                      use old api odoo<8.0 or create yaml old style
     -V                      show version
     -v                      verbose mode
     -X                      make file.py executable
     -0                      create yaml file from zero
     -1                      do not recurse travese directories



|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2020-10-25

.. |Maturity| image:: https://img.shields.io/badge/maturity-Mature-green.png
    :target: https://odoo-community.org/page/development-status
    :alt: Production/Stable
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=master
    :target: https://travis-ci.org/zeroincombenze/tools
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=master
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=1.0.0.4
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/1.0.0.4/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/1.0.0.4
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-1.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/1.0.0.4/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-1.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/1.0.0.4/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-1.svg
    :target: https://erp1.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/1.0.0.4/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/1.0.0.4
    :alt: Codecov
.. |Odoo Italia Associazione| image:: https://www.odoo-italia.org/images/Immagini/Odoo%20Italia%20-%20126x56.png
   :target: https://odoo-italia.org
   :alt: Odoo Italia Associazione
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
   :target: https://t.me/axitec_helpdesk


