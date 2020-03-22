
+---------------------------------+------------------------------------------+
| |en|                            | |it|                                     |
+---------------------------------+------------------------------------------+
| When you want upgrade and you   | Per aggiornare, se avete installato con  |
| installed using above           | le istruzioni di cui sopra:              |
| statements:                     |                                          |
+---------------------------------+------------------------------------------+

::

    odoo_install_repository {{repos_name}} -b {{branch}} -O {{GIT_ORGID}} -U
    venv_mgr amend /opt/odoo/VENV-{{branch}} -O {{branch}} -DI
    # Adjust following statements as per your system
    sudo systemctl restart odoo

.. $if odoo_layer == 'module'
From UI: go to:
.. $if branch in '11.0' '10.0'

* |menu| Setting > Activate Developer mode
* |menu| Apps > Update Apps List
* |menu| Setting > Apps |right_do| Select **{{module_name}}** > Update
.. $elif branch in '9.0'

* |menu| admin > About > Activate Developer mode
* |menu| Setting > Modules > Update Modules List
* |menu| Setting > Local Modules |right_do| Select **{{module_name}}** > Update
.. $elif branch in '8.0' '7.0' '6.1'

* |menu| Setting > Modules > Update Modules List
* |menu| Setting > Local Modules |right_do| Select **{{module_name}}** > Update
.. $fi
.. $fi