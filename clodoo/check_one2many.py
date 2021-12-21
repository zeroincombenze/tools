#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
# import oerplib
# from os0 import os0
try:
    from clodoo import clodoo
except ImportError:
    import clodoo
try:
    from z0lib.z0lib import z0lib
except ImportError:
    try:
        from z0lib import z0lib
    except ImportError:
        import z0lib
# import pdb


__version__ = "0.3.55"
msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print(text)
        msg_time = time.time()


parser = z0lib.parseoptargs("Odoo test environment",
                            "© 2017-2018 by SHS-AV s.r.l.",
                            version=__version__)
parser.add_argument('-h')
parser.add_argument("-c", "--config",
                    help="configuration command file",
                    dest="conf_fn",
                    metavar="file",
                    default='./inv2draft_n_restore.conf')
parser.add_argument("-d", "--dbname",
                    help="DB name",
                    dest="db_name",
                    metavar="file",
                    default='demo')
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument('-V')
parser.add_argument('-v')
ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
oerp, uid, ctx = clodoo.oerp_set_env(ctx=ctx)

# pdb.set_trace()
model_fld = 'ir.model.fields'
for fld_id in oerp.search(model_fld, [('ttype', '=', 'one2many')]):
    try:
        fld = oerp.browse(model_fld, fld_id)
        print('browse(%s, %d){"name":%s, "model_id":%s,'
              ' "relation":%s, "relation_field":%s}' % (model_fld,
                                                        fld_id,
                                                        fld.name,
                                                        fld.model_id.model,
                                                        fld.relation,
                                                        fld.relation_field))
        with open('check_one2many.log', 'ab') as log:
            log.write("browse(%s, %d)\n" % (model_fld, fld_id))
        model2 = fld.model_id.model
        for id in oerp.search(model2):
            msg_burst(' - browse(%s, %d).%s' % (model2, id, fld.name))
            try:
                rec = oerp.browse(model2, id)
                for kk in rec[fld.name]:
                    msg_burst('search(%s, id=%d)' % (fld.relation, kk.id))
                    try:
                        x = oerp.search(fld.relation, [('id', '=', kk.id)])
                    except BaseException:
                        x = []
                    if len(x) != 1:
                        with open('check_one2many.log', 'ab') as log:
                            log.write("**** Error in model %s id %d! ****\n" %
                                      (fld.relation, kk.id))
            except BaseException:
                print("**** Error in model %s id %d! ****" % (model2, id))
                with open('check_one2many.log', 'ab') as log:
                    log.write("**** Error in model %s id %d! ****\n" % (model2,
                                                                        id))
    except BaseException:
        print("**** Error in model %s id %d! ****" % (model_fld, fld_id))
        with open('check_one2many.log', 'ab') as log:
            log.write("**** Error in model %s id %d! ****\n" % (model_fld,
                                                                fld_id))
