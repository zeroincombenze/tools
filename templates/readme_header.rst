.. $if odoo_layer == 'module'
===============
|icon| {{name}}
===============
.. $if name != summary

**{{summary}}**
.. $fi

.. |icon| image:: {{icon}}

.. $elif odoo_layer == 'repository'
==============================
{{repos_name}} Odoo {{branch}} 
==============================

.. $else
==================================
Odoo {{branch}} (formerly OpenERP)
==================================

.. $fi
|Maturity| |Build Status| |Coverage Status| |Codecov Status| |license gpl| |Tech Doc| |Help| |Try Me|

.. contents::