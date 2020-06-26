#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""zar
Zeroincombenze Archive Replica
"""

from __future__ import print_function,unicode_literals
import os
import sys
import subprocess

try:
    import z0testlib
    Z0BUG = z0testlib.Z0test()
except ImportError:
    from zerobug import Z0BUG


__version__ = '1.3.34'
STS_FAILED = 1
STS_SUCCESS = 0

if __name__ == "__main__":
    action = False
    if len(sys.argv) > 1:
        action = sys.argv[1]
    if action == '-h':
        print('%s [-h] [-H] [-T] [-V]' % Z0BUG.module_id)
        sys.exit(STS_SUCCESS)
    test_file = 'zerobug'
    if (action == '-T' or ('DEV_ENVIRONMENT' in os.environ and
            os.environ['DEV_ENVIRONMENT'] == Z0BUG.module_id)):
        if (os.path.isdir('./tests') and
                os.path.isfile(os.path.join('tests', test_file))):
            os.chdir('./tests')
            sts = subprocess.call(test_file)
        elif os.path.isfile(test_file):
            sts = subprocess.call(test_file)
        else:
            sts = STS_FAILED
        sys.exit(sts)

    if action != '-H':
        to_copy = False
        setup_file = './setup.py'
        if os.path.isfile('../setup.py') and os.path.isfile('./setup.py'):
            to_copy = True
            setup_file = '../setup.py'
        with open(setup_file, 'r') as fd:
            do_copy = False
            content = unicode(fd.read(), 'utf-8')
            for line in content.split('\n'):
                if line.find('version=') >= 0:
                    version = line.split('=')[1].strip()
                    if version[1:-2] == __version__:
                        print(version[1:-2])
                        do_copy = True
                    else:
                        print('Version mismatch %s/%s' % (version[1:-2],
                                                          __version__))
                    break
            if to_copy and do_copy:
                fd2 = open('./setup.py', 'w')
                fd2.write(content)
                fd2.close()
    if action != '-V':
        for text in __doc__.split('\n'):
            print(text)
    sys.exit(0)
