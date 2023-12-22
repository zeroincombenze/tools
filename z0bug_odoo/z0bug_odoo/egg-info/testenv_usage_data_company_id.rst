If value is empty, user company is used.
This behavior is not applied on
**res.users**, **res.partner**, **product.template** and **product.product** models.
For these models you must fill the **company_id** field.

When data is searched by ``resource_search()`` function on every model with company_id,
the **company_id** field is automatically added to search domain, using 'or' between
company_id null and company_id equal to supplied value or current user company.
