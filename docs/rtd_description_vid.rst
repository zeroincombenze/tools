.. toctree::
   :maxdepth: 2

+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| Parameter name             | standard value             | anonymous distro     | zeroincombenze d | oca distro      | axitec distro   | Note                                     |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| ROOT (Odoo root)           |                            | ~/%V                 | ~/zero%M         | ~/oca%M         | ~/odoo_%M       | i.e. ~/oca14                             |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| CONFN (configuration file) | odoo.conf odoo-server.conf | odoo%M-server.conf   | odoo%M-zero.conf | odoo%M-oca.conf | odoo%M-axi.conf | Directory /etc/odoo (see Odoo structure) |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| USER (db user)             | odoo                       | odoo%M               | odoo%M           | odoo%M          | odoo%M          | i.e odoo12                               |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| FLOG (log file)            | odoo.log odoo-server.log   | odoo%M-server.log    | odoo%M-zero.log  | odoo%M-oca.log  | odoo%M-axi.log  | Directory /var/log/odoo                  |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| FPID (pid file)            | odoo.pid odoo-server.pid   | odoo%M-server.pid    | odoo%M-zero.pid  | odoo%M-oca.pid  | odoo%M-axi.pid  | Directory /var/run/odoo                  |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| RPCPORT (xmlrpc port)      | 8069                       | 8160 + %M            | 8460 + %M        | 8260 + %M       | 8360 + %M       |                                          |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| LPPORT (longpolling)       | 8072                       | 8130 + %M            | 8430 + %M        | 8230 + %M       | 8330 + %M       |                                          |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| SVCNAME (service name)     | odoo odoo-server           | odoo%M odoo%M-server | odoo%M-zero      | odoo%M-oca      | odoo%M-axi      |                                          |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+


|


Last Update / Ultimo aggiornamento: 2022-05-17

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
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


