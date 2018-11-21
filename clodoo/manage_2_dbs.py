#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
# import oerplib
import clodoo
from z0lib import parseoptargs
import transodoo
# import pdb


__version__ = "0.1.1.1"

msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print text
        msg_time = time.time()


parser = parseoptargs("Manage 2 DBs",
                      "© 2017-2018 by SHS-AV s.r.l.",
                      version=__version__)
parser.add_argument('-h')
parser.add_argument("-c", "--left-config",
                    help="configuration command file",
                    dest="left_conf_fn",
                    metavar="file",
                    default='./inv2draft_n_restore.conf')
parser.add_argument("-d", "--left-db_name",
                    help="Database name",
                    dest="left_db_name",
                    metavar="name",
                    default='demo')
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument('-V')
parser.add_argument('-v')
parser.add_argument("-w", "--right-config",
                    help="configuration command file",
                    dest="right_conf_fn",
                    metavar="file",
                    default='./inv2draft_n_restore.conf')
parser.add_argument("-x", "--right-db_name",
                    help="Database name",
                    dest="right_db_name",
                    metavar="name",
                    default='demo')

left_ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
right_ctx = left_ctx.copy()
left_ctx['db_name'] = left_ctx['left_db_name']
left_ctx['conf_fn'] = left_ctx['left_conf_fn']
right_ctx['db_name'] = right_ctx['right_db_name']
right_ctx['conf_fn'] = right_ctx['right_conf_fn']
uid, right_ctx = clodoo.oerp_set_env(ctx=right_ctx)
uid, left_ctx = clodoo.oerp_set_env(ctx=left_ctx)
transodoo.read_stored_dict(right_ctx)
left_ctx['mindroot'] = right_ctx['mindroot']
