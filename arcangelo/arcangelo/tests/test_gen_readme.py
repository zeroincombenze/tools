# -*- coding: utf-8 -*-
# flake8: noqa - pylint: skip-file
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
import os
import sys

from python_plus import _c
from z0lib import z0lib
from zerobug import z0test, z0testodoo

sys.path.insert(0,
                os.path.dirname(os.path.dirname(os.getcwd()))
                if os.path.basename(os.getcwd()) == "tests"
                else os.path.dirname(os.getcwd()))                         # noqa: E402
from arcangelo.scripts import gen_readme

__version__ = "2.0.22"

MODULE_ID = "wok_code"
TEST_FAILED = 1
TEST_SUCCESS = 0
ODOO_VERSIONS = ("12.0", "10.0", "7.0")

DESCR_FN = """Lorem ipsum
-----------

Lorem ipsum **dolor** sit amet
.. $if branch in '%s'
consectetur *adipiscing* elit
.. $fi
.. $if branch in '12.0'
odoo 12.0
.. $elif branch in '10.0'
odoo 10.0
.. $elif branch in '8.0'
odoo 8.0
.. $else
Unknown Odoo version
.. $fi

* Feature A
* Feature B

::

    >>> doc
|
.. image:: logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

+-----------+---------+
| Feature A | |check| |
+-----------+---------+
| Feature B |         |
+-----------+---------+
| Feature C | ©SHS    |
+-----------+---------+
"""

AUTHORS_FN = """Lorem ipsum
.. $if branch in '%s'
* SHS-AV s.r.l. <https://www.shs-av.com>
.. $elif branch in '12.0'
* wrong author <https://12.0>
.. $elif branch in '10.0'
* wrong author <https://10.0>
.. $elif branch in '8.0'
* wrong author <https://8.0>
.. $else
Unknown Odoo version
.. $fi
"""

CONTRIBUTORS_FN = """Lorem ipsum
.. $if branch in '%s'
* antonio <antoniov@libero.it>
.. $elif branch in '12.0'
* alberta <alberta@libero.it>
.. $elif branch in '10.0'
* daniela <daniela@libero.it>
.. $elif branch in '8.0'
* elia <elia@libero.it>
.. $else
Unknown Odoo version
.. $fi
"""

README_MAIN_MODULE = """
{{description}}
"""

README_7 = """Lorem ipsum **dolor** sit amet
consectetur *adipiscing* elit
Unknown Odoo version

* Feature A
* Feature B

::

    >>> doc
|
.. image:: https://raw.githubusercontent.com/zeroincombenze/test_repo/7.0/test_module/static/src/img/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

+-----------+---------+
| Feature A | |check| |
+-----------+---------+
| Feature B |         |
+-----------+---------+
| Feature C | ©SHS    |
+-----------+---------+
"""

README_10 = """Lorem ipsum **dolor** sit amet
consectetur *adipiscing* elit
odoo 10.0

* Feature A
* Feature B

::

    >>> doc
|
.. image:: https://raw.githubusercontent.com/zeroincombenze/test_repo/10.0/test_module/static/description/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

+-----------+---------+
| Feature A | |check| |
+-----------+---------+
| Feature B |         |
+-----------+---------+
| Feature C | ©SHS    |
+-----------+---------+
"""

README_12 = """Lorem ipsum **dolor** sit amet
consectetur *adipiscing* elit
odoo 12.0

* Feature A
* Feature B

::

    >>> doc
|
.. image:: https://raw.githubusercontent.com/zeroincombenze/test_repo/12.0/test_module/static/description/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

+-----------+---------+
| Feature A | |check| |
+-----------+---------+
| Feature B |         |
+-----------+---------+
| Feature C | ©SHS    |
+-----------+---------+
"""


def version():
    return __version__


class RegressionTest:

    def setup(self):
        self.templatedir = os.path.join(
            os.path.expanduser("~"), "devel", "pypi", "tools", "templates"
        )
        self.icon_templatedir = os.path.join(self.templatedir, "icons")
        if not os.path.isdir(self.templatedir):
            os.makedirs(self.templatedir)
        if not os.path.isdir(self.icon_templatedir):
            os.makedirs(self.icon_templatedir)
        with open(os.path.join(self.templatedir, "footer.rst"), "w") as fd:
            fd.write(
                _c(
                    """
----------------------

.. |en| image:: {{grymb_image_en}}
   :target: {{grymb_url_en}}
.. |it| image:: {{grymb_image_it}}
   :target: {{grymb_url_it}}
"""
                )
            )
        with open(os.path.join(self.templatedir, "header_authors.txt"), "w") as fd:
            fd.write(
                _c(
                    """
Authors
-------
"""
                )
            )
        with open(os.path.join(self.templatedir, "header_contributors.txt"), "w") as fd:
            fd.write(
                _c(
                    """
Contributors
------------
"""
                )
            )
        with open(os.path.join(self.templatedir, "header_acknowledges.txt"), "w") as fd:
            fd.write(
                _c(
                    """
Acknoledges to
--------------
"""
                )
            )

        self.create_readme_main_module_file()


        with open(
                os.path.join(self.templatedir, "readme_main_repository.rst"), "w"
        ) as fd:
            fd.write(
                _c(
                    """
{{description}}
"""
                )
            )
        with open(os.path.join(self.templatedir, "readme_main_ocb.rst"), "w") as fd:
            fd.write(
                _c(
                    """
{{description}}
"""
                )
            )
        with open(os.path.join(self.icon_templatedir, "l10n_it.png"), "w") as fd:
            pass
        with open(os.path.join(self.icon_templatedir, "l10n_uk.png"), "w") as fd:
            pass
        with open(os.path.join(self.icon_templatedir, "l10n_us.png"), "w") as fd:
            pass
        z0lib.os_system(
            "build_cmd %s" % os.path.join(self.rundir, "scripts", "gen_readme.py")
        )

    def get_doc_path(self, odoo_path, gitorg):
        doc_path = os.path.join(odoo_path, "readme")
        if not os.path.isdir(doc_path):
            os.mkdir(doc_path)
        return doc_path

    def create_description_file(self, moduledir, odoo_version, gitorg):
        egg_info_path = self.get_doc_path(moduledir, gitorg)
        descr_fn = os.path.join(egg_info_path, "DESCRIPTION.rst")
        with open(descr_fn, "w") as fd:
            fd.write(_c(DESCR_FN % odoo_version))

    def create_authors_file(self, moduledir, odoo_version, gitorg):
        egg_info_path = self.get_doc_path(moduledir, gitorg)
        if gitorg == "zero":
            descr_fn = os.path.join(egg_info_path, "AUTHORS.rst")
            with open(descr_fn, "w") as fd:
                fd.write(_c(AUTHORS_FN % odoo_version))

    def create_contributors_file(self, moduledir, odoo_version, gitorg):
        egg_info_path = self.get_doc_path(moduledir, gitorg)
        descr_fn = os.path.join(egg_info_path, "CONTRIBUTORS.rst")
        with open(descr_fn, "w") as fd:
            fd.write(_c(CONTRIBUTORS_FN % odoo_version))

    def create_readme_main_module_file(self):
        tmpl_fn = os.path.join(self.templatedir, "readme_main_module.rst")
        with open(tmpl_fn, "w") as fd:
            fd.write(_c(README_MAIN_MODULE))

    def fn_source(self, fn):
        with open(fn) as fd:
            test_source = fd.read()
        return test_source

    def test_01(self):
        ctx = {
            "git_orgid": "zero",
            "odoo_marketplace": False,
            "write_index": False,
            "branch": "12.0",
            "odoo_majver": 12,
            "module_name": "mymodule",
            "repos_name": "myrepo",
        }
        src_url = "https://example.com/something"
        tgt_url = src_url
        self.assertEqual(gen_readme.url_by_doc(ctx, src_url),
                         tgt_url,
                         msg_info="README.rst")
        src_url = ("https://github.com/zeroincombenze/myrepo"
                   "/mymodule/static/description/icon.png")
        tgt_url = src_url
        self.assertEqual(gen_readme.url_by_doc(ctx, src_url), tgt_url)
        src_url = "icon.png"
        tgt_url = ("https://raw.githubusercontent.com/zeroincombenze/myrepo/12.0"
                   "/mymodule/static/description/icon.png")
        self.assertEqual(gen_readme.url_by_doc(ctx, src_url), tgt_url)

        ctx["write_index"] = True
        src_url = "https://example.com/something"
        tgt_url = src_url
        self.assertEqual(gen_readme.url_by_doc(ctx, src_url),
                         tgt_url,
                         msg_info="index.html")
        src_url = ("https://github.com/zeroincombenze/myrepo"
                   "/mymodule/static/description/icon.png")
        tgt_url = "icon.png"
        self.assertEqual(gen_readme.url_by_doc(ctx, src_url), tgt_url)
        src_url = "icon.png"
        tgt_url = src_url
        self.assertEqual(gen_readme.url_by_doc(ctx, src_url), tgt_url)

        ctx["write_index"] = False
        ctx["odoo_marketplace"] = True
        src_url = "https://example.com/something"
        tgt_url = src_url
        self.assertEqual(gen_readme.url_by_doc(ctx, src_url),
                         tgt_url,
                         msg_info="marketplace")
        src_url = ("https://github.com/zeroincombenze/myrepo"
                   "/mymodule/static/description/icon.png")
        tgt_url = "icon.png"
        self.assertEqual(gen_readme.url_by_doc(ctx, src_url), tgt_url)
        src_url = "icon.png"
        tgt_url = src_url
        self.assertEqual(gen_readme.url_by_doc(ctx, src_url), tgt_url)

    def test_02(self):
        base_cmd = os.path.join(self.rundir, "scripts", "gen_readme.py")
        gitorg = "zero"
        for odoo_version in ODOO_VERSIONS:
            os.chdir(self.testdir)
            self.root = z0testodoo.build_odoo_env(odoo_version)
            odoo_root = os.path.join(self.root, odoo_version)
            repodir = z0testodoo.create_repo(
                odoo_root, "test_repo", odoo_version
            )
            moduledir = z0testodoo.create_module(
                repodir, "test_module", "%s.0.1.0" % odoo_version
            )
            self.create_description_file(moduledir, odoo_version, gitorg)
            self.create_authors_file(moduledir, odoo_version, gitorg)
            self.create_contributors_file(moduledir, odoo_version, gitorg)
            os.chdir(moduledir)
            cmd = "%s -fBwG%s" % (base_cmd, gitorg)
            sts, stdout, stderr = z0lib.os_system_traced(cmd)
            self.assertEqual(sts, 0, msg_info="cd %s; %s" % (moduledir, cmd))
            for fn in ("__manifest__.rst",
                       "CHANGELOG.rst",
                       "DESCRIPTION.it_IT.rst",
                       "USAGE.rst",
                       "USAGE.it_IT.rst",
                       "CONFIGURATION.rst",
                       "CONFIGURATION.it_IT.rst",
                       ):
                self.assertTrue(
                    os.path.isfile(os.path.join(moduledir, "readme", fn)),
                    msg_info="%s -> %s" % (cmd, fn))

            if odoo_version == "7.0":
                self.assertEqual(
                    README_7,
                    self.fn_source(os.path.join(moduledir, "README.rst")),
                    msg_info=os.path.join(moduledir,
                                          "README.rst") + "  #" + odoo_version)
            elif odoo_version == "10.0":
                self.assertEqual(
                    README_10,
                    self.fn_source(os.path.join(moduledir, "README.rst")),
                    msg_info=os.path.join(moduledir,
                                          "README.rst") + "  #" + odoo_version)
            elif odoo_version == "12.0":
                self.assertEqual(
                    README_12,
                    self.fn_source(os.path.join(moduledir, "README.rst")),
                    msg_info=os.path.join(moduledir,
                                          "README.rst") + "  #" + odoo_version)


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )



