.. toctree::
   :maxdepth: 2

Usage
=====


::

    usage: arcangelo.py [-h] [-a] [-B] [-b TO_VERSION] [-C RULE_GROUPS] [-c]
                        [-F FROM_VERSION] [-f] [-G GIT_ORGID]
                        [--git-merge-conflict left|right] [--ignore-pragma] [-i]
                        [-j PYTHON] [-l] [-n] [-o OUTPUT] [-P PACKAGE_NAME]
                        [-R RULES] [-S] [--test-res-msg TEST_RES_MSG] [-v] [-V]
                        [-w] [-y] [--add-rule-group ADD_RULE_GROUP]
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
                            python version, format #.##, 2+3 use future
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
      -y, --assume-yes      force target path creation with different base name
      --add-rule-group ADD_RULE_GROUP
                            Add rule group form file, default is .arcangelo.yml
    
    © 2021-2025 by SHS-AV s.r.l.
    



**arcangelo** is based on rules files located in config directory where arcangelo
is running. Configuration files are yaml formatted.

Python stages
-------------

Source process analysis is split in stages which would enable or disable rules. Process stages are:

    #. "header" -> Initial source stage, include comment lines
    #. "import" -> Import statements
    #. "class_body" -> Inside class, from class to last line (not function)
    #. "function_body" -> Inside function, from def to last line

When stage transition is detected, the transition_stage macro contains the previous value and
stage macro contains new value.
If no import stage was found, on the first class transition transition_stage is set to "import",
so it is possible adding import statements.


Rules
-----

Every rule is list of following format:

    CTX, PYEXPR, EREGEX, (ACTION, PARAMETERS), ...

    where

    * CTX: would be a python context to load rule
    * PYEXPR: would be a python expression for applying the rule
    * EREGEX is  enhanced regular expression for applying the rule
    * ACTION is the action to apply on current item (if PYEXPR and EREGEX are both matched)
    * PARAMETERS are the values supplying to action

The list/tuple (ACTION, PARAMETERS) can be repeated more than once inside rule.


CTX and PYEXPR
~~~~~~~~~~~~~~

CTX and PYEXPR are python expression for applying the rule.
CTX is matched when file is loaded while PYEXPR is matched on every file line.
Valid macros to validate expression are:

EREGEX
~~~~~~

EREGEX is enhanced regular expression (python re) that may be negative
if it starts with ! (exclamation mark).


ACTION and ARGS
~~~~~~~~~~~~~~~

ACTION is applied on current item (file or line) if CTX and PYEXPR and EREGEX are True.

    ACTION values for lines:

    * **s**: substitute REGEX REPLACE_TEXT
    * **d**: delete line; stop immediately rule processing and re-read the line
    * **i**: insert line before current line
    * **a**: append line after current line
    * **$**: execute FUNCTION
    * **+**: set trigger TRIGGER_NAME (from 1st group of matching regex)
    * **-**: reset trigger TRIGGER_NAME
    * **=**: execute python code


    ACTION values for files:

    * **mv**: mv current file to new fqn
    * **rm**: remove file
    * **no**: no action done

Action **substitute**: "s REGEX REPLACE_TEXT"

    * The 1.st item is the EREGEX to search for replace (negate is not applied)
    * The 2.nd item is the text to replace which can contain macros like %(classname)s

Action **delete**: "d"

    * Delete current line
    * Break rules analyzing
    * Must be the last action of the rule

Action **insert**: "i text"

    * Insert text before current line
    * Must be the last action of the rule

Action **append**: "a text"

    * Append text after current line
    * Must be the last action of the rule

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

Action **set trigger**: "+ TRIGGER name [value]"

    * Set a trigger value to match next line contexts
    * Value of trigger is the 1st match group, enclose by parens
    * If there are no parens in match text, trigger is set to value if supplied
    * If there are no parens in match text and no value is supplied, trigger is set to True
    * If value matches "[+-][0-9]+" value is added or subtracted

Action **reset trigger**: "- TRIGGER name"

    * Reset a boolean trigger value to match next line contexts


Replacing macros in actions and args
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The regular expression EREGEX may contains macro names enclose by "%(name)s".

+--------------------+-------------------------------------------------------------------------------+--------------+
| Name               | Description                                                                   | usage        |
+--------------------+-------------------------------------------------------------------------------+--------------+
| backport_multi     | Processing a backported version (multiple version path)                       | CTX + PYEXPR |
+--------------------+-------------------------------------------------------------------------------+--------------+
| classname          | Name of current class                                                         | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| dedent             | Dedent statement level                                                        | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| final              | Processing final version when multiple version path                           | CTX + PYEXPR |
+--------------------+-------------------------------------------------------------------------------+--------------+
| first_line         | True if current line is the 1st of source (see header too)                    | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| from_major_version | Major version of project by -F switch                                         | CTX + PYEXPR |
+--------------------+-------------------------------------------------------------------------------+--------------+
| fctname            | Current function name                                                         | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| header             | Current line is in the file header (comments and empty lines)                 | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| imported           | Imported packages list                                                        | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| indent             | Space indentation of current line                                             | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| line               | Current line                                                                  | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| migration_multi    | Processing a migrate version with multiple version path                       | CTX + PYEXPR |
+--------------------+-------------------------------------------------------------------------------+--------------+
| mime               | Current file mime                                                             | CTX + PYEXPR |
+--------------------+-------------------------------------------------------------------------------+--------------+
| open_stmt          | # of open parens; if > 0, current line is a continuation line                 | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| python_future      | True if source is python 2 or 3 with future                                   | CTX + PYEXPR |
+--------------------+-------------------------------------------------------------------------------+--------------+
| python_version     | Python version to run source                                                  | CTX + PYEXPR |
+--------------------+-------------------------------------------------------------------------------+--------------+
| singleton          | Singleton rule: may be applied just once                                      | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| stage              | Parsing stage: header,import,class_body,function_body                         | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| stmt_indent        | Space indentation of current statement                                        | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| to_major_version   | Major version of project by -b switch                                         | CTX + PYEXPR |
+--------------------+-------------------------------------------------------------------------------+--------------+
| transition_stage   | Prior parsing stage                                                           | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| try_indent         | The try statement indentation: if >=0 current line is inside try/except block | PYEXPR       |
+--------------------+-------------------------------------------------------------------------------+--------------+
| py23               | Value 2 if python2 else 3 (int)                                               | CTX + PYEXPR |
+--------------------+-------------------------------------------------------------------------------+--------------+



Rules examples
--------------

Replace statement "(int, long)" with "int"

::

    mig_int_long_2_python3:
      ctx: 'py23 == 3'
      search: '\(int, *long\)'
      do:
        - action: 's'
          args:
          - '\(int, *long\)'
          - 'int'

Replace statement "int" with "int, long" for python 2 form:

::

    mig_int_2_python2:
      ctx: 'py23 == 2'
      expr: '"int(" not in line'
      search: 'int'
      do:
        - action: 's'
          args:
          - 'int'
          - 'int, long'


Replace statement "super()" with python 2 form, including current class name "super(classname, self)"

::

    super:
      ctx: 'py23 == 2'
      search: 'super\([^)]*\)'
      do:
        - action: 's'
          args:
          - 'super\(\)'
          - 'super(%(classname)s, self)'

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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.1.0/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.1.0/man
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
