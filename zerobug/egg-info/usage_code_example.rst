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
