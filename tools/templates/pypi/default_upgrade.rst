.. $if not no_pypi
.. $if odoo_layer == 'module'
Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install --upgrade {{name}}

.. $fi
.. $fi
Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools
.. $if write_index

Source code
~~~~~~~~~~~

You can find source code on `github <https://github.com/zeroincombenze/tools.git>`__
.. $fi
