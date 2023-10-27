
===========
z0lib 2.0.7
===========



|Maturity| |license gpl|




Overview
========

Simple bash library

+---------------+-----------------------------------------------------------+
| xuname        | Detect and print more OS informations than uname command  |
+---------------+-----------------------------------------------------------+
| parse_optargs | Parse command line arguments in a professional way        |
+---------------+-----------------------------------------------------------+
| print_help    | Print help for parse command line arguments               |
+---------------+-----------------------------------------------------------+

You can find more info here:
http://wiki.zeroincombenze.org/en/Linux/dev
http://docs.zeroincombenze.org/z0lib/


|
|

Getting started
===============



Zeroincombenze tools require:

* Linux Centos 7/8 or Debian 9/10 or Ubuntu 18/20/22
* python 2.7+, some tools require python 3.6+
* bash 5.0+

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install z0lib

|

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    source $HOME/devel/activate_tools



Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install z0lib -U

|

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    ./install_tools.sh -U
    source $HOME/devel/activate_tools


ChangeLog History
-----------------

2.0.7.0.7
~~~~~~~~~

* [FIX] parseopt

2.0.7 (2023-07-20)
~~~~~~~~~~~~~~~~~~

* [FIX] run_traced return system exit code
* [IMP] run_traced: new rtime parameter to show rtime output
* [IMP] New main

2.0.7.0.7
~~~~~~~~~

* [FIX] Sometime configuration init fails
* [IMP] Configuration name LOCAL_PKGS read real packages
* [IMP] is_pypi function more precise

2.0.7.0.7
~~~~~~~~~

* [FIX] run_traced: cd does not work w/o alias
* [IMP] coveralls and codecov are not more dependencies

2.0.7.0.7
~~~~~~~~~

* [FIX] run_traced: --switch sometime crashes
* [FIX] run_traced: alias function

2.0.7.0.7
~~~~~~~~~

* [FIX] best recognition of python version
* [FIX] run_traced: fail with python 2


|
|

Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


|

Authors
-------

* `Antonio Maria Vigliotti <False>`__
* `SHS-AV s.r.l. <https://www.zeroincombenze.it>`__

Contributors
------------

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>
* Antonio Maria Vigliotti <info@shs-av.com>
* | <False>
* This module is part of tools project. <False>
* Last Update / Ultimo aggiornamento: 2023-08-12 <False>
* .. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png <False>
* :target: https://odoo-community.org/page/development-status <False>
* :alt: <False>
* .. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg <False>
* :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html <False>
* :alt: License: AGPL-3 <False>
* .. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg <False>
* :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html <False>
* :alt: License: OPL <False>
* .. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg <False>
* :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.7/dev <False>
* :alt: Technical Documentation <False>
* .. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg <False>
* :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.7/man <False>
* :alt: Technical Documentation <False>
* .. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg <False>
* :target: https://erp2.zeroincombenze.it <False>
* :alt: Try Me <False>
* .. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4 <False>
* :target: https://www.zeroincombenze.it/ <False>
* :alt: Zeroincombenze <False>
* .. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png <False>
* :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/ <False>
* .. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png <False>
* :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/ <False>
* .. |check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/check.png <False>
* .. |no_check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/no_check.png <False>
* .. |menu| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/menu.png <False>
* .. |right_do| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/right_do.png <False>
* .. |exclamation| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/exclamation.png <False>
* .. |warning| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/warning.png <False>
* .. |same| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/same.png <False>
* .. |late| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/late.png <False>
* .. |halt| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/halt.png <False>
* .. |info| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/info.png <False>
* .. |xml_schema| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/iso/icons/xml-schema.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md <False>
* .. |DesktopTelematico| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/DesktopTelematico.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md <False>
* .. |FatturaPA| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/fatturapa.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md <False>
* .. |chat_with_us| image:: https://www.shs-av.com/wp-content/chat_with_us.gif <False>
* :target: https://t.me/Assitenza_clienti_powERP <False>
* | <False>
* This module is part of tools project. <False>
* Last Update / Ultimo aggiornamento: 2023-10-16 <False>
* .. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png <False>
* :target: https://odoo-community.org/page/development-status <False>
* :alt: <False>
* .. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg <False>
* :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html <False>
* :alt: License: AGPL-3 <False>
* .. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg <False>
* :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html <False>
* :alt: License: OPL <False>
* .. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg <False>
* :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.7/dev <False>
* :alt: Technical Documentation <False>
* .. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg <False>
* :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.7/man <False>
* :alt: Technical Documentation <False>
* .. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg <False>
* :target: https://erp2.zeroincombenze.it <False>
* :alt: Try Me <False>
* .. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4 <False>
* :target: https://www.zeroincombenze.it/ <False>
* :alt: Zeroincombenze <False>
* .. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png <False>
* :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/ <False>
* .. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png <False>
* :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/ <False>
* .. |check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/check.png <False>
* .. |no_check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/no_check.png <False>
* .. |menu| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/menu.png <False>
* .. |right_do| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/right_do.png <False>
* .. |exclamation| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/exclamation.png <False>
* .. |warning| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/warning.png <False>
* .. |same| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/same.png <False>
* .. |late| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/late.png <False>
* .. |halt| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/halt.png <False>
* .. |info| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/info.png <False>
* .. |xml_schema| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/iso/icons/xml-schema.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md <False>
* .. |DesktopTelematico| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/DesktopTelematico.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md <False>
* .. |FatturaPA| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/fatturapa.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md <False>
* .. |chat_with_us| image:: https://www.shs-av.com/wp-content/chat_with_us.gif <False>
* :target: https://t.me/Assitenza_clienti_powERP <False>
* | <False>
* This module is part of tools project. <False>
* Last Update / Ultimo aggiornamento: 2023-10-16 <False>
* .. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png <False>
* :target: https://odoo-community.org/page/development-status <False>
* :alt: <False>
* .. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg <False>
* :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html <False>
* :alt: License: AGPL-3 <False>
* .. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg <False>
* :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html <False>
* :alt: License: OPL <False>
* .. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg <False>
* :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.7/dev <False>
* :alt: Technical Documentation <False>
* .. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg <False>
* :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.7/man <False>
* :alt: Technical Documentation <False>
* .. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg <False>
* :target: https://erp2.zeroincombenze.it <False>
* :alt: Try Me <False>
* .. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4 <False>
* :target: https://www.zeroincombenze.it/ <False>
* :alt: Zeroincombenze <False>
* .. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png <False>
* :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/ <False>
* .. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png <False>
* :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/ <False>
* .. |check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/check.png <False>
* .. |no_check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/no_check.png <False>
* .. |menu| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/menu.png <False>
* .. |right_do| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/right_do.png <False>
* .. |exclamation| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/exclamation.png <False>
* .. |warning| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/warning.png <False>
* .. |same| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/same.png <False>
* .. |late| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/late.png <False>
* .. |halt| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/halt.png <False>
* .. |info| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/info.png <False>
* .. |xml_schema| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/iso/icons/xml-schema.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md <False>
* .. |DesktopTelematico| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/DesktopTelematico.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md <False>
* .. |FatturaPA| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/fatturapa.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md <False>
* .. |chat_with_us| image:: https://www.shs-av.com/wp-content/chat_with_us.gif <False>
* :target: https://t.me/Assitenza_clienti_powERP <False>

|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2023-10-25

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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.7/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.7/man
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


