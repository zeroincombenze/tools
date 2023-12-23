Data values may be raw data (string, number, dates, etc.) or external reference
or some macro.
You can declare data value on your own but you can discover the full test environment
in https://github.com/zeroincombenze/zerobug-test/mk_test_env/ and get data
from this environment.

.. note::

    The fields **company_id** and **currency_id** may be empty to use default value.
    If you want to issue no value, do not declare column in model file (csv or xlsx).

You can evaluate the field value engaging a simple python expression inside tags like in
following syntax:

    "<?odoo EXPRESSION ?>"

The expression may be a simple python expression with following functions:

.. $include testenv_usage_expr.csv
