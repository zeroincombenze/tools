.. $if odoo_layer == 'pypi'
===========================
{{name}} {{module_version}}
===========================

.. $if name != summary

**{{summary}}**
.. $fi

.. $elif odoo_layer == 'pypirepo'
==========================================
|Zeroincombenze| {{repos_name}} {{branch}}
==========================================
.. $fi
|Maturity| |Build Status| |Coverage Status| |Codecov Status| |license gpl|

.. contents::