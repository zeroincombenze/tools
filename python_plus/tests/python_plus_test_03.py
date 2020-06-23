# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Python-plus Regression Test Suite
"""
from __future__ import print_function, unicode_literals

# import pdb
import os
import os.path
import sys
import shutil
from zerobug import Z0BUG


MODULE_ID = 'python_plus'
TEST_FAILED = 1
TEST_SUCCESS = 0

__version__ = "0.1.4"


def version():
    return __version__


class Test():

    def __init__(self, zarlib):
        self.Z = zarlib

    def test_01(self, z0ctx):
        venv_dir = '%s/SAMPLE' % self.Z.testdir
        pyver = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        cmd = 'venv_mgr -q -p%s create %s' % (pyver, venv_dir)
        if not z0ctx['dry_run']:
            os.system(cmd)
        sts = self.Z.test_result(z0ctx,
                                 "%s" % cmd,
                                 True,
                                 os.path.isdir(venv_dir))
        for nm in ('bin', 'lib', 'include'):
            tgtdir = os.path.join(venv_dir, nm)
            sts += self.Z.test_result(z0ctx,
                                      "Check for %s" % tgtdir,
                                      True,
                                      os.path.isdir(tgtdir))
        #
        if os.path.isdir(venv_dir):
            shutil.rmtree(venv_dir)


if __name__ == "__main__":
    exit(Z0BUG.main_local(
        Z0BUG.parseoptest(
            sys.argv[1:],
            version=version()),
        Test))
