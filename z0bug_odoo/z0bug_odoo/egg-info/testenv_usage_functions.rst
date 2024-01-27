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

| Args:
|     resource (str): Odoo model name, i.e. "res.partner"
|     data (dict): record data
|     name (str): label of dataset; default is resource name
|     group (str): used to manager group data; default is "base"
|     merge (str): values are ("local"|"zerobug")
|
| Raises:
|     TypeError: if invalid parameters issued

declare_all_data
~~~~~~~~~~~~~~~~

Declare all data to load on setup_env()

| Args:
|     message (dict): data message
|         TEST_SETUP_LIST (list): resource list to load
|         TEST_* (dict): resource data; * is the uppercase resource name where
|                        dot are replaced by "_"; (see declare_resource_data)
|     group (str): used to manager group data; default is "base"
|     merge (str): values are ("local"|"zerobug")
|     data_dir (str): data directory, default is "tests/data"
|
| Raises:
|     TypeError: if invalid parameters issued

get_resource_data
~~~~~~~~~~~~~~~~~

Get declared resource data; may be used to test compare

| Args:
|     resource (str): Odoo model name or name assigned, i.e. "res.partner"
|     xref (str): external reference
|     group (str): if supplied select specific group data; default is "base"
|     try_again (bool): engage conveyed value
|
| Returns:
|     dictionary with data or empty dictionary

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

| Args:
|     company (obj): company to update; if not supplied a new company is created
|     xref (str): external reference or alias for main company
|     partner_xref (str): external reference or alias for main company partner
|     recv_xref (str): external reference or alias for receivable account
|     pay_xref (str): external reference or alias for payable account
|     bnk1_xref (str): external reference or alias for 1st liquidity bank
|     values (dict): company data to update immediately
|     group (str): if supplied select specific group data; default is "base"
|
| Returns:
|     default company for user

setup_env
~~~~~~~~~

Create all record from declared data.

This function starts the test workflow creating the test environment.
Test data must be declared before engage this function by file .csv or
file .xlsx or by source declaration TEST_<MODEL>.

setup_env may be called more times with different group value.
If it is called with the same group, it recreates the test environment with
declared values; however this feature might do not work for some reason: i.e.
if test creates a paid invoice, the setup_env() cannot unlink invoice.
If you want to recreate the same test environment, assure the conditions for
unlink of all created and tested records.

If you create more test environment with different group you can grow the data
during test execution with complex scenario.
In this way you can create functional tests not only regression tests.

| Args:
|     lang (str): install & load specific language
|     locale (str): install locale module with CoA; i.e l10n_it
|     group (str): if supplied select specific group data; default is "base"
|     source (str): values are ("local"|"zerobug")
|     setup_list (list): list of Odoo modelS; if missed use TEST_SETUP_LIST
|     data_dir (str): data directory, default is "tests/data"
|
| Returns:
|     None

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

If field is associated to an onchange function the relative onchange functions
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

    Returns:
        windows action to execute or obj record

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

If field is associated to an onchange function the relative onchange functions
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
