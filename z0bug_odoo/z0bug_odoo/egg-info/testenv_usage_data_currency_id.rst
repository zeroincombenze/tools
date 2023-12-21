If value is empty, user company is used.
When data is searched by ``resource_search()`` function the "company_id" field
is automatically filled and added to search domain.
This behavior is not applied on
**res.users**, **res.partner**, **product.template** and **product.product** models.
For these models you must fill the "company_id" field.
For these models ``resource_search()`` function searches for record with company_id
null or equal to current user company.