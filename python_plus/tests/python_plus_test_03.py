# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Python-plus Regression Test Suite
"""
from __future__ import print_function, unicode_literals

import os
import os.path
import sys
import shutil
# from zerobug import Z0BUG


MODULE_ID = 'python_plus'
TEST_FAILED = 1
TEST_SUCCESS = 0

TEST_PYTHON = """
from z0lib import z0lib
parser = z0lib.parseoptargs("Test","(C) SHS-AV",version="1.2.3.4")
parser.add_argument('-h')
parser.add_argument('-V')
ctx = parser.parseoptargs(['-V'])
"""

__version__ = "1.0.3.1"


def version():
    return __version__


class Test():

    def __init__(self, zarlib):
        self.Z = zarlib
        self.venv_dir = '%s/SAMPLE' % self.Z.testdir

    def test_01(self, z0ctx):
        pyver = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        cmd = '%s/vem -qIf -p%s create %s' % (
            self.Z.rundir, pyver, self.venv_dir)
        if not z0ctx['dry_run']:
            os.system(cmd)
        sts = self.Z.test_result(z0ctx,
                                 "%s" % cmd,
                                 True,
                                 os.path.isdir(self.venv_dir))
        for nm in ('bin', 'lib'):
            tgtdir = os.path.join(self.venv_dir, nm)
            sts += self.Z.test_result(z0ctx,
                                      "Check for %s" % tgtdir,
                                      True,
                                      os.path.isdir(tgtdir))
        return sts

    def test_02(self, z0ctx):
        if not z0ctx['dry_run']:
            test_python = os.path.join(self.venv_dir, 'test.py')
            with open(test_python, 'w') as fd:
                fd.write(TEST_PYTHON)
            cmd = '%s/vem -qf %s install z0lib' % (
                self.Z.rundir, self.venv_dir)
            os.system(cmd)
            cmd = '%s/vem -qf %s exec "python %s"' % (
                self.Z.rundir, self.venv_dir, test_python)
            os.system(cmd)
        sts = 0
        return sts

    def test_09(self, z0ctx):
        if os.path.isdir(self.venv_dir):
            shutil.rmtree(self.venv_dir)


# if __name__ == "__main__":
#     exit(Z0BUG.main_local(
#         Z0BUG.parseoptest(
#             sys.argv[1:],
#             version=version()),
#         Test))
