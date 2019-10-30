Files and directories
---------------------

Document structure is:

::

    docs
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


Statements
----------

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
-----

Macro currently suppported:

.. $include macro.rst


Documentation may contains some graphical symbols in format |symbol|.
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
-------------------------------------

Following macroes may be declared in package documentation, mainly in __init__.txt file with $set statement.

+---------------------+-----------------------------------------------+
| no_section_oca_diff | If value is 1 the section oca_diff is skipped |
+---------------------+-----------------------------------------------+
| no_pypy             | Value 1 means module is not a pypi package    |
+---------------------+-----------------------------------------------+