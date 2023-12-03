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
