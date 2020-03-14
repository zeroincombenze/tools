#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
Zeroincombenze® Maintainer Quality Tools

Maintainer Quality Tools or MQT is a module created by OCA to provide helpers
to ensure the quality of Odoo addons.
More info are avaiable at:
<https://github.com/zeroincombenze/tools/tree/master/maintainer-quality-tools>

MQT is execute inside TravisCI environment. Tests to validate MQT are
themselves executed in TravisCI environment, so filesystem tree is (when you
read 'by TRavisCI' means both TravisCI both local travis-emulator):

    ${HOME}
    |
    \___ build (by TravisCI)
    |    |
    |    \___ ${TRAVIS_BUILD_DIR}  (by TravisCI}
    |    |    # github tested project (during this test is <tools>)
    |    |
    |    \___ ${ODOO_REPO} (during this test is <OCA/OCB>
    |
    \___ maintainer-quality-tools (this module under test)
    |    |
    |    \___ travis (child of maintainer-quality-tools), in PATH
    |
    \___ ${ODOO_REPO}-${VERSION} (during this test is OCA-10.0)
    |    # symlnk of ${HOME}/build/{ODOO_REPO}
    |
    \___ dependencies
    |    # Odoo dependencies (2)
    |
    \___ tools (by .travis.yml)   # clone of this project
         |
         \___ maintainer-quality-tools (child of tools)
              # moved to ${HOME}/maintainer-quality-tools 
"""

# import pdb
import os
import sys
import shutil
from zerobug import Z0test

__version__ = "0.2.2.43"

MODULE_ID = 'maintainer-quality-tools'

TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest():

    def __init__(self, z0bug):
        self.Z = z0bug
        for f in ('getaddons', 'test_server', 'git_run', 'travis_helpers'):
            shutil.copy('../travis/%s.py' % f, './')

    def test_01(self, z0ctx):
        import test_server
        sts = TEST_SUCCESS
        tres = True
        res = True
        for repo in ('odoo/odoo', 'OCA/OCB', 'zeroincombenze/OCB'):
            for ver in ('6.1', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0'):
                if not z0ctx['dry_run']:
                    res = test_server.get_server_path(
                        repo,
                        ver,
                        os.path.join(z0ctx['testdir'], 'res'))
                    tres = os.path.join(
                        z0ctx['testdir'],
                        'res',
                        '%s-%s' % (repo.split('/')[1], ver))
                sts = self.Z.test_result(
                    z0ctx,
                    'get_server_path(%s,%s)' % (repo, ver),
                    tres,
                    res)
        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(Z0test.main_local(
        Z0test.parseoptest(
            sys.argv[1:],
            version=version()),
        RegressionTest))
