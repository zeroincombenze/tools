
+---------------------------------+------------------------------------------+
| |en|                            | |it|                                     |
+---------------------------------+------------------------------------------+
| These instructions are just an  | Istruzioni di esempio valide solo per    |
| example; use on Linux CentOS 7+ | distribuzioni Linux CentOS 7+,           |
| Ubuntu 14+ and Debian 8+        | Ubuntu 14+ e Debian 8+                   |
|                                 |                                          |
| Installation is built with:     | L'installazione è costruita con:         |
+---------------------------------+------------------------------------------+
| {{zero_tools:%-74.74s}} |
+---------------------------------+------------------------------------------+
| Suggested deployment is:        | Posizione suggerita per l'installazione: |
+---------------------------------+------------------------------------------+
| $HOME/{{branch:%-68.68s}} |
+----------------------------------------------------------------------------+

::

.. $if repos_name == 'OCB'
    # Odoo module installation
.. $else
    # Odoo repository installation; OCB repository must be installed
.. $fi
    deploy_odoo clone -r {{repos_name}} -b {{branch}} -G {{GIT_ORGID}} -p $HOME/{{branch}}
.. $if repos_name == 'OCB'
    # Create virtual environment
    vem create $HOME/{{branch}}/venv_odoo -a "*" -DI --odoo-path=$HOME/{{branch}}
.. $else
    # Upgrade virtual environment
    vem amend $HOME/{{branch}}/venv_odoo
.. $fi
