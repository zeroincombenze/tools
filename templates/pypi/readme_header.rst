.. $if odoo_layer == 'module'
===========================
{{name}} {{module_version}}
===========================

.. $if name != summary

**{{summary}}**
.. $fi


|Maturity| |Build Status| |Coverage Status| |license gpl|

.. $elif odoo_layer == 'repository'
==========================================
|Zeroincombenze| {{repos_name}} {{branch}}
==========================================

|Coverage Status| |license gpl|

.. $fi
.. $if template.find('mainpage') < 0:
.. contents::
.. $fi
