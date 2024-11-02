============
z0lib 2.0.13
============



|Maturity| |license gpl|



Overview
========

z0lib is a simple bash and python library.

It was created to give support to bash and python software.
The package has both bash version and both python version of functions.
Since 2022, bash development was abandoned and only python code is still upgraded.

.. important::

    However, most functions are still available for bash scripts.

The available libraries are:

* z0librc: bash version library
* z0librun.py: python version library



Features
--------

+--------------+------+--------+-----------------------------------------------------------------+
| Description  | bash | python | Note(s)                                                         |
+--------------+------+--------+-----------------------------------------------------------------+
| run_traced   | ✅   | ✅     | Run os command with trace                                       |
+--------------+------+--------+-----------------------------------------------------------------+
| xuname       | ✅   | ❌     | OS indentity (python has native function)                       |
+--------------+------+--------+-----------------------------------------------------------------+
| parseoptargs | ✅   | ❌     | Command line parser (python has native function)                |
+--------------+------+--------+-----------------------------------------------------------------+
| link_cfg     | ✅   | ❌     | Get values from configuration file (python has native function) |
+--------------+------+--------+-----------------------------------------------------------------+



Getting started
===============


Prerequisites
-------------

Zeroincombenze(R) tools requires:

* Linux Centos 7/8 or Debian 9/10/11 or Ubuntu 16/18/20/22/24
* python 2.7+, some tools require python 3.7+, best python 3.9+
* bash 5.0+



Installation
------------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install z0lib

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    [[ ! -d ./tools ]] && git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



Upgrade
-------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install --upgrade z0lib

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



ChangeLog History
-----------------

2.0.13 (2024-10-31)
~~~~~~~~~~~~~~~~~~~

* [FIX] os_system minor fixes

2.0.12 (2024-08-22)
~~~~~~~~~~~~~~~~~~~

* [FIX] os_system with verbose

2.0.11 (2024-07-13)
~~~~~~~~~~~~~~~~~~~

* [IMP] New function os_system
* [IMP] New function print_flush

2.0.10 (2024-07-07)
~~~~~~~~~~~~~~~~~~~

* [IMP] run_traced improvements
* [IMP] Python 3.6 deprecated

2.0.9 (2024-02-01)
~~~~~~~~~~~~~~~~~~

* [IMP] Internal matadata

2.0.8 (2023-10-16)
~~~~~~~~~~~~~~~~~~

* [FIX] parseopt

2.0.7 (2023-07-20)
~~~~~~~~~~~~~~~~~~

* [FIX] run_traced return system exit code
* [IMP] run_traced: new rtime parameter to show rtime output
* [IMP] New main

2.0.5 (2023-05-14)
~~~~~~~~~~~~~~~~~~

* [FIX] Sometime configuration init fails
* [IMP] Configuration name LOCAL_PKGS read real packages
* [IMP] is_pypi function more precise

2.0.4 (2023-04-10)
~~~~~~~~~~~~~~~~~~

* [FIX] run_traced: cd does not work w/o alias
* [IMP] coveralls and codecov are not more dependencies

2.0.3 (2022-12-22)
~~~~~~~~~~~~~~~~~~

* [FIX] run_traced: --switch sometime crashes
* [FIX] run_traced: alias function

2.0.2 (2022-12-07)
~~~~~~~~~~~~~~~~~~

* [FIX] best recognition of python version
* [FIX] run_traced: fail with python 2

2.0.1 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [IMP] Stable version

2.0.0.4.1 (2022-10-20)
~~~~~~~~~~~~~~~~~~~~~~

* [FIX] run_traced: wrong execution for "cd <path>; ..."
* [IMP] CFG_init 'ALL': set ODOO_ROOT

2.0.0.4 (2022-10-05)
~~~~~~~~~~~~~~~~~~~~

* [IMP] python2 tests

2.0.0.3 (2022-09-30)
~~~~~~~~~~~~~~~~~~~~

* [FIX] run_traced return code

2.0.0.2 (2022-09-14)
~~~~~~~~~~~~~~~~~~~~

* [IMP] run_traced for python apps

2.0.0.1 (2022-09-06)
~~~~~~~~~~~~~~~~~~~~

* [IMP] set_pybin accept filename
* [IMP] check_pythonpath removed

2.0.0 (2022-08-10)
~~~~~~~~~~~~~~~~~~

* [REF] Partial refactoring for shell scripts



Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


Authors
-------

* `SHS-AV s.r.l. <https://www.zeroincombenze.it>`__



Contributors
------------

* `Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>`__


|
|

.. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.13/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.13/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg
    :target: https://erp2.zeroincombenze.it
    :alt: Try Me
.. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4
   :target: https://www.zeroincombenze.it/
   :alt: Zeroincombenze
.. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png
   :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png
   :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/check.png
.. |no_check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/no_check.png
.. |menu| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/menu.png
.. |right_do| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/right_do.png
.. |exclamation| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/exclamation.png
.. |warning| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/warning.png
.. |same| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/same.png
.. |late| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/late.png
.. |halt| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/halt.png
.. |info| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/info.png
.. |xml_schema| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/iso/icons/xml-schema.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md
.. |DesktopTelematico| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/DesktopTelematico.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md
.. |FatturaPA| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/fatturapa.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md
.. |chat_with_us| image:: https://www.shs-av.com/wp-content/chat_with_us.gif
   :target: https://t.me/Assitenza_clienti_powERP
