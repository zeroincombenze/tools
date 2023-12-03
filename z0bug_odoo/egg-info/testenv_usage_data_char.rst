Char and Text values are python string; please use unicode whenever is possible
even when you test Odoo 10.0 or less.

You can evalute the field value engaging a simple python expression inside tags like in
following syntax:

    "<?odoo EXPRESSION ?>"

The expression may be a simple python expression with following functions:

.. $include testenv_usage_expr.csv

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

