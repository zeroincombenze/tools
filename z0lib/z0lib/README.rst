
===========
z0lib 1.0.5
===========



|Maturity| |Build Status| |Coverage Status| |license gpl|




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


|

Installation
------------

Installation
------------

Zeroincombenze tools require:

* Linux Centos 7/8 or Debian 9/10 or Ubuntu 18/20
* python 2.7, some tools require python 3.6+
* bash 5.0+

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    pip install z0lib

|

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    source /opt/odoo/devel/activate_tools


Upgrade
-------

Upgrade
-------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    pip install z0lib -U

|

Current stable version
~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    ./install_tools.sh -U
    source /opt/odoo/devel/activate_tools

Current development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    ./install_tools.sh -Ud
    source /opt/odoo/devel/activate_tools


History
-------

1.0.3.1 (2021-10-29)
~~~~~~~~~~~~~~~~~~~~

[REF] CFG_set

1.0.0.3 (2021-04-06)
~~~~~~~~~~~~~~~~~~~~

[REF] run_traced: identation based on stack
[IMP] run_traced: parameter -quiet

1.0.0.2 (2021-04-05)
~~~~~~~~~~~~~~~~~~~~

[REF] parseoptarg with long options
[REF] run_traced: colors management



|
|

Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


Contributors
------------

* Antonio Maria Vigliotti <info@shs-av.com>
|
This module is part of tools project.
Last Update / Ultimo aggiornamento: 2021-08-31
.. |Maturity| image:: https://img.shields.io/badge/maturity-Mature-green.png
:target: https://odoo-community.org/page/development-status
:alt:
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=master
:target: https://travis-ci.com/zeroincombenze/tools
:alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
:target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
:alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
:target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
:alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=master
:target: https://coveralls.io/github/zeroincombenze/tools?branch=1.0
:alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/1.0/graph/badge.svg
:target: https://codecov.io/gh/zeroincombenze/tools/branch/1.0
:alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-1.svg
:target: https://wiki.zeroincombenze.org/en/Odoo/1.0/dev
:alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-1.svg
:target: https://wiki.zeroincombenze.org/it/Odoo/1.0/man
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-1.svg
:target: https://erp1.zeroincombenze.it
:alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/1.0/graph/badge.svg
:target: https://codecov.io/gh/OCA/tools/branch/1.0
.. |Odoo Italia Associazione| image:: https://www.odoo-italia.org/images/Immagini/Odoo%20Italia%20-%20126x56.png
:target: https://odoo-italia.org
:alt: Odoo Italia Associazione
.. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4
:target: https://www.zeroincombenze.it/
:alt: Zeroincombenze
.. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png
:target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png
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
:target: https://t.me/axitec_helpdesk
Last Update / Ultimo aggiornamento: 2021-09-25
.. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
Last Update / Ultimo aggiornamento: 2021-10-06
Last Update / Ultimo aggiornamento: 2021-10-07
Last Update / Ultimo aggiornamento: 2021-10-12
Last Update / Ultimo aggiornamento: 2021-10-13
Last Update / Ultimo aggiornamento: 2021-10-20
Last Update / Ultimo aggiornamento: 2021-10-25
Last Update / Ultimo aggiornamento: 2021-10-30
:target: https://t.me/Assitenza_clienti_powERP
Last Update / Ultimo aggiornamento: 2021-11-01
Last Update / Ultimo aggiornamento: 2021-11-11
Last Update / Ultimo aggiornamento: 2021-11-13
Last Update / Ultimo aggiornamento: 2021-12-04
Last Update / Ultimo aggiornamento: 2021-12-05
Last Update / Ultimo aggiornamento: 2021-12-11
Last Update / Ultimo aggiornamento: 2021-12-16
Last Update / Ultimo aggiornamento: 2021-12-17
Last Update / Ultimo aggiornamento: 2021-12-19
:target: https://odoo-community.org/page/development-status
:alt:
:target: https://travis-ci.com/zeroincombenze/tools
:alt: github.com
:target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
:alt: License: AGPL-3
:target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
:alt: License: OPL
:target: https://coveralls.io/github/zeroincombenze/tools?branch=1.0
:alt: Coverage
:target: https://codecov.io/gh/zeroincombenze/tools/branch/1.0
:alt: Codecov
:target: https://wiki.zeroincombenze.org/en/Odoo/1.0/dev
:alt: Technical Documentation
:target: https://wiki.zeroincombenze.org/it/Odoo/1.0/man
:target: https://erp1.zeroincombenze.it
:alt: Try Me
:target: https://codecov.io/gh/OCA/tools/branch/1.0
:target: https://odoo-italia.org
:alt: Odoo Italia Associazione
:target: https://www.zeroincombenze.it/
:alt: Zeroincombenze
:target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
:target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md
:target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md
:target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md
:target: https://t.me/Assitenza_clienti_powERP


|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2021-12-20

.. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=master
    :target: https://travis-ci.com/zeroincombenze/tools
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=master
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=1.0
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/1.0/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/1.0
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-1.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/1.0/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-1.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/1.0/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-1.svg
    :target: https://erp1.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/1.0/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/1.0
    :alt: Codecov
.. |Odoo Italia Associazione| image:: https://www.odoo-italia.org/images/Immagini/Odoo%20Italia%20-%20126x56.png
   :target: https://odoo-italia.org
   :alt: Odoo Italia Associazione
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


