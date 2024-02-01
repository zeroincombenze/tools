.. toctree::
   :maxdepth: 2

Digest of code_example
======================


Code example
~~~~~~~~~~~~

*zerobug* makes available following functions to test:

::

    Z0BUG_setup         # bash
    Z0BUG.setup(ctx)    # python (deprecated)
    Z0BUG.setup()       # python


Setup for test. It is called before all tests. It has same functionality of
unittest2.setup()

::

    Z0BUG_teardown         # bash
    Z0BUG.teardown(ctx)    # python (deprecated)
    Z0BUG.teardown()       # python

Clear at the end of test. It is called after all tests. It has same functionality of
unittest2.teardown()

::

    Z0BUG_build_os_tree  list_of_paths         # bash
    Z0BUG.Z.build_os_tree(ctx, list_of_paths)  # python

Build a full os tree from supplied list.
If python, list of paths is a list of strings.
If bash, list is one string of paths separated by spaces.
Function reads list of paths and then create all directories.
If directory is an absolute path, it is created with the supplied path.
If directory is a relative path, the directory is created under **tests/res** directory.

.. warning::

    No check is made if parent dir does not exit. Please, supply path from parent
    to children, if you want to build a nested tree.

::

    Z0BUG_remove_os_tree  list_of_paths         # bash
    Z0BUG.Z.remove_os_tree(ctx, list_of_paths)  # python

Remove a full os tree created by ``build_os_tree``
If python, list of paths is a list of strings.
If bash, list is a string of paths separated by spaces.
Function reads list of paths and remove all directories.
If directory is an absolute path, the supplied path is dropped.
If directory is a relative path, the directory is dropped from tests/res directory.

..  warning::

    This function remove directory and all sub-directories without any control


::

    #! python
    from zerobug import z0test

    class RegressionTest():

        def setup(self):
            pass

        def teardown(self):
            os_tree = [
                '16.0/addons',
                '16.0/odoo',
                '16.0'
            ]
            root = self.Z.remove_os_tree(ctx, os_tree)

        def test_01(self):
            os_tree = [
                '16.0',
                '16.0/addons',
                '16.0/odoo'
            ]
            root = self.Z.build_os_tree(ctx, os_tree)

::

    #! bash
    Z0BUG_setup() {
        :
    }

    Z0BUG_teardwon() {
            Z0BUG_build_os_tree "16.0/addons 16.0/odoo 16.0"
    }

    test_01() {
        Z0BUG_build_os_tree "16.0 16.0/addons 16.0/odoo"
    }

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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.14/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.14/man
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
