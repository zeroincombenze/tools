+----------------------------------+-------------------------------------------+
| |en|                             | |it|                                      |
+----------------------------------+-------------------------------------------+
| If your Odoo instance crashes    | Se Odoo non si avvia dopo l'installazione |
| after installed this module,     | di questo modulo, applica le seguenti     |
| you can do following instruction | istruzioni:                               |
| to recover installation status:  |                                           |
+----------------------------------+-------------------------------------------+

.. $if odoo_layer == 'module'
``run_odoo_debug -b {{branch}} -um {{module_name}} -s -d MYDB``
.. $else
``run_odoo_debug -b {{branch}} -um all -s -d MYDB``
.. $fi
