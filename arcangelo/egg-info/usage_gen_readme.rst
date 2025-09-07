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
~~~~~~~~~~~~~~~~~~~~~

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

.. $include usage_gen_readme_sym.csv

Macro
~~~~~

Text macro is replaced by macro contents. For current version {{branch}} of
gen_readme.py, macro is enclosed by double braces.

.. raw:: html

    For current version &lbrace;&lbrace;branch}} of gen_readme.py

Capture command output
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can add command output of a chell command in your documentation.
The syntax is the same of bash:

.. raw:: html

    &dollar;(COMMAND ARGUMENTS)

Example:

.. raw:: html

    Here the output of the help of bash Linux command <b>true</b>:<br/><br/>
    &dollar;(man true)

::

    $(man true)

gen_readme.py command line
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    $(gen_readme -h)
