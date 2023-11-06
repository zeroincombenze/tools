.. $if not no_pypi
Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install {{name}}

.. $fi
Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    [[ ! -d ./tools ]] && git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools
.. $if write_index

Source code
~~~~~~~~~~~

You can find source code on `github <https://github.com/zeroincombenze/tools.git>`__
.. $fi
