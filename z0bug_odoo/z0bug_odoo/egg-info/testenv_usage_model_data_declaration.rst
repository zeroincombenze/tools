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

.. warning::

    When you write a file with a spreadsheet app, pay attention to automatic string
    replacement. For example double quote char <"> may be replaced by <”>.
    These replaced characters may be create some troubles during import data step,
    expecially when used in "python expression".
