gen_readme.py usage
-------------------

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

    docs
    |--- index rst
    |--- logozero_180x46.png
    \--- rtd*  # (generated form egg-info directory)
    egg-info
    |--- __init__.txt
    |--- description.rst
    |--- descrizione.rst
    |--- features.rst
    |--- oca_diff.rst
    |--- certifications.rst
    |--- prerequisites.rst
    |--- installation.rst
    |--- configuration.rst
    |--- upgrade.rst
    |--- support.rst
    |--- usage.rst
    |--- maintenance.rst
    |--- troubleshooting.rst
    |--- known_issues.rst
    |--- proposals_for_enhancement.rst
    |--- history.rst
    |--- faq.rst
    |--- sponsor.rst
    |--- copyright_notes.rst
    |--- avaiable_addons.rst
    |--- contact_us.rst
    |--- authors.txt
    |--- contributors.txt
    |--- translators.txt
    \--- acknowledges.txt
    readme
    |--- CONTRIBUTORS.rst
    |--- DESCRIPTION.rst
    \--- *.rst  # (Other OCA docs)

Predefined template structire is:

::

    tools
      \--- templates
            |--- Odoo
            |      |--- contact_us.rst
            |      |--- default_authors.txt
            |      |--- default_contributors.txt
            |      |--- default_copyright_notes.rst
            |      |--- default_description.rst
            |      |--- default_descrizione.rst
            |      |--- default_installation.rst
            |      |--- default_maintenance.rst
            |      |--- default_oca_diff.rst
            |      |--- default_proposals_for_enhancement.rst
            |      |--- default_quality
            |      |--- endorsement.rst
            |      |--- default_support.rst
            |      |--- default_troubleshooting.rst
            |      |--- default_upgrade.rst
            |      |--- header_acknowledges.txt
            |      |--- header_troubleshooting.rst
            |      |--- ocb_description.rst
            |      |--- ocb_descrizione.rst
            |      |--- readme_footer.rst
            |      |--- readme_header.rst
            |      |--- readme_index.html
            |      |--- readme_main_module.rst
            |      |--- readme_main_ocb.rst
            |      |--- readme_main_repository.rst
            |      \--- readme_manifest.rst
            |
            \--- pypi
                   |--- default_contributors.txt
                   |--- default_installation.rst
                   |--- module_index.rst
                   |--- module_mainpage.rst
                   |--- readme_footer.rst
                   |--- readme_header.rst
                   |--- readme_main_module.rst
                   |--- readme_main_repository.rst
                   \--- repository_mainpage.rst


Statements
~~~~~~~~~~

Following statements may be used in documentation:

::

    .. $if python_condition
    .. $elif python_condition
    .. $else
    .. $fi

    .. $include filename
    .. $block filename
    .. $set assignment


Macro
~~~~~

Macro currently supported:

.. $include macro.rst


Documentation may contains some graphical symbols in format \|symbol\|.
Currently follows symbols are supported:

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


Macro used in documentation templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following macroes may be declared in package documentation, mainly in __init__.txt file with $set statement.

+---------------------+-----------------------------------------------+
| no_section_oca_diff | If value is 1 the section oca_diff is skipped |
+---------------------+-----------------------------------------------+
| no_pypy             | Value 1 means module is not a pypi package    |
+---------------------+-----------------------------------------------+
