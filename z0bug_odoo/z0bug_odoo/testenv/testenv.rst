Test Environment v2.0.2
=======================

Overview
--------

TestEnv makes available a test environment ready to use in order to test your Odoo
module in quick and easy way.

The purpose of this software are:

* Create the Odoo test environment with records to use for your test
* Make available some useful functions to test your module (in z0bug_odoo)
* Simulate the wizard to test wizard functions (wizard simulator)
* Environment running different Odoo modules versions

Please, pay attention to test data: TestEnv use internal unicode even for python 2
based Odoo (i.e. 10.0). You should declare unicode date whenever is possible.
Note, Odoo core uses unicode even on old Odoo version.

Tests are based on test environment created by module mk_test_env in repository
https://github.com/zeroincombenze/zerobug-test

How to use
----------

Copy this file in tests directory of your module.
Please copy this documentation testenv.rst file in your module too.
The __init__.py must import testenv.
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
            # Add following statement just for get debug information
            self.debug_level = 2
            data = {"TEST_SETUP_LIST": TEST_SETUP_LIST}
            for resource in TEST_SETUP_LIST:
                item = "TEST_%s" % resource.upper().replace(".", "_")
                data[item] = globals()[item]
            self.declare_all_data(data)     # TestEnv swallows the data
            self.setup_env()                # Create test environment

        def tearDown(self):
            super().tearDown()
            if os.environ.get("ODOO_COMMIT_TEST", ""):
                # Save test environment, so it is available to dump
                self.env.cr.commit()     # pylint: disable=invalid-commit
                _logger.info("✨ Test data committed")

        def test_mytest(self):
            _logger.info(
                "🎺 Testing test_mytest"    # Use unicode char to best log reading
            )
            ...

        def test_mywizard(self):
            self.wizard(...)                # Test requires wizard simulator

An important helper to debug is self.debug_level. When you begins your test cycle,
you are hinted to set self.debug_level = 3; then you can decrease the debug level
when you are developing stable tests.
Final code should have self.debug_level = 0.
TestEnv logs debug message with symbol "🐞 " so you can easily recognize them.

Requirements
------------

Ths TestEnv software requires:

* python_plus PYPI package
* z0bug_odoo PYPI package
* python 2.7 / 3.6 / 3.7 / 3.8

TestEnv is full integrated with Zeroincombenze(R) tools.
See https://zeroincombenze-tools.readthedocs.io/
and https://github.com/zeroincombenze/tools.git
Zeroincombenze(R) tools help you to test Odoo module with pycharm.

Model data declaration
----------------------

Each model is declared in a dictionary which key which is the external
reference used to retrieve the record.
i.e. the following record is named 'z0bug.partner1' in res.partner:

    TEST_RES_PARTNER = {
        "z0bug.partner1": {
            "name": "Alpha",
            "street": "1, First Avenue",
            ...
        }
    )

PLease, do not to declare 'product.product' records: they are automatically
created as child of 'product.template'. The external reference must contain
the pattern '_template' (see below).

Magic relationship
------------------

Some models/tables should be managed together, i.e. 'account.move' and 'account.move.line'.
TestEnv manages these models/tables, called header/detail, just as a single object.
Where header record is created, all detail lines are created with header.
To do this job you must declare external reference as explained below (external reference).

Warning: you must declare header and lines data before create header record.

    TEST_SALE_ORDER = {
        "z0bug.order_1": {
            ...
        }
    }
    TEST_SALE_ORDER_LINE = {
        "z0bug.order_1_1": {
            ...
        }
    }
    TEST_SETUP_LIST = ["sale.order", "sale.order.line"]

    class MyTest(SingleTransactionCase):

        def test_something(self):
            data = {"TEST_SETUP_LIST": TEST_SETUP_LIST}
            for resource in TEST_SETUP_LIST:
                item = "TEST_%s" % resource.upper().replace(".", "_")
                data[item] = globals()[item]
            # Declare order data in specific group to isolate data
            self.declare_all_data(data, group="order")
            # Create the full sale order with lines
            self.resource_make(model, xref, group="order")

Another magic relationship is the 'product.template' (product) / 'product.product' (variant) relationship.
Whenever a 'product.template' (product) record is created,
Odoo automatically creates one variant (child) record for 'product.product'.
If your test module does not need to manage product variants you can avoid to declare
'product.product' data even if this model is used in your test data.

For example, you have to test 'sale.order.line' which refers to 'product.product'.
You simply declare a 'product.template' record with external reference user "_template"
magic text.

    TEST_PRODUCT_TEMPLATE = {
        "z0bug.product_template_1": {
            "name": "Product alpha",
            ...
        }
    )
    ...
    TEST_SALE_ORDER_LINE = {
        "z0bug.order_1_1": {
            "product_id": "z0bug.product_product_1",
            ...
        }
    )
    ...
    # Get 'product.template' record
    self.resource_bind("z0bug.product_template_1")
    # Get 'product.product' record
    self.resource_bind("z0bug.product_product_1")


External reference
------------------

Every record is tagged by an external reference.
The external reference may be:

* Ordinary Odoo external reference, format "module.name"
* Test reference, format "z0bug.name"
* Key value, format "external.key"
* 2 keys reference, for header/detail relationship
* Magic reference for 'product.template' / 'product.product'

Ordinary Odoo external reference is a record of 'ir.model.data';
you can see them from Odoo GUI interface.

Test reference are visible just in the test environment.
They are identified by "z0bug." prefix module name.

External key reference is identified by "external." prefix followed by
the key value used to retrieve the record.
The field "code" or "name" are used to search record;
for account.tax the "description" field is used.
Please set self.debug_level = 2 (or more) to log these field keys.

The 2 keys reference needs to address child record inside header record
at 2 level model (header/detail) relationship.
The key MUST BE the same key of the parent record,
plus "_", plus line identifier (usually 'sequence' field).
i.e. "z0bug.move_1_3" means: line with sequence 3 of 'account.move.line'
which is child of record "z0bug.move_1" of 'account.move'.
Please set self.debug_level = 2 (or more) to log these relationships.

For 'product.template' (product) you must use '_template' text in reference.
TestEnv inherit 'product.product' (variant) external reference (read above 'Magic relationship).

Module test execution workflow
------------------------------

Module test execution workflow should be:

    #. Data declaration, in setUp() function
    #. Base data creation, in setUp() function
    #. Supplemental data declaration
    #. Supplemental data creation

Test data may be managed by one or more data group; if not declared,
"base" group name is used. The "base" group must be created at the setUp()
level: it is the base test data.
Testing function may declare and manage other group data. Look at the
following example:

    import os
    import logging
    from .testenv import MainTest as SingleTransactionCase

    _logger = logging.getLogger(__name__)

    TEST_PRODUCT_TEMPLATE = {
        "z0bug.product_template_1": {...}
    }
    TEST_RES_PARTNER = {
        "z0bug.partner1": {...}
    )
    TEST_SETUP_LIST = ["res.partner", "product.template"]

    TEST_SALE_ORDER = {
        "z0bug.order_1": {
            "partner_id": "z0bug.partner1",
            ...
        }
    }
    TEST_SALE_ORDER_LINE = {
        "z0bug.order_1_1": {
            "product_id": "z0bug.product_product_1",
            ...
        }
    )

    class MyTest(SingleTransactionCase):

        def setUp(self):
            super().setUp()
            # Add following statement just for get debug information
            self.debug_level = 2
            data = {"TEST_SETUP_LIST": TEST_SETUP_LIST}
            for resource in TEST_SETUP_LIST:
                item = "TEST_%s" % resource.upper().replace(".", "_")
                data[item] = globals()[item]
            self.declare_all_data(data)     # TestEnv swallows the data
            self.setup_env()                # Create test environment

        def test_something(self):
            data = {"TEST_SETUP_LIST": ["sale.order", "sale.order.line"]}
            for resource in TEST_SETUP_LIST:
                item = "TEST_%s" % resource.upper().replace(".", "_")
                data[item] = globals()[item]
            # Declare order data in specific group to isolate data
            self.declare_all_data(data, group="order")
            # Create the full sale order with lines
            self.resource_make(model, xref, group="order")

Note the external reference are globals and they are visible from any group
while the data is visible just inside group.
You can manage specific table/model data or table/model data group.

Data values
-----------

Data values may be raw data (string, number, dates, etc.) or external reference
or some macro.
You can declare data value on your own but you can discover th full test environment
in https://github.com/zeroincombenze/zerobug-test/mk_test_env/ and get data
from this environment.

company_id
~~~~~~~~~~

If value is empty, user company is used. This behavior is
not applied on "res.users" models.
Fot the "product.product", "product.template" and "res.partner" is searched
for company or null value.

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

Char and Text values are python string; please use unicode whenever is possible.

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

Integer, Floating and Monetary values are python integer or float.
If numeric value is issued as string, it is internally converted
as integer/float.

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
                    [+2, another_date],                    # 2 days after another day
                "message_last_post": "2023-06-26",         # Specific date
            }
        }
    )

many2one
~~~~~~~~

You can issue an integer (if you exactly know the ID)
or an external reference. Read above about external reference.

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

The one2many and many2many field may contains one or more ID;
every ID use the many2one notation using external reference.
Value may be a string (just 1 value) or a list.

    self.add_test_data(
        "res.partner",
        {
            "z0bug.partner1": {
                "bank_ids":
                    [
                        "base.bank_partner_demo",
                        "base_iban.bank_iban_china_export",
                    ],
                "category_id": "base.res_partner_category_0",
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
    merge (str): merge data from public data (currently just "zerobug")

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

add_translation
~~~~~~~~~~~~~~~

Add a translation value for a field of a model.

def add_translation(self, resource, field, tnxl):

    resource (str): Odoo model name, i.e. "res.partner"
    field (str): model field name, i.e. "street"
    tnxl (list/tuple): tuple with (old_value, new_value)

add_translation_xref
~~~~~~~~~~~~~~~~~~~~

Add an alias of an external reference

def add_translation_xref(self, xref, xref_tnxl):

    xref (str): external reference
    xref_tnxl (list/tuple): tuple with (old_value, new_value)
