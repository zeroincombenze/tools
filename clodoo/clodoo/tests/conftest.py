# -*- coding: utf-8 -*-
# content of conftest.py

from subprocess import PIPE, Popen

import pytest

# from clodoo import transodoo


def pytest_report_header(config):
    return "project zerobug"


@pytest.fixture
def version_to_test():
    def get_version(cmd):
        res, err = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        res = res or err
        return res.split()[0].split('=')[-1].strip().strip('"').strip("'")

    def _version_to_test(package, version, mode=None):
        """check for version of module/package
        @package: pypi package or external command
        @version: version to test
        @mode may be:
            '' = use package.version() - This is the default mode
            '.' = use grep to find 1st occurrence of __version__=
            '-V' = exec 'package -V'
            '-v' = exec 'package -v'
            '--version' = exec 'package --version'
        """
        if mode and mode.startswith('-'):
            assert version == get_version([package, mode])
        elif mode == '.':
            assert version == get_version(['grep', '__version__', package])
        else:
            assert package.version() == version

    return _version_to_test
