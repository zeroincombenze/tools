.. toctree::
   :maxdepth: 2

Code example
~~~~~~~~~~~~

*zerobug* makes avaiable following functions to test:

|

`Z0BUG.setup(ctx)` (python)

`Z0BUG_setup` (bash)

Setup for test. It is called before all tests.

|

`Z0BUG.teardown(ctx)` (python)

`Z0BUG_teardown` (bash)

Setup for test. It is called after all tests.

|

`Z0BUG.build_os_tree(ctx, list_of_paths)` (python)

`Z0BUG_build_os_tree list_of_paths` (bash)

Build a full os tree from supplied list.
If python, list of paths is a list of strings.
If bash, list is one string of paths separated by spaces.
Function reads list of paths and then create all directories.
If directory is an absolute path, it is created with the supplied path.
If directory is a relative path, the directory is created under "tests/res" directory.

Warning!
To check is made is parent dir does not exit. Please, supply path from parent
to children, if you want to build a nested tree.

::

    # (python)
    from zerobug import Z0BUG
    class RegressionTest():

        def __init__(self, Z0BUG):
            self.Z0BUG = Z0BUG

        def test_01(self, ctx):
            os_tree = ['10.0',
                       '10.0/addons',
                       '10.0/odoo',]
            root = self.Z0BUG.build_os_tree(ctx, os_tree)

::

    # (bash)
    Z0BUG_setup() {
        Z0BUG_build_os_tree "10.0 10.0/addons 10.0/odoo"
    }

|

`Z0BUG.remove_os_tree(ctx, list_of_paths)` (python)

`Z0BUG_remove_os_tree list_of_paths` (bash)

Remove a full os tree created by `build_os_tree`
If python, list of paths is a list of strings.
If bash, list is a string of paths separated by spaces.
Function reads list of paths and remove all directories.
If directory is an absolute path, the supplied path is dropped.
If directory is a relative path, the directory is dropped from tests/res directory.

Warning!
This function remove directory and all sub-directories without any control.

::

    # (python)
    from zerobug import Z0BUG
    class RegressionTest():

        def __init__(self, Z0BUG):
            self.Z0BUG = Z0BUG

        def test_01(self, ctx):
            os_tree = ['10.0',
                       '10.0/addons',
                       '10.0/odoo',]
            root = self.Z0BUG.remove_os_tree(ctx, os_tree)

|

`Z0BUG.build_odoo_env(ctx, version)` (python)

Like build_os_tree but create a specific odoo os tree.

::

    # (python)
    from zerobug import Z0BUG
    from zerobug import Z0testOdoo
    class RegressionTest():

        def __init__(self, Z0BUG):
            self.Z0BUG = Z0BUG

        def test_01(self, ctx):
            root = Z0testOdoo.build_odoo_env(ctx, '10.0')

|

`Z0BUG.git_clone(remote, reponame, branch, odoo_path, force=None)` (python)

Execute git clone of `remote:reponame:branch` into local directory `odoo_path`.
In local travis emulation, if repository uses local repository, if exists.
Return odoo root directory

::

    # (python)
    from zerobug import Z0BUG
    from zerobug import Z0testOdoo

    from zerobug import Z0BUG
    class RegressionTest():

        def __init__(self, Z0BUG):
            self.Z0BUG = Z0BUG

        def test_01(self, ctx):
            remote = 'OCA'
            reponame = 'OCB'
            branch = '10.0'
            odoo_path = '/opt/odoo/10.0'
            Z0testOdoo.git_clone(remote, reponame, branch, odoo_path)


|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2021-07-08

.. |Maturity| image:: https://img.shields.io/badge/maturity-Mature-green.png
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
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=1.0.1.2
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/1.0.1.2/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/1.0.1.2
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-1.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/1.0.1.2/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-1.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/1.0.1.2/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-1.svg
    :target: https://erp1.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/1.0.1.2/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/1.0.1.2
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


