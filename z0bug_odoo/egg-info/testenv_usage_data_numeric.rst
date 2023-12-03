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
