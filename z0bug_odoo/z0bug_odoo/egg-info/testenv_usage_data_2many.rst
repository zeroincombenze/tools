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

