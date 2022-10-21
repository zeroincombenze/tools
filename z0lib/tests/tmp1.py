#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa - pylint: skip-file
import os

fn = os.path.join(os.path.dirname(__file__), 'tmp.py')
with open(fn, 'r') as fd:
    # tgt = 'C=\'"$TDIR"\'\\nD=\'"$HOME_DEVEL"\'\\n'
    tgt=''
    sts = 0
    for ln in fd.read().split('\n'):
        if ln.startswith('##'):
            sts = not sts
        elif ln.startswith('#') or 'pdb' in ln:
            continue
        elif ln.startswith('C='):
            tgt += 'C=a(\'"$TDIR"\')\\n'
        elif ln.startswith('D='):
            tgt += 'D=\'"$HOME_DEVEL"\'\\n'
        elif sts:
            tgt += '%s\\n' % ln
    tgt = tgt.replace('\\n\\n', '\\n')
    if tgt.startswith('\\n'):
        tgt = tgt[2:]
print(tgt)
