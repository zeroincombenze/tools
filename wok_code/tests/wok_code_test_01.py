#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
import os
import sys

from python_plus import _c
from z0lib import z0lib
from zerobug import z0test, z0testodoo

__version__ = "2.0.1"

MODULE_ID = 'z0bug_odoo'
TEST_FAILED = 1
TEST_SUCCESS = 0
ODOO_VERSIONS = ('7.0', '10.0', '12.0')

DESCR_FN = r"""Lorem ipsum
-----------

Lorem ipsum **dolor** sit amet
.. \$if branch in '%s'
consectetur *adipiscing* elit
.. \$elif branch in '12.0'
odoo 12.0
.. \$elif branch in '10.0'
odoo 10.0
.. \$elif branch in '8.0'
odoo 8.0
.. \$else
Unknown Odoo version
.. \$fi

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
AUTHORS_FN = r"""Lorem ipsum
.. \$if branch in '%s'
* SHS-AV s.r.l. <https://www.shs-av.com>
.. \$elif branch in '12.0'
* wrong author <https://12.0>
.. \$elif branch in '10.0'
* wrong author <https://10.0>
.. \$elif branch in '8.0'
* wrong author <https://8.0>
.. \$else
Unknown Odoo version
.. \$fi
"""
CONTRIBUTORS_FN = r"""Lorem ipsum
.. \$if branch in '%s'
* antonio <antoniov@libero.it>
.. \$elif branch in '12.0'
* alberta <alberta@libero.it>
.. \$elif branch in '10.0'
* daniela <daniela@libero.it>
.. \$elif branch in '8.0'
* elia <elia@libero.it>
.. \$else
Unknown Odoo version
.. \$fi
"""


def version():
    return __version__


class RegressionTest:
    def __init__(self, z):
        self.templatedir = os.path.join(
            os.path.expanduser('~'), 'devel', 'pypi', 'tools', 'templates'
        )
        if not os.path.isdir(self.templatedir):
            os.makedirs(self.templatedir)
        with open(os.path.join(self.templatedir, 'footer.rst'), 'w') as fd:
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
        with open(os.path.join(self.templatedir, 'header_authors.txt'), 'w') as fd:
            fd.write(
                _c(
                    """
Authors
-------
"""
                )
            )
        with open(os.path.join(self.templatedir, 'header_contributors.txt'), 'w') as fd:
            fd.write(
                _c(
                    """
Contributors
------------
"""
                )
            )
        with open(os.path.join(self.templatedir, 'header_acknowledges.txt'), 'w') as fd:
            fd.write(
                _c(
                    """
Acknoledges to
--------------
"""
                )
            )
        with open(os.path.join(self.templatedir, 'readme_main_module.rst'), 'w') as fd:
            fd.write(
                _c(
                    """
{{description}}
"""
                )
            )
        with open(
            os.path.join(self.templatedir, 'readme_main_repository.rst'), 'w'
        ) as fd:
            fd.write(
                _c(
                    """
{{description}}
"""
                )
            )
        with open(os.path.join(self.templatedir, 'readme_main_ocb.rst'), 'w') as fd:
            fd.write(
                _c(
                    """
{{description}}
"""
                )
            )
        self.Z = z

    def setup(self, z0ctx):
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(self.Z.rundir, "scripts", "gen_readme.py"))

    def get_doc_path(self, odoo_path, gitorg):
        if gitorg == 'zero':
            doc_path = os.path.join(odoo_path, 'egg-info')
        else:
            doc_path = os.path.join(odoo_path, 'readme')
        if not os.path.isdir(doc_path):
            os.mkdir(doc_path)
        return doc_path

    def create_description_file(self, moduledir, odoo_version, gitorg):
        egg_info_path = self.get_doc_path(moduledir, gitorg)
        if gitorg == 'zero':
            descr_fn = os.path.join(egg_info_path, 'description.rst')
        else:
            descr_fn = os.path.join(egg_info_path, 'DESCRIPTION.rst')
        with open(descr_fn, 'w') as fd:
            fd.write(_c(DESCR_FN % odoo_version))

    def create_authors_file(self, moduledir, odoo_version, gitorg):
        egg_info_path = self.get_doc_path(moduledir, gitorg)
        if gitorg == 'zero':
            descr_fn = os.path.join(egg_info_path, 'authors.rst')
            with open(descr_fn, 'w') as fd:
                fd.write(_c(AUTHORS_FN % odoo_version))

    def create_contributors_file(self, moduledir, odoo_version, gitorg):
        egg_info_path = self.get_doc_path(moduledir, gitorg)
        if gitorg == 'zero':
            descr_fn = os.path.join(egg_info_path, 'contributors.rst')
        else:
            descr_fn = os.path.join(egg_info_path, 'CONTRIBUTORS.rst')
        with open(descr_fn, 'w') as fd:
            fd.write(_c(CONTRIBUTORS_FN % odoo_version))

    def test_01(self, z0ctx):
        sts = 0
        # home = os.path.expanduser('~')
        cmd = os.path.join(self.Z.rundir, 'gen_readme.py')
        gitorg = 'zero'
        for odoo_version in ODOO_VERSIONS:
            if not z0ctx['dry_run']:
                self.root = z0testodoo.build_odoo_env(z0ctx, odoo_version)
                odoo_root = os.path.join(self.root, odoo_version)
                repodir = z0testodoo.create_repo(
                    z0ctx, odoo_root, 'test_repo', odoo_version
                )
                moduledir = z0testodoo.create_module(
                    z0ctx, repodir, 'test_module', '%s.0.1.0' % odoo_version
                )
                self.create_description_file(moduledir, odoo_version, gitorg)
                self.create_authors_file(moduledir, odoo_version, gitorg)
                self.create_contributors_file(moduledir, odoo_version, gitorg)
                os.chdir(moduledir)
                # os.system('%s -B' % cmd)
                sts, stdout, stderr = z0lib.run_traced('%s -Bw .G %s' % (cmd, gitorg))
                if sts:
                    break


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )