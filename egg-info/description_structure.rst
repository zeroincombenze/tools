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
