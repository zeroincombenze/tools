
+---------------------------------+------------------------------------------+
| |en|                            | |it|                                     |
+---------------------------------+------------------------------------------+
| These instructions are just an  | Istruzioni di esempio valide solo per    |
| example; use on Linux CentOS 7+ | distribuzioni Linux CentOS 7+,           |
| Ubuntu 14+ and Debian 8+        | Ubuntu 14+ e Debian 8+                   |
|                                 |                                          |
| Installation is built with:     | L'installazione è costruita con:         |
+---------------------------------+------------------------------------------+
| {{zero_tools:%-74.74s}} |
+---------------------------------+------------------------------------------+
| Suggested deployment is:        | Posizione suggerita per l'installazione: |
+---------------------------------+------------------------------------------+
| $HOME/{{branch:%-68.68s}} |
+----------------------------------------------------------------------------+

::

    cd $HOME
    # *** Tools installation & activation ***
    # Case 1: you have not installed zeroincombenze tools
    git clone https://github.com/zeroincombenze/tools.git
    cd $HOME/tools
    ./install_tools.sh -pT
    source $HOME/devel/activate_tools
    # Case 2: you have already installed zeroincombenze tools
    cd $HOME/tools
    ./install_tools.sh -UT
    source $HOME/devel/activate_tools
    # *** End of tools installation or upgrade ***
.. $if repos_name == 'OCB'
    # Odoo module installation
.. $else
    # Odoo repository installation; OCB repository must be installed
.. $fi
    deploy_odoo clone -r {{repos_name}} -b {{branch}} -G {{GIT_ORGID}} -p $HOME/{{branch}}
.. $if repos_name == 'OCB'
    # Create virtual environment
    vem create $HOME/{{branch}}/venv_odoo -a "*" -DI --odoo-path=$HOME/{{branch}}
.. $else
    # Upgrade virtual environment
    vem amend $HOME/{{branch}}/venv_odoo
.. $fi

.. $if odoo_layer == 'module'
From UI: go to:
.. $if branch in '16.0' '15.0' '14.0' '13.0' '12.0' '11.0' '10.0'

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
