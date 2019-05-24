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
from zerobug import Z0test

__version__ = "0.2.2.18"

MODULE_ID = 'maintainer-quality-tools'

TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest():

    def __init__(self, z0bug):
        self.Z = z0bug

    def test_01(self, z0ctx):
        sts = TEST_SUCCESS
        # call(cmd, stdin=stdinp_fd, stdout=stdout_fd, shell=True)
        # command = ['git', 'clone', '-q', url, '-b', branch,
        #    '--single-branch', '--depth=1', checkout_dir]
        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(Z0test.main_local(
        Z0test.parseoptest(
            sys.argv[1:],
            version=version()),
        RegressionTest))
