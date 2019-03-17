#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
# import oerplib
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
import pdb


__version__ = "0.3.8.10"


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
                    help="DB name to connect",
                    dest="db_name",
                    metavar="file",
                    default='')
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument('-V')
parser.add_argument('-v')
ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                               db=ctx['db_name'],
                               ctx=ctx)

model_grp = 'res.groups'
model_ctg = 'ir.module.category'
gid = True
while gid:
    gid = raw_input('Type res.groups id: ')
    if gid:
        gid = int(gid)
    if gid:
        group = clodoo.browseL8(ctx, model_grp, gid, context={'lang': 'en_US'})
        cid = group.category_id.id
        categ = clodoo.browseL8(ctx, model_ctg, cid, context={'lang': 'en_US'})
        print '%6d) Category %s' % (cid, categ.name)
        for id in clodoo.searchL8(ctx, model_grp, [('category_id', '=', cid)]):
            group = clodoo.browseL8(
                ctx, model_grp, id, context={'lang': 'en_US'})
            print '%6d) -- Value [%-16.16s] > [%s]' % (id,
                                                       group.name,
                                                       group.full_name)

model = 'ir.translation'
clodoo.unlinkL8(
    ctx, model, clodoo.searchL8(
        ctx, model, [('lang', '=', 'it_IT'),
                     '|',
                     ('name', '=', 'ir.module.module,description'),
                     ('name', '=', 'ir.module.module,shortdesc')]))
pdb.set_trace()
