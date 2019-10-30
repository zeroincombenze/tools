.. $if not no_pypi
To install stable version:

::
    pip install {{name}}

|

.. $fi
To install current version:

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    source /opt/odoo/dev/activate_tools
