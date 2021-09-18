Code example
~~~~~~~~~~~~

*zerobug* makes available following functions to test:

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

Build a full os tree to test.

Function reads list of paths and then creates all directories.
If directory is an absolute path, it is created with the supplied path.
If directory is a relative path,
the directory is created under "tests/res" directory.

Warning!
No check is made is parent dir does not exit.
Please, supply path from parent to children,
if you want to build a nested tree.

Args:
    * os_tree (list): list of directories to create

Returns:
    str: parent path of filesystem

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

Function reads list of paths and removes all directories.
If directory is an absolute path, the supplied path is dropped.
If directory is a relative path,
the directory is dropped from tests/res directory.

Warning!
This function remove directory and
all sub-directories without any control.

Args:
    * os_tree (list): list of directories to remove

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

Build a simplified Odoo directory tree to test.
The path contains addons, odoo-bin/openerp and release.py files.

Args:
    * version (str): '14.0','13.0',...,'7.0','6.1'
    * hierarchy (str): flat,tree,server, default 'flat'

Returns:
    str:  Filesystem root of Odoo

::

    # (python)
    from zerobug import Z0BUG
    from zerobug import Z0testOdoo
    class RegressionTest():

        def __init__(self, Z0BUG):
            self.Z0BUG = Z0BUG

        def test_01(self, ctx):
            # Create the root directory
            version = '12.0'
            root = Z0testOdoo.build_odoo_env(ctx, version)
            # Create the repository l10n-italy
            repos_dir = Z0testOdoo.build_odoo_repos(
                    ctx, root, version, 'l10n-italy')
            # Create the module l10n_it_account
            module_name = 'l10n_it'
            manifest = {
                'version': '0.1.0',
            }
            module_dir = Z0testOdoo.build_odoo_module(
                ctx, repos_dir, module_name, manifest)

|

`Z0BUG.build_odoo_repos(self, ctx, root, repos)` (python)

Create a repository directory `repos` under the Odoo root
returned by `build_odoo_env` function.

Args:
    * root (str): root filesystem, returned by `build_odoo_env`
    * version (str): '14.0','13.0',...,'7.0','6.1'
    * repos (str): repository name to create

Returns:
    str: path to repository

See example `Z0BUG.build_odoo_env(ctx, version)`

|

`Z0BUG.build_odoo_module(self, ctx, repos_dir, module_name, manifest):` (python)

Create an Odoo module tree under repos_dir
returned by build_odoo_repos.
File manifest is filled with data passed.
No file are added to Odoo tree.

Args:
    * repos_dir (str): repository path
    * module_name (str): module name
    * manifest (dict): manifest contents

Returns:
    str: parent path of Odoo filesystem

See example `Z0BUG.build_odoo_env(ctx, version)`

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
