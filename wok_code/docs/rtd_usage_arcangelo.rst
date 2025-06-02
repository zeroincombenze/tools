.. toctree::
   :maxdepth: 2

Digest of arcangelo
===================


::

    usage: arcangelo.py [-h] [-a] [-B] [-b TO_VERSION] [-C RULE_GROUPS] [-c]
                        [-F FROM_VERSION] [-f] [-G GIT_ORGID]
                        [--git-merge-conflict left|right] [--ignore-pragma] [-i]
                        [-j PYTHON] [-l] [-n] [-o OUTPUT] [-P PACKAGE_NAME]
                        [-R RULES] [-S] [--test-res-msg TEST_RES_MSG] [-v] [-V]
                        [-w] [--add-rule-group ADD_RULE_GROUP]
                        [path ...]
    
    Beautiful source file
    
    positional arguments:
      path
    
    options:
      -h, --help            show this help message and exit
      -a, --lint-anyway     set to True when migrate software
      -B, --debug           add comment with applied rule: do not use in
                            production
      -b TO_VERSION, --to-version TO_VERSION
      -C RULE_GROUPS, --rule-groups RULE_GROUPS
                            Rule groups (comma separated) to parse (use + for
                            adding, - for removing) use switch -l to see default
                            groups list
      -c, --copyright-check
      -F FROM_VERSION, --from-version FROM_VERSION
      -f, --force           Parse file even containing '# flake8: noqa' or '#
                            pylint: skip-file'
      -G GIT_ORGID, --git-org GIT_ORGID
      --git-merge-conflict left|right
                            Keep left or right side code after git merge conflict
      --ignore-pragma       ignore coding utf-8 declaration
      -i, --in-place
      -j PYTHON, --python PYTHON
                            python version, format #.##, 2-3 use future
      -l, --list-rules      list rule groups (-ll list with rules too, -lll full
                            list)
      -n, --dry-run         do nothing (dry-run)
      -o OUTPUT, --output OUTPUT
      -P PACKAGE_NAME, --package-name PACKAGE_NAME
      -R RULES, --rules RULES
                            Rules (comma separated) to parse (use - for removing)
                            use switch -ll to see default rules list
      -S, --string-normalization
                            force double quote enclosing strings
      --test-res-msg TEST_RES_MSG
      -v, --verbose
      -V, --version         show program's version number and exit
      -w, --no-parse-with-formatter
                            do nor execute black or prettier on modified files
      --add-rule-group ADD_RULE_GROUP
                            Add rule group form file, default is .arcangelo.yml
    
    © 2021-2025 by SHS-AV s.r.l.
    



**arcangelo** is based on rules files located in config directory where arcangelo
is running. Configuration files are yaml formatted.

Every rule is list of following format:

    PYEREX, (ACTION, PARAMETERS), ...

    where

    * PYEREX is (python expression + enhanced regular expression) for applying the rule
    * ACTION is the action to apply on current item (if PYEREX is matched)
    * PARAMETERS are the values supplying to action

The list/tuple (ACTION, PARAMETERS) can be repeated more than once under PYEREX


**PYEREX is (python expression + enhanced regular expression)** is a set of 3
distinct expressions, which are:

    #. Python expression (in order to apply eregex): enclosed by double braces
    #. Status eregex match (in order to apply eregex): enclosed by parens
    #. Applicable eregex to match item

    ACTION is applied if (python expression AND status eregex AND applicable eregex);
    the undeclared python expression or undeclared status eregx returns always true.

    eregex is a regular expression (python re) that may be negative if it starts with !
    (exclamation mark)

    Examples:

+-----+--------------------+-----------------------------------------------------------+---------------------------------------------------------+
| Pos | Example            | Note                                                      | Action                                                  |
+-----+--------------------+-----------------------------------------------------------+---------------------------------------------------------+
| 1   | REGEX              | REGEX is a python re                                      | item is processed if it matches REGEX                   |
+-----+--------------------+-----------------------------------------------------------+---------------------------------------------------------+
| 2   | !REGEX             | REGEX is a python re                                      | item is processes if it does not match REGEX            |
+-----+--------------------+-----------------------------------------------------------+---------------------------------------------------------+
| 3   | \\!REGEX           | REGEX is a python re beginning with ! (exclamation point) | like case 1                                             |
+-----+--------------------+-----------------------------------------------------------+---------------------------------------------------------+
| 4   | !(RE)REGEX         | RE and REGEX are two python re                            | if item does not match (by search) the RE, apply rule 1 |
+-----+--------------------+-----------------------------------------------------------+---------------------------------------------------------+
| 5   | \{\{EXPR\}\}EREGEX | EXPR is double expression                                 | EREGEX is processed if pythonic EXPR is true            |
+-----+--------------------+-----------------------------------------------------------+---------------------------------------------------------+



    * !(import xyz)import -> Rules is applied if matches the statemente "import" but not "import zyz"
    * \{\{self.to_major_version>10\}\}import something -> If target Odoo version is >10.0 matches statement "import something", otherwise ignore rule
    * \{\{self.from_major_version<=10\}\}import something -> If original Odoo version is <=10.0 matches statement "import something", otherwise ignore rule
    * \{\{self.python_version==3.10\}\}open -> If python version is 3.10, matches statemente import, otherwise ignore rule
    * \{\{self.py23==3\}\}open -> If python major version is 3, matches statemente import, otherwise ignore rule

**ACTION is the action will be executed** when EREGEX is True or when EREGEX fails if action begins with "/" (slash).

    **ACTION values**:

    * **s**: substitute REGEX REPLACE_TEXT
    * **d**: delete line; stop immediately rule processing and re-read the line
    * **i**: insert line before current line
    * **a**: append line after current line
    * **$**: execute FUNCTION
    * **+**: set trigger TRIGGER_NAME (from 1st group of matching regex)
    * **-**: reset trigger TRIGGER_NAME
    * **=**: execute python code

**Python test and replacing macros**.

Above you can find some simple example of python expression. The following table
contains the list of values can used in python expression or in text replacement for
substitute action. For example, the value classname can be used in following python
expression:

::

    {\{self.classname=="MyClass"}}

while in replacement text the form is:

::

    's' super() super(%(classname)s)

Value list:

+--------------------+---------------------------------------------------------------------------+
| Name               | Description                                                               |
+--------------------+---------------------------------------------------------------------------+
| backport_multi     | Processing a backported version (multiple version path)                   |
+--------------------+---------------------------------------------------------------------------+
| classname          | Name of current class                                                     |
+--------------------+---------------------------------------------------------------------------+
| dedent             | Dedent statement level                                                    |
+--------------------+---------------------------------------------------------------------------+
| final              | Processing final version when multiple version path                       |
+--------------------+---------------------------------------------------------------------------+
| first_line         | True if current line is the 1st of source (see header too)                |
+--------------------+---------------------------------------------------------------------------+
| from_major_version | Major version of project by -F switch                                     |
+--------------------+---------------------------------------------------------------------------+
| header             | Current line is in the file header (comments and empty lines)             |
+--------------------+---------------------------------------------------------------------------+
| imported           | Imported packages list                                                    |
+--------------------+---------------------------------------------------------------------------+
| indent             | Space indentation of current line                                         |
+--------------------+---------------------------------------------------------------------------+
| migration_multi    | Processing a migrate version with multiple version path                   |
+--------------------+---------------------------------------------------------------------------+
| mime               | Current file mime                                                         |
+--------------------+---------------------------------------------------------------------------+
| open_stmt          | # of open parens; if > 0, current line is a continuation line             |
+--------------------+---------------------------------------------------------------------------+
| python_future      | True if source is python 2 and 3 with future                              |
+--------------------+---------------------------------------------------------------------------+
| stage              | Parsing stage: pre,header,import,class_body,function_body,comment         |
+--------------------+---------------------------------------------------------------------------+
| stmt_indent        | Space indentation of current statement                                    |
+--------------------+---------------------------------------------------------------------------+
| to_major_version   | Major version of project by -b switch                                     |
+--------------------+---------------------------------------------------------------------------+
| transition_stage   | Prior parsing stage                                                       |
+--------------------+---------------------------------------------------------------------------+
| try_indent         | try statement indentation: if >=0 current line is inside try/except block |
+--------------------+---------------------------------------------------------------------------+
| py23               | Value 2 if python2 else 3 (int)                                           |
+--------------------+---------------------------------------------------------------------------+



Action **substitute**: "s REGEX REPLACE_TEXT"

    * The 1.st item is the EREGEX to search for replace (negate is not applied)
    * The 2.nd item is the text to replace which can contain macros like %(classname)s

Action **delete**: "d"

    * Delete current line
    * Break rules analyzing

Action **insert**: "i text"

    * Insert text before current line

Action **append**: "a text"

    * Append text after current line

Action **execute**: "$ FUNCTION"

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

Follow rule replace "@api.one" with "# @api.one" and adds comment line:

::

    no_api_mix:
      match: '^ *@api\.(one|returns|cr|model_cr|model_cr_context|v8|noguess)'
      do:
        - action: 's'
          args:
          - '@api\.(one|returns|cr|model_cr|model_cr_context|v8|noguess)'
          - '# @api.\1'
        - action: 'a'
          args:
          - '# TODO> Update code to multi or add self.ensure_one()'

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
