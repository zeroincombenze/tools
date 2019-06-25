.. $if odoo_layer == 'module'
==================================
|icon| {{name}} {{module_version}}
==================================

.. $if name != summary

**{{summary}}**
.. $fi

.. |icon| image:: {{icon}}

|Maturity| |Build Status| |Codecov Status| |license gpl| |Try Me|

.. $elif odoo_layer == 'repository'
.. $if git_orgid == 'zero'
==========================================
|Zeroincombenze| {{repos_name}} {{branch}}
==========================================
.. $fi
|Build Status| |Codecov Status| |license gpl| |Try Me|

.. $else
==================================
Odoo {{branch}} (formerly OpenERP)
==================================

|Build Status| |Codecov Status| |license gpl| |Try Me|
.. $fi

.. contents::