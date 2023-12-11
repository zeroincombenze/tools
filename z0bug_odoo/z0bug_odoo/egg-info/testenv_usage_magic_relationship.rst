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
#. Record ID **must** begin with header ID, followed by "_" and line ID
#. Reference data do not require ``self.env.ref()``: they are automatically referenced

It is also easy write the csv or xlsx file. This is the example with above data

File **sale_order.csv**

::

    id,partner_id,origin
    example.order_1,base.res_partner_1,example

File **sale_order_line.csv**

::

    id,product_id,product_qty,price_unit
    example.order_1_1,product.product_product_1,1,1.23
    example.order_1_2,product.product_product_2,2,2.34

In your test file you must declare the following statement:

::

    TEST_SETUP_LIST = ["sale.order", "sale.order.line"]

.. warning::

    You must declare header and lines data before create header record

.. note::

    External reference coding is free: however is hinted to use the The 2
    keys reference explained in "External reference" chapter.

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

