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
.. $elif git_orgid == 'oia'
====================================================
|Odoo Italia Associazione| {{repos_name}} {{branch}}
====================================================
.. $fi

.. $else
==================================
Odoo {{branch}} (formerly OpenERP)
==================================

.. $fi
|Maturity| |Build Status| |Coverage Status| |Codecov Status| |license gpl| |Tech Doc| |Help| |Try Me|

.. contents::