.. toctree::
   :maxdepth: 2

Usage
=====


Travis emulator usage
---------------------

::

    Usage: travis [-h][-A regex][-BC][-D number][-E][-e iso][-Ffk][-j pyver][-L number][-l dir][-mn][-O git-org][-P file:line][-p pattern][-Q file][-qr][-S false|true][-T regex][-Vv][-X 0|1][-Y file][-Z] action sub sub2
    Travis-ci emulator for local developer environment
    Action may be: (help,emulate,force-lint,lint,force-test,test,force-test-multi,test-multi,force-testdeps,testdeps,force-translate,translate,chkconfig,parseyaml,show,show-log,show-color,summary,wep-db)
     -h --help            this help
     -A --trace-after regex
                          travis stops after executed yaml statement
     -B --debug           debug mode: do not create log
     -C --no-cache        do not use stored PYPI
     -D --debug-level number
                          travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)
     -E --no-savenv       do not save virtual environment into ~/VME/... if does not exist
     -e --locale iso
                          use locale
     -F --full            run final travis with full features
     -f --force           force to create stored VME or remove recent log (wep-db)
     -k --keep            keep DB and virtual environment before and after tests
     -j --python pyver
                          test with specific python versions (comma separated)
     -L --lint-level number
                          lint_check_level: may be minimal,reduced,average,nearby,oca; def value from .travis.yml
     -l --logdir dir
                          log directory (def=/home/odoo/travis_log)
     -m --missing         show missing line in report coverage
     -n --dry-run         do nothing (dry-run)
     -O --org git-org
                          git organization to test, i.e. oca or zeroincombenze
     -P --python-brk file:line
                          set python breakpoint at file:linenumber
     -p --pattern pattern
                          pattern to apply for test files (comma separated)
     -Q --config file
                          configuration file (def .z0tools.conf)
     -q --quiet           silent mode
     -r                   run restricted mode (deprecated)
     -S --syspkg false|true
                          use python system packages (def yaml dependents)
     -T --trace regex
                          trace stops before executing yaml statement
     -V --version         show version
     -v --verbose         verbose mode
     -X --translation 0|1
                          enable translation test (def yaml dependents)
     -Y --yaml-file file
                          file yaml to process (def .travis.yml)
     -Z --zero            use local zero-tools
    
    © 2015-2022 by zeroincombenze®
    https://zeroincombenze-tools.readthedocs.io/
    Author: antoniomaria.vigliotti@gmail.com
    


Configuration file
~~~~~~~~~~~~~~~~~~

Values in configuration file are:

+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| Parameter         | Descriptio                                         | Default value                                                                                |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| CHAT_HOME         | URL to web chat to insert in documentation         |                                                                                              |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| ODOO_SETUPS       | Names of Odoo manifest files                       | __manifest__.py __openerp__.py __odoo__.py __terp__.py                                       |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| dbtemplate        | Default value for MQT_TEMPLATE_DB                  | template_odoo                                                                                |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| dbname            | Default value for MQT_TEST_DB                      | test_odoo                                                                                    |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| dbuser            | Postgresql user: default value for MQT_DBUSER      | $USER                                                                                        |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| UNBUFFER          | Use unbuffer                                       | 0                                                                                            |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| virtualenv_opts   | Default option to create virtual environment       |                                                                                              |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| NPM_CONFIG_PREFIX | N/D                                                | \$HOME/.npm-global                                                                           |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_TXT_COLOR      | N/D                                                | 0;97;40                                                                                      |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_RUN_COLOR      | N/D                                                | 1;37;44                                                                                      |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_NOP_COLOR      | N/D                                                | 31;100                                                                                       |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_HDR1_COLOR     | N/D                                                | 97;42                                                                                        |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_HDR2_COLOR     | N/D                                                | 30;43                                                                                        |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_HDR3_COLOR     | N/D                                                | 30;45                                                                                        |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| LOCAL_PKGS        | N/D                                                | clodoo lisa odoo_score os0 python-plus travis_emulator wok_code z0bug-odoo z0lib zar zerobug |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PYTHON_MATRIX     | Python version available to test (space separated) |                                                                                              |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+

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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.10/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.10/man
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
