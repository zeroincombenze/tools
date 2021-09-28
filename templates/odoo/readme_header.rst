.. $if odoo_layer == 'module'
==================================
|icon| {{name}} {{module_version}}
==================================

.. $if name != summary

**{{summary}}**
.. $fi

.. |icon| image:: {{icon}}

.. $if git_orgid == 'powerp'
|Maturity| |Build Status| |license opl|
.. $else
|Maturity| |Build Status| |Codecov Status| |license gpl| |Try Me|
.. $fi

.. $elif odoo_layer == 'repository'
.. $if git_orgid == 'zero'
==========================================
|Zeroincombenze| {{repos_name}} {{branch}}
==========================================
.. $fi
.. $if git_orgid == 'powerp'
|Build Status| |license opl|
.. $else
|Build Status| |Codecov Status| |license gpl| |Try Me|
.. $fi

.. $else
==================================
Odoo {{branch}} (formerly OpenERP)
==================================

.. $if git_orgid == 'powerp'
|Build Status| |license opl|
.. $else
|Build Status| |Codecov Status| |license gpl| |Try Me|
.. $fi
.. $fi

.. contents::
