
==========
os0 0.2.15
==========



|Maturity| |Build Status| |Coverage Status| |license gpl|




Overview
========

Module os0
==========

Operating System indipendent interface
--------------------------------------


Operating System indipendent interface
--------------------------------------

This module provides a portable way of using operating system dependent functionality.
It expands standard os module naming using both URI standard name both local name, as UNC and ODS5.

* URI (Uniform Resource Identifier) is standard posix filename.
* UNC (Uniform Naming Convention) is windows standard
* ODS5 is used for define OpenVMS standard filenames

An example of URI filename is '/home/myfile'.

UNC example for the same of previous URI name is '\\home\\myfile' (with single backslash)

ODS5 (OpenVMS) for the same of previous URI name is '[home]myfile'

See https://en.wikipedia.org/wiki/Path_(computing)

Features:
* Conversion any string type to unicode or utf-8 (avoid python2/3 conflict)
* Manage both URI both local filenames

URI filename conversion rules by os0.setlfilename

+--------------------+------------------+--------------------+-----------------------+
| Case               | Linux            | Windows            | OpenVMS               |
+--------------------+------------------+--------------------+-----------------------+
| Simple file        | myfile.ext       | myfile.ext         | myfile.ext            |
+--------------------+------------------+--------------------+-----------------------+
| Abs pathname       | /root/myfile.ext | \\root\\myfile.ext | [root]myfile.ext      |
+--------------------+------------------+--------------------+-----------------------+
| Rel pathname       | lib/myfile.ext   | lib\\myfile.ext    | [.lib]myfile.ext      |
+--------------------+------------------+--------------------+-----------------------+
| CWD pathname       | ./myfile.ext     | .\\myfile.ext      | []myfile.ext          |
+--------------------+------------------+--------------------+-----------------------+
| Updir pathname     | ../myfile.ext    | ..\\myfile.ext     | [-]myfile.ext         |
+--------------------+------------------+--------------------+-----------------------+
| Root file          | /myfile.ext      | \\myfile.ext       | [000000]myfile.ext    |
+--------------------+------------------+--------------------+-----------------------+
| dotted pathname    | /u/os.1.0/a.b.c  | \\u\\os.1.0/a.b.c  | [u.os^.1^.0]a^.^.b.c  |
+--------------------+------------------+--------------------+-----------------------+
| hidden/leading dot | .myfile          | .myfile            | .myfile ??            |
+--------------------+------------------+--------------------+-----------------------+
|                    |                  |                    |                       |
+--------------------+------------------+--------------------+-----------------------+
| executable         | myfile           | myfile.exe         | myfile.exe            |
+--------------------+------------------+--------------------+-----------------------+
| command file       | myfile           | myfile.bat         | myfile.com            |
+--------------------+------------------+--------------------+-----------------------+
| directory          | mydir/           | mydir              | mydir.DIR             |
+--------------------+------------------+--------------------+-----------------------+
|                    |                  |                    |                       |
+--------------------+------------------+--------------------+-----------------------+
| dev null           | /dev/null        | nul                | NL0:                  |
+--------------------+------------------+--------------------+-----------------------+
| dev/disk/myfile    | /dev/disk/myfile | c:\\myfile         | disk:[000000]myfile   |
+--------------------+------------------+--------------------+-----------------------+
| system disk        | /c/temp/myfile   | c:\\temp\\myfile   | c:[temp]myfile        |
+--------------------+------------------+--------------------+-----------------------+



Notes:
* URL with username (user@) is not supported by this version
* URL with port number or service (http:) is not supported by this version
* URL with server domain (//server) is not supported by this version
* URL with character encoding (%20) is not supported by this version
* Linux has not disk device in pathname; in order to manager Windows and
  OpenVMS devices here is used /dev/disk where disk may be a letter in Windows
  or a name in OpenVMS.
  Both Windows and OpenVMS use colon (:) at the end of disk device in local
  pathname (see last but one example above)
* Here is also implemented a brief form for disk device, if exist on hosting
  machine
  Brief form is /dev/pathname like /c/windows/ or /sys$sysdevice/sys0/
  This brief form may be not universal translatable (see last example above)
* Updir (..) may be recursive -> ../../myfile -> ..\\..\\myfile -> [-.-]myfile
* Home dir (~/myfile) is no supported by this version
* OpenVMS logical names use dollar sign, such as sys$sysdevice;
  in Linux dollar start a macro.
  Need to verify about some trouble
* OpenVMS files have version; syntax is 'myfile.exe;ver' where ';ver'
   can be omitted
   No any other OS has this feature, so in version of module there is no
   support for filename version






To use module os0 import it
    >>> from os0 import os0

First method is set local filename of URI file.
Set local filename of URI name is the same URI name
    >>> os0.setlfilename('myFile')
    'myFile'

Set local filename has optional parameter. FLAT means generic file name
    >>> os0.setlfilename('myFile', os0.LFN_FLAT)
    'myFile'

Executable file in Windows or OpenVMS have .EXE extension.
Conversion of URI name must add .EXE suffix, while URI is unchanged.
    >>> os0.setlfilename('myFile', os0.LFN_EXE)
    'myFile'

Command file in Windows has .BAT suffix while in OpenVMS haS .COM extension.
Conversion of URI name must add these suffix, while URI is unchanged.
    >>> os0.setlfilename('myFile', os0.LFN_CMD)
    'myFile'

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
    pip install os0

|

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    source /opt/odoo/devel/activate_tools


|
|

Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


Contributors
------------

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>

|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2020-06-26

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alfa
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=.
    :target: https://travis-ci.org/zeroincombenze/tools
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=.
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=.
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/./graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/.
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-0.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/./dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-0.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/./man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-0.svg
    :target: https://erp0.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/./graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/.
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
   :target: https://t.me/axitec_helpdesk


