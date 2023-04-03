
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
    # Odoo repository upgrade
    deploy_odoo update -r {{repos_name}} -b {{branch}} -G {{GIT_ORGID}} -p $HOME/{{branch}}
    vem amend $HOME/{{branch}}/venv_odoo
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
