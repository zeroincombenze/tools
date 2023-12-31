::

    $(arcangelo -h)


**arcangelo** is based on rules files located in config directory where arcangelo
is running. Configuration files are yaml formatted.

Every rule is list of following format:

    EREGEX, (ACTION, PARAMETERS), ...

where

    * EREGEX is an enhanced regular expression for applying the rule
    * ACTION is the action to apply on current line
    * PARAMETERS are the values to supply on action

The list/tuple (ACTION, PARAMETERS) can be repeated more than once


**EREGEX is an enhanced regular expression**; the format are

.. $include rules_usage_arcangelo.csv

Notes:

* !(import xyz)import -> Rules is applied if matches the statemente "import" but not "import zyz"
* \{\{self.to_major_version>10\}\}import something -> If target Odoo version is >10.0 matches statement "import something", otherwise ignore rule
* \{\{self.from_major_version<=10\}\}import something -> If original Odoo version is <=10.0 matches statement "import something", otherwise ignore rule
* \{\{self.python_version==3.10\}\}open -> If python version is 3.10, matches statemente import, otherwise ignore rule
* \{\{self.py23==3\}\}open -> If python major version is 3, matches statemente import, otherwise ignore rule

**ACTION is the action will be executed** when EREGEX is True or when EREGEX fails if action begins with "/" (slash).
ACTION can submitted to Odoo or python version:

* +[0-9] means from Odoo/python major version
* -[0-9] means Odoo major version and older
* +[23]\.[0-9] means from python version
* -[23]\.[0-9] means python version and older

**ACTION values**:

* s: substitute REGEX REPLACE_TEXT
* d: delete line; stop immediately rule processing and re-read the line
* i: insert line before current line
* a: append line after current line
* $: execute FUNCTION
* =: execute python code

Action substitute: "s REGEX REPLACE_TEXT"

* The 1.st item is the EREGEX to search for replace (negate is not applied)
* The 2.nd item is the text to replace which can contain macros like %(classname)s

Action execute: "$ FUNCTION"

* Function must return requires break and line offset
* If function requires break, no other rules will be processed
* The value 0 for offset means read next line, the value -1 re-read the current line, +1 skip next line, and so on

Function example:

::

    def FUNCTION(self, nro):
        do_break = False
        offset = 0
        if self.lines[nro] == "<odoo>":
            do_break = True
            offset = 1
        return do_break, offset

Rules examples:

Follow rule replace "except_osv" with "UserError" and other:

::

    -
      - 'from openerp.osv.osv import except_osv'
      -
        - 's'
        - 'from openerp.osv.osv import except_osv'
        - 'from odoo.exceptions import UserError'
