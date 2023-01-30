gen_readme.py usage
~~~~~~~~~~~~~~~~~~~

::

    usage: gen_readme.py [-h] [-b ODOO_VID] [-B] [-G GIT_ORGID] [-g OPT_GPL] [-H]
                         [-l ODOO_LAYER] [-L LANG] [-m MODULE_NAME]
                         [-M FORCE_MATURITY] [-n] [-o OUTPUT_FILE]
                         [-P PRODUCT_DOC] [-p PATH_NAME] [-q] [-R] [-r REPOS_NAME]
                         [-t TEMPLATE_NAME] [-T] [-V] [-v] [-W] [-w]

    Generate README

    optional arguments:
      -h, --help            show this help message and exit
      -b ODOO_VID, --odoo-branch ODOO_VID
      -B, --debug-template
      -G GIT_ORGID, --git-org GIT_ORGID
      -g OPT_GPL, --gpl-info OPT_GPL
      -H, --write-index_html
      -l ODOO_LAYER, --layer ODOO_LAYER
                            ocb|module|repository
      -L LANG, --lang LANG  iso code
      -m MODULE_NAME, --module-name MODULE_NAME
                            filename
      -M FORCE_MATURITY, --force-maturity FORCE_MATURITY
                            Alfa,Beta,Mature,Production/stable
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
      -T, --trace-file
      -V, --version         show program's version number and exit
      -v, --verbose         verbose mode
      -W, --write-authinfo
      -w, --suppress-warning

Examples:

::

    # Update Odoo module documentation
    cd ~/odoo_12/l10n-italy/l10n_it_balance # Odoo project directory
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
          Current branch is {{branch}}

In above example then word branch after statement $if ia the VAR branch.
The word branch in the second line is a text. The item {{branch}} is the macro, replaced by the value of varaibale branch.

CONDITION may be a python condition or one of follow special condition:

::

    VAR in LIST
    where VAR is a variable to test and LIST is value list space separated
    i.e.
    .. $if branch in '10.0' '11.0' '12.0'

FILE may be a file name. Supported file types are .rst and .csv

::

    i.e.
        .. $include my_description.rst
        .. $include my_table.csv



Macro
~~~~~

Macro currently supported:

.. $include description_macro.csv


Documentation may contains some graphical symbols in format \|symbol\|.
Currently follows symbols are supported:

.. $include usage_gen_readme_sym.csv

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
