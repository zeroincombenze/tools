+---------------------------------+------------------------------------------+
| |en|                            | |it|                                     |
+---------------------------------+------------------------------------------+
| These instruction are just an   | Istruzioni di esempio valide solo per    |
| example to remember what        | distribuzioni Linux CentOS 7, Ubuntu 14+ |
| you have to do on Linux.        | e Debian 8+                              |
|                                 |                                          |
| Installation is built with:     | L'installazione è costruita con:         |
+---------------------------------+------------------------------------------+
| {{zero_tools:%-74.74s}} |
+---------------------------------+------------------------------------------+
| Suggested deployment is         | Posizione suggerita per l'installazione: |
+---------------------------------+------------------------------------------+
| {{local_path:%-74.74s}} |
+----------------------------------------------------------------------------+

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    export PATH=$HOME/dev:$PATH
    odoo_install_repository {{repos_name}} -b {{branch}} -O {{GIT_ORGID}}
    for pkg in os0 z0lib; do
        pip install $pkg -U
    done
    sudo manage_odoo requirements -b {{branch}} -vsy -o /opt/odoo/{{branch}}

.. $if odoo_layer == 'module'
From UI: go to:
.. $if branch in '11.0' '10.0'

* |menu| Setting > Activate Developer mode 
* |menu| Apps > Update Apps List
* |menu| Setting > Apps |right_do| Select **{{module_name}}** > Install
.. $elif branch in '9.0'

* |menu| admin > About > Activate Developer mode
* |menu| Setting > Modules > Update Modules List
* |menu| Setting > Local Modules |right_do| Select **{{module_name}}** > Install
.. $elif branch in '8.0' '7.0' '6.1'

* |menu| Setting > Modules > Update Modules List
* |menu| Setting > Local Modules |right_do| Select **{{module_name}}** > Install
.. $fi
.. $fi