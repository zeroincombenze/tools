.. toctree::
   :maxdepth: 2

Overview
========


Travis emulator can emulate TravisCi parsing the **.travis.yml** file in local
Linux machine and it is osx/darwin compatible.
You can test your application before pushing code to github.com web site.

Travis emulator can creates all the build declared in ``travis.yml**``;
all the builds are executed in sequential way.
The directory ~/travis_log (see -l switch) keeps the logs of all builds created.
Please note that log file is a binary file with escape ANSI screen code.
If you want to see the log use one of following command:

::

    travis show

    less -R ~/travis_log/<build_name>.log

A travis build executes the following steps:

+-----------------------------------------------------------------+--------------------+----------+-----+
| Description                                                     | name               | local    | web |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Initialize from .travis.conf                                    | travis.conf        | ✔        | ✗   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Matrix initialization (python version too)                      | matrix             | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Build job                                                       | build              | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Optional install packages `apt addons`                          | addons.apt.package | simulate | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Optional install packages `cache`                               |                    | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Set global values `env global`                                  | env.global         | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute code `before_install`                                   | before_install     | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute build code `install`                                    |                    | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute build code `before_script`                              |                    | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute build code `script`                                     | script             | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute build `before_cache` (only if cache is effective)       |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute build code `after_success`                              |                    | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Or execute `after_failure`                                      |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Optional code `before_deploy` (only if deployment is effective) |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Optional code `deploy`                                          |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Optional code `after_deploy` (only if deployment is effective)  |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute code `after_script`                                     |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Wep from local .travis.conf                                     |                    | ✔        | ✗   |
+-----------------------------------------------------------------+--------------------+----------+-----+



Read furthermore info read `travis-ci phase <https://docs.travis-ci.com/user/job-lifecycle/>`__


Difference between local travis and web site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The travis emulator works mostly like TravisCi web site. However you ha to consider
some points where you run local tests:

Local software is not published

    When you test on your local PC, the software is not yet publishd.
    Perhaps you prefer test local packages or local modules.
    The travis emulator with z0bug_odoo replace the commands ``git clone`` with
    local `ln -s` creating logical link with local repository, if possible.
    Local module are searched in the testing module directory. See Odoo structure
    for furthermore info.

Your PC is not TravisCi web site

    Probability you have just one python interpreter and your user is not sudo enabled.
    The travis emulator run build just with Odoo interpreter installed even if your
    .travis.yml file contains more python version to test.
    The travis emulator does not try to install global packages because
    it does not change the PC configuration.
    Please, install manually all the global packages using apt-get, yum, dnf or your local installer software.

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
