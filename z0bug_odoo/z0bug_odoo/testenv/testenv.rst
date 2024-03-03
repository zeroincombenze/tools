Test Environment v2.0.17
========================

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

.. note::

    Odoo core uses unicode even on old Odoo version.

Tests are based on test environment created by module mk_test_env in
`repository <https://github.com/zeroincombenze/zerobug-test>`__



How to use
----------

You can locate the recent testenv.py in testenv directory of module
`z0bug_odoo <https://github.com/zeroincombenze/tools/tree/master/z0bug_odoo/testenv>`__

For full documentation visit:
`zero-tools <https://zeroincombenze-tools.readthedocs.io/en/latest/pypi_z0bug_odoo/index.html>`__
or
`z0bug_odoo <https://z0bug-odoo.readthedocs.io/en/latest/>`__
or
`zero-tools (github) <https://github.com/zeroincombenze/tools>`__
or
`github with example modules <https://github.com/zeroincombenze/zerobug-test>`__

Copy the testenv.py file in tests directory of your module.
Please copy the documentation testenv.rst file in your module too.

The __init__.py must import testenv.

::

    from . import testenv
    from . import test_<MY_TEST_FILE>

Your python test file have to contain some following example lines:

::

    import os
    import logging
    from .testenv import MainTest as SingleTransactionCase

    _logger = logging.getLogger(__name__)

    TEST_SETUP_LIST = ["res.partner", ]

    class MyTest(SingleTransactionCase):

        def setUp(self):
            super().setUp()
            # Add following statement just for get debug information
            self.debug_level = 2
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

An important helper to debug is self.debug_level. When you begins your test cycle,
you are hinted to set self.debug_level = 3; then you can decrease the debug level
when you are developing stable tests.
Final code should have self.debug_level = 0.
TestEnv logs debug message with symbol "🐞 " so you can easily recognize them.

Ths TestEnv software requires:

* python_plus PYPI package
* z0bug_odoo PYPI package version 2.0.12
* python 2.7 / 3.6 / 3.7 / 3.8 / 3.9 / 3.10



Model data declaration
~~~~~~~~~~~~~~~~~~~~~~

Each model is declared in a csv file or xlsx file in **test/data** directory of the
module. The file name is the same of model name with dots replaced by undescore.

i.e. below the contents of **res_parter.csv** file:

::

    id,name,street
    z0bug.partner1,Alpha,"1, First Avenue"

The model may also be declared in a dictionary which key which is the external
reference used to retrieve the record.

i.e. the following record declaration is the same of above example; record id is named
``z0bug.partner1`` in res.partner:

::

    TEST_RES_PARTNER = {
        "z0bug.partner1": {
            "name": "Alpha",
            "street": "1, First Avenue",
            ...
        }
    )

.. warning::

    Please, do not to declare ``product.product`` records: they are automatically
    created as child of ``product.template``. The external reference must contain
    the pattern ``_template`` (see below).



Magic relationship
~~~~~~~~~~~~~~~~~~

Some models/tables should be managed together, i.e. **account.move** and **account.move.line**.
TestEnv manages these models/tables, called header/detail, just as a single object.
When header record is created, all detail lines are created with header.
Odoo standard declaration requires the details data in child reference field with
command *0, 0*.
This method make unreadable the source data. Look at the simple follow example with
usually Odoo declaration way:

::

    sale_order_data = {
        "example.order_1": {
            "partner_id": self.env.ref("base.res_partner_1"),
            "origin": "example",
            ...
            "order_line": [
                (0, 0, {
                    "product_id": self.env.ref("product.product_product_1"),
                    "product_qty": 1,
                    "price_unit": 1.23,}),
                (0, 0, {
                    "product_id": self.env.ref("product.product_product_2"),
                    "product_qty": 2,
                    "price_unit": 2.34,}),
            ]
        }

    }

Now look at the same data in internal declaration by **z0bug_odoo**:

::

    TEST_SALE_ORDER = {
        "example.order_1": {
            "partner_id": "base.res_partner_1",
            "origin": "example",
            ...
        }

    }

    TEST_SALE_ORDER_LINE = {
        "example.order_1_1": {
            "product_id": "product.product_product_1",
            "product_qty": 1,
            "price_unit": 1.23,
        },
        "example.order_1_2": {
            "product_id": "product.product_product_2",
            "product_qty": 2,
            "price_unit": 2.34,
        }
    }

As you can see, the data is easy readable and easy updatable. Please, notice:

#. Sale order lines are declared in specific model **sale.order.line**
#. Reference data do not require ``self.env.ref()``: they are automatically referenced

It is also easy write the csv or xlsx file. This is the example with above data

::

    id,partner_id,origin
    example.order_1,base.res_partner_1,example

    id,product_id,product_qty,price_unit
    example.order_1_1,product.product_product_1,1,1.23
    example.order_1_2,product.product_product_2,2,2.34

In your test file you must declare the following statement:

::

    TEST_SETUP_LIST = ["sale.order", "sale.order.line"]

.. warning::

    You must declare header and lines data before create header record


Another magic relationship is the **product.template** (product) / **product.product** (variant)
relationship.
Whenever a **product.template** (product) record is created,
Odoo automatically creates one variant (child) record for **product.product**.
If your test module does not need to manage product variants you can avoid to declare
**product.product** data even if this model is used in your test data.

For example, you have to test **sale.order.line** which refers to **product.product**.
You simply declare a **product.template** record with external reference
uses "_template" magic text.

::

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



Module test execution session
-----------------------------

Introduction
~~~~~~~~~~~~

Module test execution workflow should be:

    #. Data declaration, in setUp() function
    #. Base data creation, in setUp() function
    #. Supplemental data declaration
    #. Supplemental data creation

Test data may be managed by one or more data group; if not declared,
"base" group name is used. The "base" group will be created at the setUp()
level: it is the base test data.
Testing function may declare and manage other group data. Look at the
following example:

::

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
            self.debug_level = 2
            self.setup_env()                # Create base test environment

        def test_something(self):
            # Now add Sale Order data, group "order"
            self.setup_env(group="order", setup_list=["sale.order", "sale.order.line"])

Note the external reference are globals and they are visible from any groups.
After base data is created it starts the real test session. You can simulate
various situation; the most common are:

    #. Simulate web form create record
    #. Simulate web form update record
    #. Simulate the multi-record windows action
    #. Download any binary data created by test
    #. Engage wizard

.. note::

    you can also create / update record with usually create() / write() Odoo function,
    but they do not really simulate the user behavior.
    They do not engage the onchange methods, they do not load any view and so on.

The real best way to test a create session is like the follow example
based on **res.partner model**:

::

        record = self.resource_edit(
            resource="res.partner",
            web_changes=[
                ("name", "Adam"),
                ("country_id", "base.us"),
                ...
            ],
        )

You can also simulate the update session, issuing the record:

::

        record = self.resource_edit(
            resource=record,
            web_changes=[
                ("name", "Adam Prime"),
                ...
            ],
        )

Look at resource_edit() documentation for furthermore details.

In you test session you should need to test a wizard. This test is very easy
to execute as in the follow example that engage the standard language install
wizard:

::

        # We engage language translation wizard with "it_IT" language
        # see "<ODOO_PATH>/addons/base/module/wizard/base_language_install*"
        _logger.info("🎺 Testing wizard.lang_install()")
        act_windows = self.wizard(
            module="base",
            action_name="action_view_base_language_install",
            default={
                "lang": "it_IT"
                "overwrite": False,
            },
            button_name="lang_install",
        )
        self.assertTrue(
            self.is_action(act_windows),
            "No action returned by language install"
        )
        # Now we test the close message
        self.wizard(
            act_windows=act_windows
        )
        self.assertTrue(
            self.env["res.lang"].search([("code", "=", "it_IT")]),
            "No language %s loaded!" % "it_IT"
        )

Look at wizard() documentation for furthermore details.



Data values
-----------

Data values may be raw data (string, number, dates, etc.) or external reference
or some macro.
You can declare data value on your own but you can discover th full test environment
in https://github.com/zeroincombenze/zerobug-test/mk_test_env/ and get data
from this environment.



company_id
~~~~~~~~~~

If value is empty, user company is used.
When data is searched by ``resource_search()`` function the "company_id" field
is automatically filled and added to search domain.
This behavior is not applied on
**res.users**, **res.partner**, **product.template** and **product.product** models.
For these models you must fill the "company_id" field.
For these models ``resource_search()`` function searches for record with company_id
null or equal to current user company.



boolean
~~~~~~~

You can declare boolean value:

* by python boolean False or True
* by integer 0 or 1
* by string "0" or "False" or "1" or "True"

::

    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "supplier": False,
                "customer": "True",
                "is_company": 1,
            }
        }
    )



char / text
~~~~~~~~~~~

Char and Text values are python string; please use unicode whenever is possible
even when you test Odoo 10.0 or less.

You can evalute the field value engaging a simple python expression inside tags like in
following syntax:

    "<?odoo EXPRESSION ?>"

The expression may be a simple python expression with following functions:

+--------------+----------------------------------------+----------------------------------+
| function     | description                            | example                          |
+--------------+----------------------------------------+----------------------------------+
| compute_date | Compute date                           | compute_date('<###-##-##').year  |
+--------------+----------------------------------------+----------------------------------+
| random       | Generate random number from 0.0 to 1.0 | int(random() * 1000)             |
+--------------+----------------------------------------+----------------------------------+
| ref          | Odoo reference self.env.ref()          | ref('product.product_product_1') |
+--------------+----------------------------------------+----------------------------------+
| ref[field]   | field of record of external reference  | product.product_product_1.name   |
+--------------+----------------------------------------+----------------------------------+



::

    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                "name": "Alpha",
                "street": "1, First Avenue"
                # Name of Caserta city
                "city": "<? base.state_it_ce.name ?>",
                # Reference: 'year/123'
                "ref": "<? compute_date('####-##-##')[0:4] + '/123' ?>",
            }
        }
    )



integer / float / monetary
~~~~~~~~~~~~~~~~~~~~~~~~~~

Integer, Floating and Monetary values are python integer or float.
If numeric value is issued as string, it is internally converted
as integer/float.

::


    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "color": 1,
                "credit_limit": 500.0,
                "payment_token_count": "0",
            }
        }
    )



date / datetime
~~~~~~~~~~~~~~~

Date and Datetime value are managed in special way.
They are processed by ``compute_date()`` function (read below).
You can issue a single value or a 2 values list, 1st is the date,
2nd is the reference date.

::

    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "activity_date_deadline": "####-1>-##",    # Next month
                "signup_expiration": "###>-##-##",         # Next year
                "date": -1,                                # Yesterday
                "last_time_entries_checked":
                    [+2, another_date],                    # 2 days after another day
                "message_last_post": "2023-06-26",         # Specific date, ISO format
            }
        }
    )



many2one
~~~~~~~~

You can issue an integer (if you know exactly the ID)
or an external reference. Read above about external reference.

::

    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
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
every ID use the same above many2one notation with external reference.
Value may be a string (just 1 value) or a list.

::

    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "bank_ids":
                    [
                        "base.bank_partner_demo",
                        "base_iban.bank_iban_china_export",
                    ],
                "category_id": "base.res_partner_category_0",
            }
        }
    )

.. note::

    You can also use tha classic Odoo syntax with commands:
    You can integrate classic Odoo syntax with **z0bug_odoo external** reference.

* [0, 0, values (dict)]               # CREATE record and link
* [1, ID (int), values (dict)]        # UPDATE linked record
* [2, ID (int)]                       # DELETE linked record by ID
* [3, ID (int)]                       # UNLINK record ID (do not delete record)
* [4, ID (int)]                       # LINK record by ID
* [5, x] or [5]                       # CLEAR unlink all record IDs
* [6, x, IDs (list)]                  # SET link record IDs



binary
~~~~~~

Binary file are supplied with os file name. Test environment load file and
get binary value. File must be located in **tests/data** directory.

::

    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "image": "z0bug.partner1.png"
            }
        }
    )



External reference for many2one, one2many and many2many fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every record tagged by an external reference may be:

    * Ordinary Odoo external reference ``(a)``, format "module.name"
    * Test reference, format "z0bug.name" ``(b)``
    * Key value, format "external.key" ``(c)``
    * 2 keys reference, for header/detail relationship ``(d)``
    * Magic reference for **product.template** / **product.product** ``(e)``

Ordinary Odoo external reference ``(a)`` is a record of **ir.model.data**;
you can see them from Odoo GUI interface.

Test reference ``(b)`` are visible just in the test environment.
They are identified by "z0bug." prefix module name.

External key reference ``(c)`` is identified by "external." prefix followed by
the key value used to retrieve the record.
If key value is an integer it is the record "id".
The field "code" or "name" are used to search record;
for account.tax the "description" field is used.
Please set self.debug_level = 2 (or more) to log these field keys.

The 2 keys reference ``(d)`` needs to address child record inside header record
at 2 level model (header/detail) relationship.
The key MUST BE the same key of the parent record,
plus "_", plus line identifier (usually **sequence** field).
i.e. ``z0bug.move_1_3`` means: line with sequence ``3`` of **account.move.line**
which is child of record ``z0bug.move_1`` of **account.move**.
Please set self.debug_level = 2 (or more) to log these relationships.

For **product.template** (product) you must use '_template' text in reference ``(e)``.
TestEnv inherit **product.product** (variant) external reference
(read above "Magic relationship").

Examples:

::

    TEST_ACCOUNT_ACCOUNT = {
        "z0bug.customer_account": {
            "code": "", ...
        }
        "z0bug.supplier_account": {
            "code": "111100", ...
        }
    )

    ...

    self.resource_edit(
        partner,
        web_changes = [
            ("country_id", "base.it"),       # Odoo external reference (type a)
            ("property_account_receivable_id",
             "z0bug.customer_account"),      # Test reference (type b)
            ("property_account_payable_id",
             "external.111100"),             # External key (type c)
        ],
    )



Functions
---------

cast_types
~~~~~~~~~~

**cast_types(self, resource, values, fmt=None, group=None, not_null=False)**

Convert resource fields in appropriate type, based on Odoo type.

| Args:
|     resource (str): Odoo model name
|     values (dict): record data
|     fmt (selection): output format
|     group (str): used to manager group data; default is "base"
|
| Returns:
|     Appropriate values

The parameter fmt declares the purpose of casting and declare the returned format of
<2many> fields as follows table:

::

                                    | fmt=='cmd'         | fmt=='id'  | fmt=='py'
    <2many> [(0|1,x,dict)]          | [(0|1,x,dict)] *   | [dict] *   | [dict] *
    <2many> [(0|1,x,xref)]          | [(0|1,x,dict)]     | [dict]     | [dict]
    <2many> [(2|3|4|5,id)]          | as is              | as is      | as is
    <2many> [(2|3|4|5,xref)]        | [(2|3|4|5,id)]     | as is      | as is
    <2many> [(6,0,[ids])]           | as is              | [ids]      | [ids]
    <2many> [(6,0,xref)]            | [(6,0,[id])]       | [id]       | [id]
    <2many> [(6,0,[xref,...])]      | [(6,0,[ids])]      | [ids]      | [ids]
    <2many> dict                    | [(0,0,dict)        | [dict]     | [dict]
    <2many> xref (exists)           | [(6,0,[id])]       | [id]       | [id]
    <2many> xref (not exists)       | [(0,0,dict)]       | [dict]     | [dict]
    <2many> [xref] (exists)         | [(6,0,[id])]       | [id]       | [id]
    <2many> [xref] (not exists)     | [(0,0,dict)]       | [dict]     | [dict]
    <2many> [xref,...] (exists)     | [(6,0,[ids])]      | [ids]      | [ids]
    <2many> [xref,...] (not exists) | [(0,0,dict),(...)] | [dict,...] | [dict,...]
    <2many> [ids] **                | [(6,0,[ids])]      | [ids]      | [ids]
    <2many> id                      | [(6,0,[id])]       | [id]       | [id]
    <2many> "xref,..." (exists)     | [(6,0,[ids])]      | [ids]      | [ids]
    <2many> "xref,..." (not exists) | [(0,0,dict),(...)] | [dict,...] | [dict,...]

    Caption: dict -> {'a': 'A', ..}, xref -> "abc.def", id -> 10, ids -> 1,2,...
    * fields of dict are recursively processed
    ** ids 1-6 have processed as Odoo cmd

fmt ==  'cmd' means convert to Odoo API format: <2many> fields are returned with
prefixed 0|1|2|3|4|5|6 value (read _cast_2many docs).

fmt == 'id' is like 'cmd': prefix are added inside dict not at the beginning.

fmt == 'py' means convert to native python (remove all Odoo command prefixes).
It is used for comparison.

When no format is required (fmt is None), some conversion may be not applicable:

<many2one> field will be left unchanged when invalid xref is issued and <2many>
field me will be left unchanged when one or more invalid xref are issued.

str, int, long, selection, binary, html fields are always left as is

date, datetime fields and fmt=='cmd' and python2 (odoo <= 10.0) return ISO format
many2one fields, if value is (int|long) are left as is; if value is (xref) the
id of xref is returned.

.. note::

    Odoo one2many valid cmd are: 0,1 and 2 (not checked)

store_resource_data
~~~~~~~~~~~~~~~~~~~

**store_resource_data(self, resource, xref, values, group=None, name=None)**

Store a record data definition for furthermore use.

| Args:
|     resource (str): Odoo model name
|     xref (str): external reference
|     values (dict): record data
|     group (str): used to manager group data; default is "base"
|     name (str): label of dataset; default is resource name


Data stored is used by ``setup_env()`` function and/or by:

* ``resource_create()`` without values
* ``resource_write()`` without values
* ``resource_make()`` without values


compute_date
~~~~~~~~~~~~

**compute_date(self, date, refdate=None)**

Compute date or datetime against today or a reference date.

| Args:
|     date (date or string or integer): text date formula
|     refdate (date or string): reference date

Date may be:

* python date/datetime value
* string with ISO format "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS"
* string value that is a relative date against today or reference date

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
* '2024-##-##': year 2024, month and day from refdate (or today)
* '<###-%m-%d': year -1  from refdate (or today), month '%m', day '%d'
* '<001-%m-%d': year -1  from refdate (or today), month '%m', day '%d'
* '<###-#>-%d': year -1  from refdate, month +1 from refdate, day '%d'
* '<005-2>-##': year -5, month +2 and day from refdate

Notes:
    * Returns a ISO format string.
    * Returned date is a valid date; i.e. '####-#>-31', with ref month January result '####-02-31' becomes '####-03-03'
    * To force last day of month, set '99': i.e. '####-<#-99' becomes the last day of previous month of refdate


resource_browse
~~~~~~~~~~~~~~~

**resource_browse(self, xref, raise_if_not_found=True, resource=None, group=None)**

Bind record by xref, searching it or browsing it.
This function returns a record using issued parameters. It works in follow ways:

* With valid xref it work exactly like self.env.ref()
* If xref is an integer it works exactly like self.browse()
* I xref is invalid, xref is used to search record
    * xref is searched in stored data
    * xref ("MODULE.NAME"): if MODULE == "external", NAME is the record key

| Args:
|     xref (str): external reference
|     raise_if_not_found (bool): raise exception if xref not found or
|                                if more records found
|     resource (str): Odoo model name, i.e. "res.partner"
|     group (str): used to manager group data; default is "base"
|
| Returns:
|     obj: the Odoo model record
|
| Raises:
|     ValueError: if invalid parameters issued

resource_create
~~~~~~~~~~~~~~~

Create a test record and set external ID to next tests.
This function works as standard Odoo create() with follow improvements:

* It can create external reference too
* It can use stored data if no values supplied
* Use new api even on Odoo 7.0 or less

| Args:
|     resource (str): Odoo model name, i.e. "res.partner"
|     values (dict): record data (default stored data)
|     xref (str): external reference to create
|     group (str): used to manager group data; default is "base"
|
| Returns:
|     obj: the Odoo model record, if created


resource_write
~~~~~~~~~~~~~~

Update a test record.
This function works as standard Odoo write() with follow improvements:

* If resource is a record, xref is ignored (it should be None)
* It resource is a string, xref must be a valid xref or an integer
* If values is not supplied, record is restored to stored data values

def resource_write(self, resource, xref=None, values=None, raise_if_not_found=True, group=None):

    Args:
        resource (str|obj): Odoo model name or record to update
        xref (str): external reference to update: required id resource is string
        values (dict): record data (default stored data)
        raise_if_not_found (bool): raise exception if xref not found or if more records found
        group (str): used to manager group data; default is "base"

    Returns:
        obj: the Odoo model record

    Raises:
        ValueError: if invalid parameters issued

resource_make
~~~~~~~~~~~~~

Create or write a test record.
This function is a hook to resource_write() or resource_create().

def resource_make(self, resource, xref, values=None, group=None):

declare_resource_data
~~~~~~~~~~~~~~~~~~~~~

Declare data to load on setup_env().

def declare_resource_data(self, resource, data, name=None, group=None, merge=None)

    Args:
        resource (str): Odoo model name, i.e. "res.partner"
        data (dict): record data
        name (str): label of dataset; default is resource name
        group (str): used to manager group data; default is "base"
        merge (str): merge data with public data (currently just "zerobug")

    Raises:
        TypeError: if invalid parameters issued

declare_all_data
~~~~~~~~~~~~~~~~

Declare all data to load on setup_env().

def declare_resource_data(self, resource, data, name=None, group=None, merge=None)

    Args:
        message (dict): data message
        TEST_SETUP_LIST (list): resource list to load
        TEST_* (dict): resource data; * is the uppercase resource name where dot are replaced by "_"; (see declare_resource_data)
        group (str): used to manager group data; default is "base"
        merge (str): merge data with public data (currently just "zerobug")

    Raises:
        TypeError: if invalid parameters issuedd

get_resource_data
~~~~~~~~~~~~~~~~~

Get declared resource data; may be used to test compare.

def get_resource_data(self, resource, xref, group=None):

    Args:
        resource (str): Odoo model name or name assigned, i.e. "res.partner"
        xref (str): external reference
        group (str): if supplied select specific group data; default is "base"

    Returns:
        dictionary with data or empty dictionary

get_resource_data_list
~~~~~~~~~~~~~~~~~~~~~~

Get declared resource data list.

def get_resource_data_list(self, resource, group=None):

    Args:
        resource (str): Odoo model name or name assigned, i.e. "res.partner"
        group (str): if supplied select specific group data; default is "base"

    Returns:
        list of data

get_resource_list
~~~~~~~~~~~~~~~~~

Get declared resource list.

def get_resource_list(self, group=None):

    Args:
        group (str): if supplied select specific group data; default is "base"

setup_company
~~~~~~~~~~~~~

Setup company values for current user.

This function assigns company to current user and / or can create xref aliases
and /or can update company values.
This function is useful in multi companies tests where different company values
will be used in different tests. May be used in more simple test where company
data will be updated in different tests.
You can assign partner_xref to company base by group; then all tests executed
after setup_env(), use the assigned partner data for company of the group.
You can also create more companies and assign one of them to test by group.

def setup_company(self, company, xref=None, partner_xref=None, values={}, group=None):

    Args:
        company (obj): company to update; if not supplied a new company is created
        xref (str): external reference or alias for main company
        partner_xref (str): external reference or alias for main company partner
        values (dict): company data to update immediately
        group (str): if supplied select specific group data; default is "base"

    Returns:
        default company for user

setup_env
~~~~~~~~~

Create all record from declared data.

This function starts the test workflow creating the test environment.
Test data must be declared before engage this function with declare_all_data()
function (see above).
setup_env may be called more times with different group value.
If it is called with the same group, it recreates the test environment with
declared values; however this feature might do not work for some reason: i.e.
if test creates a paid invoice, the setup_env() cannot unlink invoice.
If you want to recreate the same test environment, assure the conditions for
unlink of all created and tested records.
If you create more test environment with different group you can use all data,
even record created by different group.
In this way you can test a complex process the evolved scenario.

def setup_env(self, lang=None, locale=None, group=None):

    Args:
        lang (str): install & load specific language
        locale (str): install locale module with CoA; i.e l10n_it
        group (str): if supplied select specific group data; default is "base"

    Returns:
        None

resource_edit
~~~~~~~~~~~~~

Server-side web form editing.

Ordinary Odoo test use the primitive create() and write() function to manage
test data. These methods create an update records, but they do not properly
reflect the behaviour of user editing form with GUI interface.

This function simulates the client-side form editing in the server-side.
It works in the follow way:

* It can simulate the form create record
* It can simulate the form update record
* It can simulate the user data input
* It calls the onchange functions automatically
* It may be used to call button in the form

User action simulation:

The parameter <web_changes> is a list of user actions to execute sequentially.
Every element of the list is another list with 2 or 3 values:

* Field name to assign value
* Value to assign
* Optional function to execute (i.e. specific onchange)

You can easily get the field name form GUI with developer mode active.
If field is associate to an onchange function the relative onchange functions
are execute after value assignment. If onchange set another field with another
onchange the relative another onchange are executed until all onchange are
exhausted. This behavior is the same of the form editing.

Warning: because function are always executed at the server side the behavior
may be slightly different from actual form editing. Please take note of
following limitations:

* update form cannot simulate discard button
* some required data in create must be supplied by default parameter
* form inconsistency cannot be detected by this function
* nested function must be managed by test code (i.e. wizard from form)

See test_testenv module for test examples
https://github.com/zeroincombenze/zerobug-test/tree/12.0/test_testenv

def resource_edit(self, resource, default={}, web_changes=[], actions=[], ctx={}):

    Args:
        resource (str or obj): if field is a string simulate create web behavior of
        Odoo model issued in resource;
        if field is an obj simulate write web behavior on the issued record
        default (dict): default value to assign
        web_changes (list): list of tuples (field, value); see <wiz_edit>
        actions (str or list or tuple): action to execute; if not supplied will be
                                execute "save" for existent record or
                                "create" if no record supplied.

    Returns:
        windows action to execute or obj record from [create, save] actions

wizard
~~~~~~

Execute a full wizard.

Engage the specific wizard, simulate user actions and return the wizard result,
usually a windows action.

It is useful to test:

    * view names
    * wizard structure
    * wizard code

Both parameters <module> and <action_name> must be issued in order to
call <wiz_by_action_name>; they are alternative to act_windows.

*** Example of use ***

::

  XML view file:
      <record id="action_example" model="ir.actions.act_window">
          <field name="name">Example</field>
          <field name="res_model">wizard.example</field>
          [...]
      </record>

Python code:

::

    act_windows = self.wizard(module="module_example",
        action_name="action_example", ...)
    if self.is_action(act_windows):
        act_windows = self.wizard(act_windows=act_windows, ...)

User action simulation:

The parameter <web_changes> is a list of user actions to execute sequentially.
Every element of the list is another list with 2 or 3 values:

* Field name to assign value
* Value to assign
* Optional function to execute (i.e. specific onchange)

If field is associate to an onchange function the relative onchange functions
are execute after value assignment. If onchange set another field with another
onchange the relative another onchange are executed until all onchange are
exhausted. This behavior is the same of the form editing.

def wizard(self, module=None, action_name=None, act_windows=None, records=None, default=None, ctx={}, button_name=None, web_changes=[], button_ctx={},):

    Args:
        module (str): module name for wizard to test; if "." use current module name
        action_name (str): action name
        act_windows (dict): Odoo windows action (do not issue module & action_name)
        records (obj): objects required by the download wizard
        default (dict): default value to assign
        ctx (dict): context to pass to wizard during execution
        button_name (str): function name to execute at the end of then wizard
        web_changes (list): list of tuples (field, value); see above
        button_ctx (dict): context to pass to button_name function

    Returns:
        result of the wizard

    Raises:
        ValueError: if invalid parameters issued

validate_record
~~~~~~~~~~~~~~~

Validate records against template values.
During the test will be necessary to check result record values.
This function aim to validate all the important values with one step.
You have to issue 2 params: template with expected values and record to check.
You can declare just some field value in template which are important for you.
Both template and record are lists, record may be a record set too.
This function do following steps:

* matches templates and record, based on template supplied data
* check if all template are matched with 1 record to validate
* execute self.assertEqual() for every field in template
* check for every template record has matched with assert

def validate_records(self, template, records):

    Args:
         template (list of dict): list of dictionaries with expected values
         records (list or set): records to validate values

    Returns:
        list of matched coupled (template, record) + # of assertions

    Raises:
        ValueError: if no enough assertions or one assertion is failed

get_records_from_act_windows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get records from a windows message.

def get_records_from_act_windows(self, act_windows):

    Args:
        act_windows (dict): Odoo windows action returned by a wizard

    Returns:
        records or False

    Raises:
        ValueError: if invalid parameters issued

Useful External Reference
-------------------------

+-------------------+-----------------------+-----------------+----------------------------------+
| id                | name                  | model           | note                             |
+-------------------+-----------------------+-----------------+----------------------------------+
| z0bug.bank        | Bank                  | account.account | Default bank account             |
+-------------------+-----------------------+-----------------+----------------------------------+
| external.INV      | Sale journal          | account.journal | Default sale journal             |
+-------------------+-----------------------+-----------------+----------------------------------+
| external.BILL     | Purchase journal      | account.journal | Default purchase journal         |
+-------------------+-----------------------+-----------------+----------------------------------+
| external.MISC     | Miscellaneous journal | account.journal | Default miscellaneous journal    |
+-------------------+-----------------------+-----------------+----------------------------------+
| external.BNK1     | Bank journal          | account.journal | Default bank journal             |
+-------------------+-----------------------+-----------------+----------------------------------+
| base.main_company | Default company       | res.company     | Default company for test         |
+-------------------+-----------------------+-----------------+----------------------------------+
| base.USD          | USD currency          | res.currency    | Test currency in test: US dollar |
+-------------------+-----------------------+-----------------+----------------------------------+



