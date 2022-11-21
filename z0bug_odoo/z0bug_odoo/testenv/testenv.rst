Test Environment v2.0.3
=======================

Overview
--------

EnvTest makes available the test environment ready to use in order to test your Odoo
module in easy way.

The purpose of this software are:

* Create the Odoo test environment with records to use for your test called "SetupEnv"
* Make available some useful functions to test your module test (in z0bug_odoo)
* Simulate the wizard to test wizard functions (wizard simulator)

Tests are based on test environment created by module mk_test_env in repository
https://github.com/zeroincombenze/zerobug-test

How to use
----------

Copy this file in tests directory of your module.
Please copy the documentation testenv.rst file in your module.
Your python test file have to contain some following example lines:

    import os
    import logging
    from .testenv import MainTest as SingleTransactionCase

    _logger = logging.getLogger(__name__)

    TEST_RES_PARTNER = {...}
    TEST_SETUP_LIST = ["res.partner", ]

    class MyTest(SingleTransactionCase):

        def setUp(self):
            super().setUp()
            data = {"TEST_SETUP_LIST": TEST_SETUP_LIST}
            for resource in TEST_SETUP_LIST:
                item = "TEST_%s" % resource.upper().replace(".", "_")
                data[item] = globals()[item]
            self.declare_all_data(data)
            self.setup_env(what)         # Create test environment

        def tearDown(self):
            super().tearDown()
            if os.environ.get("ODOO_COMMIT_TEST", ""):
                # Save test environment, so it is available to use
                self.env.cr.commit()     # pylint: disable=invalid-commit
                _logger.info("✨ Test data committed")

        def test_mytest(self):
            ...

        def test_mywizard(self):
            self.wizard(...)             # Test requires wizard simulator

Requirements
------------

Ths software requires:

* python_plus PYPI package
* z0bug_odoo PYPI package
* python 2.7 / 3.6 / 3.7 / 3.8

How to test
-----------

Setup environment is created by setup_env() function. Data must be supplied by
add_model_data() function.
You can create more test environments called group; if no name is issued
the "base" name is used.

You can run your tests after test environment is created by setup_env().
If you run setup_env() after test execution, the test environment will be recreated.
However the recreated test environment should be different from the first environment.
Some records may be no reset, i.e. an invoice paid the test execution cannot be reset.

If you have more test classes, every class has the its own environemnt
and test environment may be created more times in this way.

Model data declaration
----------------------

Each model is declared in a dictionary which key which is the external
reference used to retrieve the record.
i.e. the following record is named 'z0bug.partner1' in res.partner:

    self.add_test_data(
        "res.partner",
        {
            "z0bug.partner1": {
                "name": "Alpha",
                "street": "1, First Avenue",
                ...
            }
        }
    )

external_reference
------------------

Every record is labelled by an external reference. The external reference ma be:

* Odoo external reference, format "module.name"
* Test reference, format "z0bug.name"
* Key value, format "external.key"
* 2 keys reference, for parent/detail relationship,
  format "external.key_line" or "z0bug.name_line"

Odoo external reference is a record od ir.model.data; you can see them from
Odoo GUI interface.
Test reference are like Odoo external reference but they are visibile just
in the test environment. They are identified by "z0bug." prefix.
External key reference is the key value used to retrieve the record.
Field used to search may be declared by test software.
If no field is declared the "code" or "name" fields are used;
for account.tax the "description" is used. External key reference
is prefixed by "external."
The 2 keys reference, is the 2 level model (parent/detail relationship)
to key the child record of parent record. The key MUST BE the same key of
parent record plus "_" plus line identifier (usually sequence field".
i.e. "z0bug.invoice_1_3" means: line with sequence 3 of account.invoice.line
which is child of record "z0bug._invoice_1" of account invoice.


Data values
-----------

Data values may be raw data (string, number, dates, etc.) or external reference
or some macro.
You can declare data value on your own but you can discover th full test environment
in https://github.com/zeroincombenze/zerobug-test/mk_test_env/ and get data
from this environment.

company_id
~~~~~~~~~~

If value is empty, user company is used. This behavir is not applied on
"product.product", "product.template", "res.partner" and "res.users" models.

boolean
~~~~~~~

You can declare boolean value:

* by python boolean False or True
* by integer 0 o 1
* by string "0" / "False" or "1" / "True"

    self.add_test_data(
        "res.partner",
        {
            "z0bug.partner1": {
                "supplier": False,
                "customer": "True",
                "is_company": 1,
            }
        }
    )

char / text
~~~~~~~~~~~

Char and Text values are python string

    self.add_test_data(
        "res.partner",
        {
            "z0bug.partner1": {
                "name": "Alpha",
                "street": "1, First Avenue",
                ...
            }
        }
    )

integer / float / monetary
~~~~~~~~~~~~~~~~~~~~~~~~~~

Integer, Floating and Monetary values are python integer or float. If numeric value is issued as string,
it is internally converted as integer/float.

    self.add_test_data(
        "res.partner",
        {
            "z0bug.partner1": {
                "color": 1,
                "credit_limit": 500.0,
                "payment_token_count": "0",
            }
        }
    )

date / datetime
~~~~~~~~~~~~~~~

Date and Datetime value are managed in special way.
They are processed by compute_date() function (read below).
You can issue a single value or a 2 values list, 1st is the date,
2nd is the reference date.

    self.add_test_data(
        "res.partner",
        {
            "z0bug.partner1": {
                "activity_date_deadline": "####-1>-##",    # Next month
                "signup_expiration": "###>-##-##",         # Next year
                "date": -1,                                # Yesterday
                "last_time_entries_checked":
                    [+2, another_date]                     # 2 days after another day
            }
        }
    )

many2one
~~~~~~~~

You can issue an integer (if you exactly know the ID) or an external reference.
Read above about external reference.

    self.add_test_data(
        "res.partner",
        {
            "z0bug.partner1": {
                "country_id": "base.it",                   # Odoo external reference
                "property_account_payable_id":
                    "z0bug.customer_account",              # Test record
                "title": "external.Mister"                 # Record with name=="Mister"
            }
        }
    )

one2many / many2many
~~~~~~~~~~~~~~~~~~~~

The one2many and many2many field may contains one or more ID; every ID use
the many2one notation using external reference.
Value may be a string (just 1 value) oa a list.

    self.add_test_data(
        "res.partner",
        {
            "z0bug.partner1": {
                "bank_ids":
                    [
                        "base.bank_partner_demo",
                        "base_iban.bank_iban_china_export",
                    ],
                "category_id": "base.res_partner_category_0"
            }
        }
    )

binary (no yet implemented)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Binary file are supplied with os file name. Test environment load file and
get binary value.

Functions
---------

declare_resource_data
~~~~~~~~~~~~~~~~~~~~~

Declare data to load on setup_env().

def declare_resource_data(self, resource, data, name=None, group=None, merge=None)

    resource (str): Odoo model name, i.e. "res.partner"
    data (dict): record data
    name (str): label of dataset; default is resource name
    group (str): used to manager group data; default is "base"
    merge (str): merge data with public data (currently just "zerobug")

get_resource_data
~~~~~~~~~~~~~~~~~

Get declared resource data; may be used to test compare.

def get_resource_data(self, resource, xref, group=None):

    resource (str): Odoo model name or name assigned, i.e. "res.partner"
    xref (str): external reference
    group (str): if supplied select specific group data; default is "base"

get_resource_data_list
~~~~~~~~~~~~~~~~~~~~~~

Get declared resource data list.

def get_resource_data_list(self, resource, group=None):

    resource (str): Odoo model name or name assigned, i.e. "res.partner"
    group (str): if supplied select specific group data; default is "base"

get_resource_list
~~~~~~~~~~~~~~~~~

Get declared resource list.

def get_resource_list(self, group=None):

    group (str): if supplied select specific group data; default is "base"

compute_date
~~~~~~~~~~~~

Compute date or datetime against today or a reference date. Date may be:

* python date/datetime value
* string with ISO format "YYYY-MM-DD" / "YYYY-MM-DD HH:MM:SS"
* string value that is a relative date against today / reference date

Relative string format is like ISO, with 3 groups separated by '-' (dash).
Every group may be an integer or a special notation:

* starting with '<' meas subtract; i.e. '<2' means minus 2
* ending with '>' meas add; i.e. '2>' means plus 2
* '#' with '<' or '>' means 1; i.e. '<###' means minus 1
* all '#' means same value of reference date

A special notation '+N' and '-N', where N is an integer means add N days
or subtract N day from reference date.
Here, in following examples, are used python iso date convention:

* '+N': return date + N days to refdate (python timedelta)
* '-N': return date - N days from refdate (python timedelta)
* '%Y-%m-%d': strftime of issued value
* '%Y-%m-%dT%H:%M:%S': same datetime
* '%Y-%m-%d %H:%M:%S': same datetime
* '####-%m-%d': year from refdate (or today), month '%m', day '%d'
* '####-##-%d': year and month from refdate (or today), day '%d'
* '2022-##-##': year 2022, month and day from refdate (or today)
* '<###-%m-%d': year -1  from refdate (or today), month '%m', day '%d'
* '<001-%m-%d': year -1  from refdate (or today), month '%m', day '%d'
* '<###-#>-%d': year -1  from refdate, month +1 from refdate, day '%d'
* '<005-2>-##': year -5, month +2 and day from refdate

Notes:
    Returns a ISO format string.
    Returned date is always a valid date; i.e. '####-#>-31',
    with ref month January result '####-02-31' becomes '####-03-03'
    To force last day of month, set '99': i.e. '####-<#-99' becomes the
    last day of previous month of refdate

def compute_date(self, date, refdate=None):

    date (date or string or integer): formula; read aboove
    refdate (date or string): reference date
