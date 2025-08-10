::

    $(arcangelo -h)


**arcangelo** is based on rules files located in config directory where arcangelo
is running. Configuration files are yaml formatted.

**Python stages**

Source process analysis is split in stages which would enable or disable rules. Process stages are:

    #. "header" -> Initial source stage, include comment lines
    #. "import" -> Import statements
    #. "class_body" -> Inside class, from class to last line (not function)
    #. "function_body" -> Inside function, from def to last line

When stage transition is detected, the transition_stage macro contains the previous value and
stage macro contains new value.
If no import stage was found, on the first class transition transition_stage is set to "import",
so it is possible adding import statements.


**Rules**

Every rule is list of following format:

    CTX, PYEXPR, EREGEX, (ACTION, PARAMETERS), ...

    where

    * CTX: would be a python context to load rule
    * PYEXPR: would be a python expression for applying the rule
    * EREGEX is  enhanced regular expression for applying the rule
    * ACTION is the action to apply on current item (if PYEXPR and EREGEX are both matched)
    * PARAMETERS are the values supplying to action

The list/tuple (ACTION, PARAMETERS) can be repeated more than once inside rule.


**CTX and PYEXPR are python expression** for applying the rule. CTX is matched when file is loaded
while PYEXPR is matched on every file line. Valid macroes to validate expression are:


**EREGEX is enhanced regular expression** is a regular expression (python re) that may be negative
if it starts with ! (exclamation mark).


**ACTION is applied if CTX and PYEXPR and eregex are True**:

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


**Python test and replacing macros**.

The regular expression EREGEX may contains macroes enclose by "%(name)s".

Examples.

Replace statement "(int, long)" with "int"

::

    int_long:
      search: '\(int, *long\)'
      do:
        - action: 's'
          args:
          - '\(int, *long\)'
          - 'int'

Replace statement "int" with "int, long" for python 2 form:

::

    int:
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
      ctx: 'python_version == "2.7"'
      search: 'super\([^)]*\)'
      do:
        - action: 's'
          args:
          - 'super\(\)'
          - 'super(%(classname)s, self)'


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

Action **set trigger**: "+ TRIGGER [value]"

    * Set a trigger value to match next line contexts
    * Value of trigger is the 1st match group, enclose by parens
    * If there are no parens in match text, trigger is set to value if supplied
    * If there are no parens in match text and no value is supplied, trigger is set to True
    * If value matches "[+-][0-9]+" value is added or subtracted
