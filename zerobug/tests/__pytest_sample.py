# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future import standard_library

from builtins import object

from zerobug import Z0BUG

standard_library.install_aliases()  # noqa: E402


__version__ = '2.0.9'


def test_version_zerobug(version_to_test):
    version_to_test(Z0BUG, __version__)


def test_version_z0testrc(version_to_test):
    version_to_test('z0testrc', __version__, mode='.')


class TestClass(object):
    def test_version_zerobug(self, version_to_test):
        version_to_test(Z0BUG, __version__)

    def test_version_z0testrc(self, version_to_test):
        version_to_test('z0testrc', __version__, mode='.')
