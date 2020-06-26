# content of test_server.py

import pytest
from zerobug import Z0BUG

__version__ = '0.2.15'

def test_version_zerobug(version_to_test):
    version_to_test(Z0BUG, __version__)


def test_version_z0testrc(version_to_test):
    version_to_test('z0testrc', __version__, mode='.')


class TestClass:

    def test_version_zerobug(self, version_to_test):
        version_to_test(Z0BUG, __version__)

    def test_version_z0testrc(self, version_to_test):
        version_to_test('z0testrc', __version__, mode='.')
