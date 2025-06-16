.. toctree::
   :maxdepth: 2

Digest of gen_readme
====================


gen_readme.py usage
~~~~~~~~~~~~~~~~~~~

gen_readme.py makes easy to create high quality documentation, mainly
README.rst, index.html and index.rst for Odoo modules and python packages.

Documentation process is based on templates which include source files with
documentation fragments: see below "Files and directories" chapter.

Source files uses the reStructuredText markup language by default, which have
functionality for complex documentation to make straightforward and powerful to use.

Features:

* Output formats: HTML and RST
* Cross-references
* Hierarchical structure
* Automatic indices
* Code handling

Predefined sections
~~~~~~~~~~~~~~~~~~~

* changelog
* description
* features
* oca_diff
* certifications
* prerequisites
* installation
* configuration
* upgrade
* support
* usage
* maintenance
* troubleshooting
* known_issues
* proposals_for_enhancement
* faq
* authors
* contributors
* translators
* acknowledges
* maintainer
* sponsor
* copyright_notes
* available_addons
* contact_us

Files and directories
~~~~~~~~~~~~~~~~~~~~~

Document structure is:

::

    docs                              (1)
    ┣━ index rst
    ┣━ logozero_180x46.png
    ┗━ rtd*                           (2)

    egg-info                          (3)
    readme                            (4)
    ┣━ __manifest__.rst
    ┣━ ACKNOWLEDGES.rst               (7)
    ┣━ AUTHORS.rst                    (6)
    ┣━ CERTIFICATIONS.rst             (7)
    ┣━ CHANGELOG.rst
    ┣━ CONFIGURATION.rst
    ┣━ CONTACT_US.rst
    ┣━ CONTRIBUTORS.rst
    ┣━ COPYRIGHT_NOTES.rst
    ┣━ DESCRIPTION.rst
    ┣━ FAQ.rst
    ┣━ FEATURES.rst
    ┣━ KNOWN_ISSUES.rst
    ┣━ INSTALLATION.rst
    ┣━ OCA_DIFF.rst                   (7)
    ┣━ MAINTENANCE.rst
    ┣━ PREREQUISITES.rst              (7)
    ┣━ PROPOSALS_FOR_ENHANCEMENT.rst
    ┣━ SPONSOR.rst
    ┣━ SUPPORT.rst
    ┣━ TRANSLATORS.rst                (7)
    ┣━ TROUBLESHOOTING.rst
    ┣━ UPGRADE.rst
    ┣━ USAGE.rst
    ┗━ *.rst  # (Other OCA docs)      (5)

    Notes:
    (1) Directory for Sphynx (only PYPI projects)
    (2) Files generated from egg-info directory
    (3) Zeroincombenze root
    (4) Oca document root
    (5) See OCA documentation
    (6) Matched with __manifest__.py in Odoo projects
    (7) Not managed by OCA tools

Predefined template structure is:

::

    templates
        ┣━ Odoo
        ┃    ┣━ contact_us.rst
        ┃    ┣━ default_authors.rst
        ┃    ┣━ default_contributors.rst
        ┃    ┣━ default_copyright_notes.rst
        ┃    ┣━ default_description.rst
        ┃    ┣━ default_descrizione.rst
        ┃    ┣━ default_installation.rst
        ┃    ┣━ default_maintainer.rst
        ┃    ┣━ default_maintenance.rst
        ┃    ┣━ default_oca_diff.rst
        ┃    ┣━ default_proposals_for_enhancement.rst
        ┃    ┣━ default_quality_endorsement.rst
        ┃    ┣━ default_support.rst
        ┃    ┣━ default_troubleshooting.rst
        ┃    ┣━ default_upgrade.rst
        ┃    ┣━ header_acknowledges.rst
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
             ┣━ default_authors.rst
             ┣━ default_contributors.rst
             ┣━ default_installation.rst
             ┣━ default_prerequisites.rst
             ┣━ default_upgrade.rst
             ┣━ module_index.rst
             ┣━ module_mainpage.rst
             ┣━ pypi_index.rst
             ┣━ readme_footer.rst
             ┣━ readme_header.rst
             ┣━ readme_main_module.rst
             ┣━ readme_main_repository.rst
             ┣━ rtd_template.rst
             ┗━ rtd_template_automodule.rst

RST syntax
~~~~~~~~~~

Source file may be in html format or reStructuredText (reST) format, that is the default
plaintext markup language.

Source document contains documentation text, inline markup and directives.

A directive is a generic block of explicit markup. Directives begin with an explicit
markup start (two periods and a space), followed by the directive type and two colons.
Examples:

::

    .. directive :: (spec)
       directive body

A directive may be e preprocessor statement too. Preprocesso begins with markup start,
followed by "$" (dollar) and statement. Example:

::

    .. $if CONDITION

RST statement
~~~~~~~~~~~~~

Current supported statements are:

::

    .. $if CONDITION
    .. $elif CONDITION
    .. $else
    .. $fi
    .. $include FILENAME
    .. $block BLOCKNAME
    .. $set VAR EXPRESSION


RST directives
~~~~~~~~~~~~~~

gen_readme supports following rst directives:

::

    .. figure
    .. image

RST inline markup
~~~~~~~~~~~~~~~~~

The standard reST inline markup to visual *italic*, **boldface**
and ``code text`` is quite simple:

::

    use one asterisk: *text* for emphasis (italics),
    two asterisks: **text** for strong emphasis (boldface)
    backquotes: ``text`` for code samples.

RST lists
~~~~~~~~~

Lists and Quote-like blocks:
just place an asterisk at the start of a paragraph and indent properly.
The same goes for numbered lists; they can also be autonumbered using a #. sign:

::

    * list item A
    * list item B
    * list item C

::

    #. list item 1
    #. list item 2
    #. list item 3

Example:

* list item A
* list item B
* list item C

#. list item 1
#. list item 2
#. list item 3

RST table
~~~~~~~~~

They look like this:

::

    +------------------------+------------+----------+----------+
    | Header row, column 1   | Header 2   | Header 3 | Header 4 |
    | (header rows optional) |            |          |          |
    +========================+============+==========+==========+
    | body row 1, column 1   | column 2   | column 3 | column 4 |
    +------------------------+------------+----------+----------+
    | body row 2             | ...        | ...      |          |
    +------------------------+------------+----------+----------+

Example:

+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | ...        | ...      |          |
+------------------------+------------+----------+----------+

.. important::
    Tables are automatically created from .csv files. See below "gen_reame symbols"

RST sections
~~~~~~~~~~~~

::

    =======
    TITLE 1
    =======

    Title 2
    =======

    Title 3
    -------

    Title 4
    ~~~~~~~

gen_readme symbols
~~~~~~~~~~~~~~~~~~

gen_readme provides some no standard features.

Graphical button (only for Odoo documentation):

::

    Click on [Button] to do something

.. raw:: html

    Click on <span style="color:white;background-color:#7C7BAD">Button</span> to do something

Page tabbed (only for Odoo documentation):

::

    Click on [`Tabbed`] to see other information

.. raw:: html

    Click on <span style="border-style:solid;border-width:1px 1px 0px 1px">Tabbed</span> to see other information

Other predefined symbols are:

+----------------------------------------+--------------------------------------------+
| check                                  | |check|                                    |
+----------------------------------------+--------------------------------------------+
| DesktopTelematico                      | |DesktopTelematico|                        |
+----------------------------------------+--------------------------------------------+
| en                                     | |en|                                       |
+----------------------------------------+--------------------------------------------+
| exclamation                            | |exclamation|                              |
+----------------------------------------+--------------------------------------------+
| FatturaPA                              | |FatturaPA|                                |
+----------------------------------------+--------------------------------------------+
| halt                                   | |halt|                                     |
+----------------------------------------+--------------------------------------------+
| info                                   | |info|                                     |
+----------------------------------------+--------------------------------------------+
| it                                     | |it|                                       |
+----------------------------------------+--------------------------------------------+
| late                                   | |late|                                     |
+----------------------------------------+--------------------------------------------+
| menu                                   | |menu|                                     |
+----------------------------------------+--------------------------------------------+
| no_check                               | |no_check|                                 |
+----------------------------------------+--------------------------------------------+
| right_do                               | |right_do|                                 |
+----------------------------------------+--------------------------------------------+
| same                                   | |same|                                     |
+----------------------------------------+--------------------------------------------+
| warning                                | |warning|                                  |
+----------------------------------------+--------------------------------------------+
| xml_schema                             | |xml_schema|                               |
+----------------------------------------+--------------------------------------------+



Macro
~~~~~

Text macro is replaced by macro contents. For current version 2.0.22 of
gen_readme.py, macro is enclosed by double braces.

.. raw:: html

    For current version &lbrace;&lbrace;branch}} of gen_readme.py

Capture command output
~~~~~~~~~~~~~~~~~~~~~~

You can add command output of a chell command in your documentation.
The syntax is the same of bash:

.. raw:: html

    &dollar;(COMMAND ARGUMENTS)

Example:

.. raw:: html

    Here the output of the help of bash Linux command <b>true</b>:<br/><br/>
    &dollar;(man true)

::

    TRUE(1)                                             User Commands                                             TRUE(1)
    
    NAME
           true - do nothing, successfully
    
    SYNOPSIS
           true [ignored command line arguments]
           true OPTION
    
    DESCRIPTION
           Exit with a status code indicating success.
    
           --help display this help and exit
    
           --version
                  output version information and exit
    
           NOTE:  your  shell  may  have  its  own  version of true, which usually supersedes the version described here.
           Please refer to your shell's documentation for details about the options it supports.
    
    AUTHOR
           Written by Jim Meyering.
    
    REPORTING BUGS
           GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
           Report true translation bugs to <https://translationproject.org/team/>
    
    COPYRIGHT
           Copyright  ©  2018  Free  Software  Foundation,  Inc.   License  GPLv3+:  GNU   GPL   version   3   or   later
           <https://gnu.org/licenses/gpl.html>.
           This  is  free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent per‐
           mitted by law.
    
    SEE ALSO
           Full documentation at: <https://www.gnu.org/software/coreutils/true>
           or available locally via: info '(coreutils) true invocation'
    
    GNU coreutils 8.30                                  September 2019                                            TRUE(1)
    


gen_readme.py command line
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    usage: gen_readme.py [-h] [-b ODOO_VID] [-B] [-D PATH] [-F FROM_VERSION] [-f]
                         [-G GIT_ORGID] [-g OPT_GPL] [-H] [-l ODOO_LAYER]
                         [-L LANG] [-m MODULE_NAME] [-M FORCE_MATURITY] [-n] [-O]
                         [-o OUTPUT_FILE] [-P PRODUCT_DOC] [-p PATH_NAME] [-q]
                         [-R] [-r REPOS_NAME] [-Q QUOTE_WITH] [-t TEMPLATE_NAME]
                         [-T] [-V] [-v] [-W] [-w] [-X] [-Y]
    
    Generate README
    
    options:
      -h, --help            show this help message and exit
      -b ODOO_VID, --odoo-branch ODOO_VID
      -B, --debug-template
      -D PATH, --home-devel PATH
                            Home devel directory
      -F FROM_VERSION, --from-version FROM_VERSION
      -f, --force           force creating documentation even if doc dirs do not
                            exit
      -G GIT_ORGID, --git-org GIT_ORGID
      -g OPT_GPL, --gpl-info OPT_GPL
      -H, -I, --write-index
                            write index.html rather than README.rst
      -l ODOO_LAYER, --layer ODOO_LAYER
                            ocb|module|repository
      -L LANG, --lang LANG  iso code
      -m MODULE_NAME, --module-name MODULE_NAME
                            filename
      -M FORCE_MATURITY, --force-maturity FORCE_MATURITY
                            Alfa,Beta,Mature,Production/stable
      -n, --dry-run         do nothing (dry-run)
      -O, --odoo_marketplace
                            create index.html with Odoo marketplace rules
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
      -Q QUOTE_WITH, --quote-with QUOTE_WITH
                            CHAR
      -t TEMPLATE_NAME, --template_name TEMPLATE_NAME
                            filename
      -T, --trace-file
      -V, --version         show program's version number and exit
      -v, --verbose         verbose mode
      -W, --write-authinfo
      -w, --suppress-warning
      -X, --write-office    write openoffice/libreoffic fragment help
      -Y, --write-man-page
    
    © 2018-2025 by SHS-AV s.r.l.
    

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
