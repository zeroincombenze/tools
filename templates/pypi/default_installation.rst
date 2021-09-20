Installation
------------

Zeroincombenze tools require:

* Linux Centos 7/8 or Debian 9/10 or Ubuntu 18/20
* python 2.7, some tools require python 3.6+
* bash 5.0+

.. $if not no_pypi
Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    pip install {{name}}

|

.. $fi
Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    source /opt/odoo/devel/activate_tools
