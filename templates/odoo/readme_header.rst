.. $if odoo_layer == 'module'
.. $if name == name_i18n
==================================
|icon| {{name}} {{module_version}}
==================================
.. $else
================================================
|icon| {{name}}/{{name_i18n}} {{module_version}}
================================================
.. $fi
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
.. $else
==================================
Odoo {{branch}} (formerly OpenERP)
==================================
.. $fi

.. contents::
