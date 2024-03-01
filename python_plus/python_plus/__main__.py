#!/home/odoo/devel/venv/bin/python2
# -*- coding: utf-8 -*-
"""z0bug
"""

from __future__ import print_function, unicode_literals

import os
import subprocess
import sys

from zerobug import Z0BUG

__version__ = "2.0.12"
STS_FAILED = 1
STS_SUCCESS = 0

if __name__ == "__main__":
    action = False
    if len(sys.argv) > 1:
        action = sys.argv[1]
    if action == '-h':
        print('%s [-h] [-H] [-T] [-V]' % Z0BUG.module_id)
        sys.exit(STS_SUCCESS)
    test_file = 'test_%s.py' % Z0BUG.module_id
    # gen_test_file = 'all_tests.py'
    if action == '-T' or (
        'DEV_ENVIRONMENT' in os.environ
        and os.environ['DEV_ENVIRONMENT'] == Z0BUG.module_id
    ):
        if os.path.isdir('./tests') and os.path.isfile(
            os.path.join('tests', test_file)
        ):
            os.chdir('./tests')
            sts = subprocess.call(test_file)
        elif os.path.isfile(test_file):
            sts = subprocess.call(test_file)
        else:
            sts = STS_FAILED
        sys.exit(sts)

    if action != '-H':
        print(__version__)
    if action != '-V':
        for text in __doc__.split('\n'):
            print(text)
    sys.exit(0)



