
=================
python_plus 1.0.5
=================



|Maturity| |Build Status| |Coverage Status| |license gpl|




Overview
========

Python supplemental features
----------------------------

python_plus adds various features to python 2 and python 3 programs.
It is designed to be used as integration of pypi future to help to port your code from Python 2 to Python 3 and still have it run on Python 2.


vem: virtual environment manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This packge is released with an nice command:
**vem** that is an interactive tool with some nice features to manage standard virtual environment and it is osx/darwin compatible.



|

Usage
=====

Code example
------------

class / type test
~~~~~~~~~~~~~~~~~

Test if a string is unicode.

On Py2, this gives us:

    >>> s = 'Hello World'
    >>> isinstance(object, str)
    True

On Py3, this gives us:

    >>> s = b'Hello World'
    >>> isinstance(object, bytes)
    True


Then, for example, the following code has the same effect on Py2 as on Py3:

    >>> from python_plus import isbytestr
    >>> s = b'Hello World'
    >>> isbytestr(s)
    True


quoted string
~~~~~~~~~~~~~

Using class __:

    >>> from python_plus import __

    >>> my_str_list = __('abc,"d,e",fgh')
    >>> my_list = my_str_list.qsplit(my_str_list)
    >>> print my_list
    ['abc', 'd,e', 'fgh']

|

General function:

    >>> from python_plus import qsplit

    >>> my_str_list = 'abc,"d,e",fgh'
    >>> my_list = qsplit(my_str_list)
    >>> print my_list
    ['abc', 'd,e', 'fgh']



Code reference
~~~~~~~~~~~~~~

`` str.qslit(sep=None, maxsplit=-1, quotes=['"', '"'], escape=None, enquote=None, strip=None)``

Like split function return a list of the words in the string, using sep as the delimiter string. If maxsplit is given, at most maxsplit splits are done (thus, the list will have at most maxsplit+1 elements). If maxsplit is not specified or -1, then there is no limit on the number of splits (all possible splits are made).

If sep is given, consecutive delimiters are not grouped together and are deemed to delimit empty strings (for example, '1,,2'.split(',') returns ['1', '', '2']). The sep argument may consist of multiple characters (for example, '1<>2<>3'.split('<>') returns ['1', '2', '3']). Splitting an empty string with a specified separator returns [''].

If quotes is given, it is used to recognize quoted string: the sep tokens inside quoted string are ignored. The paramters quotes may be a string or a list. If it is a string trailing and ending delimiters are the same, like usual python string; if list is given, the first element is initial delimiter and the second element is the final delimiter like in html tag.

If escape is given, it is used to escape delimiters.

If enquote is True, returned list elements are enquoted by delimiters.

If strip is Tru, trailing and tailing spaces in returned list elements are removed.


For example:

    >>> my_str_list = __('abc,"d,e",fgh')
    >>> print my_str_list.qsplit(my_str_list)
    ['abc', 'd,e', 'fgh']


vem: virtual environment manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    Usage: vem [-h][-a list][-BCDfkIin][-O version][-o dir][-p pyver][-q][-r file][-sVv] p1 p2 p3 p4 p5 p6 p7 p8 p9
    Manage virtual environment
    action may be: help amend cp check create exec info install merge mv python shell rm show update test reset
     -h --help            this help
     -a list              bin packages to install (* means wkhtmltopdf,lessc)
     -B                   debug mode: use unstable packages (testpypi / local tools / local devel)
     -C                   clear cache before execute pip command
     -D --devel           create v.environment with development packages
     -f --force           force v.environment create, even if exists or inside another virtual env
     -k --keep            keep python2 executable as python
     -I                   run pip in an isolated mode, set home virtual directory
     -i --isolated        run pip in an isolated mode, ignoring environment variables and user configuration
     -n --dry_run         do nothing (dry-run)
     -O --odoo-ver version
                          install pypi required by odoo ver (amend, create or reset)
     -o --odoo-path dir
                          odoo path:used to search odoo requirements and linked in venv
     -p --python pyver
                          python version
     -q --quiet           silent mode
     -r --requirement file
                          after created v.environment install from the given requirements file
     -s --system-site-pack
                          create v.environment with access to the global site-packages
     -V --version         show version
     -v --verbose         verbose mode

vem is an interactive tool with some nice features to manage standard virtual environment.

Action is one of:

* help
* amend [OPTIONS] [SRC_VENV]
* check [OPTIONS] [SRC_VENV]
* cp [OPTIONS] SRC_VENV TGT_ENV
* create -p PYVER [OPTIONS] [VENV]
* exec [OPTIONS] [VENV] CMD
* info [OPTIONS] [VENV] PKG
* install [OPTIONS] [VENV] PKG
* merge [OPTIONS] SRC_VENV TGT_ENV
* mv [OPTIONS] SRC_VENV TGT_ENV
* update [OPTIONS] [VENV] PKG
* uninstall [OPTIONS] [VENV] PKG
* test [OPTIONS] [VENV]
* reset [OPTIONS] [VENV]
* show [OPTIONS] [VENV] PKG

amend [OPTIONS] [SRC_VENV]
      Amend package versions against requirements.  May used after 'create' or 'reset' when requirements are changed.

check [OPTIONS] [SRC_VENV]
      Compare package versions against requirements.  May be used after 'create' or 'reset' to check virtual environment
      consistency.

cp [OPTIONS] SRC_VENV TGT_ENV
      Copy SOURCE environment directory to TGT_ENV, like the bash command 'cp' and  set  relative  path  inside  virtual
      environment to aim the new directory name.
      Copying virtual environments is not well supported.
      Each virtualenv has path information hard-coded into it, and there may be cases where the copy code does not know it needs to update a particular file.
      Use with caution.

create -p PYVER [OPTIONS] VENV
      Create  a  new  virtual environment directory VENV like virtualenv command but with some nice features.  Switch -p
      declare which python version will be used to create new environment.
      This action can install various python packages to create a ready to use environment directory.
      See -I -D -O -o -r switches to furthermore information.

exec [OPTIONS] [SRC_VENV] CMD ...
      Execute a command in virtual environment. Enclose command by quotes.

info [OPTIONS] [SRC_VENV] PKG
      Show information about pypi package if installed in virtual environment (alias of show)

install [OPTIONS] [SRC_VENV] PKG
      Install pypi package or bin package into virtual environment.
      Warning! currently just 2 bin packages can be installed: wkhtmltopdf and lessc

show [OPTIONS] [SRC_VENV] PKG
      Show information about pypi package if installed in virtual environment (alias of info)

uninstall [OPTIONS] [SRC_VENV] PKG
      Uninstall pypi package from virtual environment.

update [OPTIONS] [SRC_VENV] PKG
      Upgrade pypi package in virtual environment.



|
|

Getting started
===============


|

Installation
------------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install python_plus


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

    pip install python_plus -U

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

1.0.3.9 (2021-10-09)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: create virtualenv again with -f

1.0.3.8 (2021-10-08)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: run inside virtual environment

1.0.3.7 (2021-10-03)
~~~~~~~~~~~~~~~~~~~~

* [IMP] lost python-plus functions

1.0.3.6 (2021-10-01)
~~~~~~~~~~~~~~~~~~~~

* [IMP] full setuptools integrated + copy-pkg-data

1.0.3.5 (2021-09-30)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: 1st installation, z0librc not found

1.0.3.4 (2021-09-26)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: minor fixes

1.0.3.3 (2021-09-26)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: error message "riga 99: deactivate:"

1.0.3.2 (2021-09-25)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: create vem with -I switch
* [REF] vem refactoring

1.0.3.1 (2021-09-23)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: added click package
* [FIX] vem: create with devel packages

1.0.2.1 (2021-08-05)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: create set right python for all ven binaries

1.0.1.3 (2021-08-05)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: run in osx darwin
* [IMP] vem: virtual environment for travis test

1.0.1.3 (2021-08-05)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: uninstall package with if package version with ">"



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
Last Update / Ultimo aggiornamento: 2021-10-06
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
Last Update / Ultimo aggiornamento: 2021-10-08
Last Update / Ultimo aggiornamento: 2021-10-09
Last Update / Ultimo aggiornamento: 2021-10-14
Last Update / Ultimo aggiornamento: 2021-10-20
Last Update / Ultimo aggiornamento: 2021-10-25
Last Update / Ultimo aggiornamento: 2021-11-01
:target: https://t.me/Assitenza_clienti_powERP
Last Update / Ultimo aggiornamento: 2021-11-18
Last Update / Ultimo aggiornamento: 2021-11-27
Last Update / Ultimo aggiornamento: 2021-12-04
Last Update / Ultimo aggiornamento: 2021-12-05
Last Update / Ultimo aggiornamento: 2021-12-09
Last Update / Ultimo aggiornamento: 2021-12-11
Last Update / Ultimo aggiornamento: 2021-12-18
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

Last Update / Ultimo aggiornamento: 2021-12-21

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


