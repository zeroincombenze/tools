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
