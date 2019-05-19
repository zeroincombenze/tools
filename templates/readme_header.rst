.. $if odoo_layer == 'module'
==================================
|icon| {{name}} {{module_version}}
==================================

.. $if name != summary

**{{summary}}**
.. $fi

.. |icon| image:: {{icon}}

.. $elif odoo_layer == 'repository'
.. $if git_orgid == 'zero'
==========================================
|Zeroincombenze| {{repos_name}} {{branch}}
==========================================
.. $fi
|Maturity| |Build Status| |Coverage Status| |Codecov Status| |license gpl| |Tech Doc| |Help| |Try Me|

.. $else
==================================
Odoo {{branch}} (formerly OpenERP)
==================================

|Build Status| |Coverage Status| |Codecov Status| |license gpl| |Tech Doc| |Help| |Try Me|
.. $fi

.. contents::