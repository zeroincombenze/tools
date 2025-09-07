::

    $(arcangelo -h)


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

.. $include rules_usage_arcangelo.csv

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

.. $include rules_usage_items.csv

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
