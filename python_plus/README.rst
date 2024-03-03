==================
python_plus 2.0.12
==================



|Maturity| |license gpl|



Overview
========

python-plus adds various features to python 2 and python 3 programs.
It is designed to be used as integration of pypi future to help to port your code from
Python 2 to Python 3 and still have it run on Python 2.

Overview
--------

list_requirements.py: list environment requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command is an internal command of python-plus but may be used as own command.
list_requirements.py displays the pypi and binaries packages needed to create a virtual
environment.
It is specially designed to show Odoo requirements.
Passing Odoo path it reads requirements.txt files in path and setup directories of OCA
repositories.

vem: virtual environment manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command is an interactive tool with some nice features to manage standard virtual
environment.
Mainly it works ad standard pip but inside a specific virtual environment.



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

    Usage: vem.sh [-h][-a list][-BCD][-d paths][-E distro][-f][-F name][-gkIi][-l iso][-n][-O version][-o dir][-p pyver][-q][-r file][-stVvy] p3 p4 p5 p6 p7 p8 p9
    Manage virtual environment
    action may be: help amend cp check create exec info inspect install merge mv python shell rm show uninstall update test
     -h --help            this help
     -a list              bin packages to install (* means wkhtmltopdf,lessc)
     -B                   use unstable packages: -B testpypi / -BB from ~/tools / -BBB from ~/pypi / -BBBB link to local ~/pypi
     -C                   clear cache before executing pip command
     -D --devel           create v.environment with development packages
     -d --dep-path paths
                          odoo dependencies paths (comma separated)
     -E --distro distro
                          simulate Linux distro: like Ubuntu20 Centos7 etc (requires -n switch)
     -f --force           force v.environment create, even if exists or inside another virtual env
     -F name              simulate Linux family: may be RHEL or Debian (requires -n switch)
     -g --global          install npm packages globally
     -k --keep            keep python2 executable as python (deprecated)
     -I --indipendent     run pip in an isolated mode and set home virtual directory
     -i --isolated        run pip in an isolated mode, ignoring environment variables and user configuration
     -l --lang iso
                          set default language
     -n --dry_run         do nothing (dry-run)
     -O --odoo-ver version
                          install pypi required by odoo version (amend or create)
     -o --odoo-path dir
                          odoo path used to search odoo requirements
     -p --python pyver
                          python version
     -q --quiet           silent mode
     -r --requirement file
                          after created v.environment install from the given requirements file
     -s --system-site-pack
                          create v.environment with access to the global site-packages
     -t --travis          activate environment for travis test
     -V --version         show version
     -v --verbose         verbose mode
     -y --yes             assume yes

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



Getting started
===============


Prerequisites
-------------

Zeroincombenze tools requires:

* Linux Centos 7/8 or Debian 9/10 or Ubuntu 18/20/22
* python 2.7+, some tools require python 3.6+, best python 3.8+
* bash 5.0+



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

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install --upgrade python_plus

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



ChangeLog History
-----------------

2.0.12 (2024-02-29)
~~~~~~~~~~~~~~~~~~~

* [IMP] New function str2bool()

2.0.11 (2024-02-05)
~~~~~~~~~~~~~~~~~~~

* [FIX] vem: show right python version if 3.10+
* [IMP] list_requirements.py improvements
* [IMP] new python version assignment from odoo version

2.0.10 (2023-07-18)
~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: werkzeug for Odoo 16.0
* [FIX] vem create: sometimes "virtualenv create" fails for python 2.7
* [IMP] pip install packages with use2to3 is backupgrdae to < 23

2.0.9 (2023-06-26)
~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: werkzeug for Odoo 16.0
* [IMP] list_requirements.py: best recognize mixed version odoo/python
* [FIX] vem: commands return application status

2.0.7 (2023-05-08)
~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: upgrade version for Odoo 16.0
* [REF] vem: partial refactoring
* [IMP] Mots coverage test

2.0.6 (2023-03-24)
~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: cryptography, pypdf2, requests & urllib3 version adjustment
* [IMP] list_requirements.py: pypdf and pypdf2 version adjustment
* [IMP] list_requirements.py: best resolution when versions conflict
* [IMP] vem: set list_requirements.py executable

2.0.5 (2022-12-23)
~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: refactoring version control
* [IMP] vem: now amend can check current version (with -f switch)

2.0.4 (2022-12-15)
~~~~~~~~~~~~~~~~~~

* [IMP] Package version adjustment
* [IMP] vem: amend show current package version
* [IMP] vem: no python2 warning in linux kernel 3
* [FIX] vem: best recognition of python version

2.0.3 (2022-11-08)
~~~~~~~~~~~~~~~~~~

* [IMP] npm management
* [IMP] compute_date: refdate may be a string

2.0.2.1 (2022-11-01)
~~~~~~~~~~~~~~~~~~~~

* [FIX] Ensure coverage 5.0+

2.0.2 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [FIX] vem: wrong behavior with > o < in version
* [IMP] list_requirements.py: "Crypto.Cipher": "pycrypto"

2.0.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~

* [IMP] stable version

2.0.0.3 (2022-09-14)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: install package with list_requirements.py

2.0.0.2 (2022-09-10)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: no input inquire

2.0.0.1 (2022-09-06)
~~~~~~~~~~~~~~~~~~~~

* [IMP] vem: new switch -d for Odoo dependencies path
* [FIX] vem: create with best package list
* [FIX] vem: install odoo/openerp


2.0.0 (2022-08-10)
~~~~~~~~~~~~~~~~~~

* [IMP] Stable version



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

* `Antonio Maria Vigliotti <info@shs-av.com>`__
* `Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>`__


|
|

.. |Maturity| image:: https://img.shields.io/badge/maturity-Mature-green.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.12/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.12/man
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
