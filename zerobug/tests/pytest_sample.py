from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
# content of test_server.py

from future import standard_library
standard_library.install_aliases()                                 # noqa: E402
from builtins import *                                             # noqa: F403
from builtins import object

import pytest
from zerobug import Z0BUG

__version__ = '0.2.15.8'


def test_version_zerobug(version_to_test):
    version_to_test(Z0BUG, __version__)


def test_version_z0testrc(version_to_test):
    version_to_test('z0testrc', __version__, mode='.')


class TestClass(object):

    def test_version_zerobug(self, version_to_test):
        version_to_test(Z0BUG, __version__)

    def test_version_z0testrc(self, version_to_test):
        version_to_test('z0testrc', __version__, mode='.')
