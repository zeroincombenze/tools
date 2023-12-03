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
