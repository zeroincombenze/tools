#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from builtins import input
import os
import sys
from babel.messages import pofile
from python_plus import _u, _b


def test_file_po(args):
    root_dir = args[0] if len(args) else os.getcwd()
    print('Checking for po file in %s' % root_dir)
    # import pdb
    # pdb.set_trace()
    for root, dirs, files in os.walk(root_dir):
        if os.path.basename(root) in (
                '.git', '__to_remove', 'doc', 'setup', '.idea'):
            continue
        # print('- examing %s ...' % root)
        if 'it.po' in files:
            po_fn = os.path.abspath(os.path.join(root, 'it.po'))
            print('-- Check for %s' % po_fn)
            with open(po_fn, 'r') as fd:
                wrong = False
                contents = _u(fd.read())
                if r'"Language: \n"' in contents:
                    contents = contents.replace(
                        r'"Language: \n"',
                        r'"Language: it\n"'
                    )
                    wrong = True
            if wrong:
                with open(po_fn, 'w') as fd:
                    fd.write(_b(contents))
            with open(po_fn, 'r') as fd:
                try:
                    catalog = pofile.read_po(fd)
                except BaseException as e:
                    print('*** File %s is unreadable\n%s' % (po_fn, e))
                    input('Press RET to continue ...')
                    continue
                for message in catalog:
                    if not message.id or not message.string:
                        continue
                    en_ctr = message.id.count(r'%')
                    it_ctr = message.string.count(r'%')
                    if en_ctr != it_ctr:
                        print('Wrong translation of "%s"->"%s"' % (
                            message.id, message.string
                        ))
                        input('Press RET to continue ...')
    return 0


if __name__ == "__main__":
    exit(test_file_po(sys.argv[1:]))