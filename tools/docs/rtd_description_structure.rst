.. toctree::
   :maxdepth: 2

Odoo structure
~~~~~~~~~~~~~~

All the tools serving Odoo are based on follow file system structure (flat layout):

::

    etc
     ┗━ odoo
          ┣━ odoo.conf                   (1)(3)
          ┣━ odoo-server.conf            (2)(3)
          ┣━ odoo{majver}.conf           (1)(4)
          ┣━ odoo{majver}-server.conf    (2)(4)
          ┗━ odoo{majver}-{org}.conf     (4)

    {vid}
      ┣━ addons                          (3)
      ┣━ ...                             (3)
      ┣━ odoo                            (1)(3)
      ┃    ┣━ ...                        (3)
      ┃    ┗━ addons                     (3)
      ┣━ openerp                         (2)(3)
      ┃    ┣━ ...                        (3)
      ┃    ┗━ addons                     (3)
      ┣━ server                          (5)
      ┃    ┗━ openerp
      ┃        ┣━ ...
      ┃        ┗━ addons
      ┣━ {repository}
      ┃    ┣━ {module}
      ┃    ┃    ┣━ __init__.py
      ┃    ┃    ┣━ __manifest__.py
      ┃    ┃    ┗━ ...
      ┃    ┗━ {module} ...
      ┃         ┗━ ...
      ┗━ {repository} ...
           ┗━ ...

    {venv}
      ┣━ ....
      ┗━ odoo                             (link)

    Notes:
    (1) Odoo version >= 10.0
    (2) Odoo version < 10.0
    (3) Odoo standard files / directory
    (4) Multi-version environment
    (5) Some old 6.1 and 7.0 installations
    {majver} Odoo major version, i.e. 12 for 12.0
    {org} Organization, i.e. oca powerp zero
    {vid} Odoo root (see about Odoo vid)
    {repository} Odoo/OCA or any repository
    {venv} Virtual directory


This is the hierarchical layout):

::

    {vid}
      ┣━ odoo
      ┃   ┣━ addons                      (3)
      ┃   ┣━ ...                         (3)
      ┃   ┣━ odoo                        (1)(3)
      ┃   ┃    ┣━ ...                    (3)
      ┃   ┃    ┗━ addons                 (3)
      ┃   ┗━ openerp                     (2)(3)
      ┃        ┣━ ...                    (3)
      ┃        ┗━  addons                (3)
      ┣━ extra
      ┃    ┣━ {repository}
      ┃    ┃    ┣━ {module}
      ┃    ┃    ┃    ┣━ __init__.py
      ┃    ┃    ┃    ┣━ __manifest__.py
      ┃    ┃    ┃    ┗━ ...
      ┃    ┃    ┗━ {module} ...
      ┃    ┃         ┗━ ...
      ┃    ┗━ {repository} ...
      ┃              ┗━ ...
      ┣━ private-addons
      ┃    ┣━ {customized-addons}
      ┃    ┃    ┣━ __init__.py
      ┃    ┃    ┣━ __manifest__.py
      ┃    ┃    ┗━ ...
      ┃    ┗━ {customized-addons} ...
      ┃         ┗━ ...
      ┣━ etc
      ┃    ┗━ *.conf                     (link)
      ┣━ powerp
      ┃    ┣━ deploy
      ┃    ┣━ generic
      ┃    ┃    ┣━ {profile-modules}
      ┃    ┃    ┃     ┗━ ...
      ┃    ┃    ┗━ {profile-modules} ...
      ┃    ┃          ┗━ ...
      ┃    ┗━ accounting
      ┃         ┣━ {powerp-modules}
      ┃         ┃     ┗━ ...
      ┃         ┗━ {powerp-modules} ...
      ┃               ┗━ ...
      ┗━ venv_odoo                       (4)

    Notes:
    (1) Odoo version >= 10.0
    (2) Odoo version < 10.0
    (3) Odoo standard files / directory
    (4) Virtual directory
    {vid} Odoo root (see about Odoo vid)
    {repository} Odoo/OCA and other repositories
    {customized-addons} Client specific custom modules
    {powerp-modules} Italian Accounting modules


|


Last Update / Ultimo aggiornamento: 2022-10-13

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
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=2.0
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/2.0/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/2.0
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg
    :target: https://erp2.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/2.0/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/2.0
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


