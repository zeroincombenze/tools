.. toctree::
   :maxdepth: 2

Zerobug
=======


This library can run unit test of software target package.
Supported languages are *python* (through z0testlib.py) and *bash* (through z0testrc)

*zerobug* was born to supports test automation, aggregation of tests into collections
and independence of the tests from the reporting framework.
Currently is becoming an improvements of *python unittest2* but still run bash tests.

The command **zerobug** of this package runs tests: it searches for test runner
files named ``test_`` (see -p switch).

Test suite is a collection of test case named ``test_[0-9]+`` inside the runner file,
executed in sorted order.

Every suite can contains one or more test case, the smallest unit test;
every unit test terminates with success or with failure.

*zerobug* is full integrated with coverage and travis-ci.

::

    usage: zerobug [-h] [-B] [-C] [-e] [-f] [-J] [-k] [-l file] [-N] [-n] [-O]
                   [-p file_list] [-Q] [-q] [-R] [-r number] [-s number] [-V] [-v]
                   [-x] [-X] [-z number] [-0]
    
    Regression test on zerobug
    
    optional arguments:
      -h, --help            show this help message and exit
      -B, --debug           run tests in debug mode
      -C, --no-coverage     run tests without coverage
      -e, --echo            enable echoing even if not interactive tty
                            (deprecated)
      -f, --failfast        Stop on first fail or error
      -J                    load travisrc (deprecated)
      -k, --keep            keep current logfile (deprecated)
      -l file, --logname file
                            set logfile name (deprecated)
      -N, --new             create new logfile (deprecated)
      -n, --dry-run         count and display # unit tests (deprecated)
      -O                    load odoorc (deprecated)
      -p file_list, --search-pattern file_list
                            Pattern to match tests, comma separated ('test*.py'
                            default)
      -Q, --count           count # unit tests (deprecated)
      -q, --quiet           run tests without output (quiet mode, deprecated)
      -R, --run-inner       inner mode w/o final messages
      -r number, --restart number
                            restart count next to number
      -s number, --start number
                            deprecated
      -V, --version         show program's version number and exit
      -v, --verbose         verbose mode
      -x, --qsanity         like -X but run silently (deprecated)
      -X, --esanity         execute test library sanity check and exit
                            (deprecated)
      -z number, --end number
                            display total # tests when execute them
      -0, --no-count        no count # unit tests (deprecated)
    
    © 2015-2023 by SHS-AV s.r.l. - https://zeroincombenze-
    tools.readthedocs.io/en/latest/zerobug
    

|
|

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.5/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.5/man
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
