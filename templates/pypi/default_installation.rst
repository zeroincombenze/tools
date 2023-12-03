.. $if not no_pypi
.. $if odoo_layer == 'module'
Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install {{name}}

.. $fi
.. $fi
Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    [[ ! -d ./tools ]] && git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools
