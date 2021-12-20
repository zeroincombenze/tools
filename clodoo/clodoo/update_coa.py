# flake8: noqa
# -*- coding: utf-8 -*-
# Import file library
import sys
# import os
import time
try:
    from clodoo import clodoo
except ImportError:
    import clodoo
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
        print text
        msg_time = time.time()


def get_company(ctx):
    model = 'res.company'
    ids = clodoo.searchL8(ctx, model, [('name', 'ilike', 'La Tua Azienda')])
    if not ids:
        ids = clodoo.searchL8(ctx, model, [('id', '>', 1)])
    if ids:
        return ids[0]
    else:
        return 1


def init_n_connect(flavour=None):
    title = 'Update Chart of Account'
    parser = z0lib.parseoptargs(title,
                                "© 2017-2018 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument("-c", "--config",
                        help="configuration command file",
                        dest="conf_fn",
                        metavar="file",
                        default='./import_partners.conf')
    parser.add_argument("-d", "--dbname",
                        help="DB name",
                        dest="db_name",
                        metavar="file",
                        default='')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    # Connect to DB
    ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    oerp, uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                                         db=ctx['db_name'],
                                         ctx=ctx)
    return oerp, uid, ctx


def get_company_account(ctx):
    company_id = ctx['company_id']
    ids = clodoo.searchL8(ctx, 'account.account',
                          [('code', '=', '0'),
                           ('company_id', '=', company_id)])
    if len(ids) != 1:
        print "Company account not found!"
        sys.exit(1)
    return ids[0]


def get_code_values(ctx, code):
    model = 'account.account'
    company_id = ctx['company_id']
    vals = {}
    vals['code'] = code
    root_id = get_company_account(ctx)
    vals['parent_id'] = root_id
    vals['company_id'] = company_id
    vals['type'] = 'view'
    ids = clodoo.searchL8(ctx, 'account.account.type',
                          [('code', '=', 'view')])
    if len(ids) == 0:
        print "Type view not found!"
        sys.exit(1)
    vals['user_type'] = ids[0]
    if code == 'A':
        vals['name'] = 'ATTIVITÀ'
    elif code == 'P':
        vals['name'] = 'PASSIVITÀ'
    elif code == 'R':
        vals['name'] = 'RICAVI'
        ids = clodoo.searchL8(ctx, model, [('code', '=', '__'),
                                           ('company_id', '=', company_id)])
        if len(ids) != 1:
            print "L&P account not found!"
            sys.exit(1)
        vals['parent_id'] = ids[0]
    elif code == 'S':
        vals['name'] = 'COSTI'
        ids = clodoo.searchL8(ctx, model, [('code', '=', '__'),
                                           ('company_id', '=', company_id)])
        if len(ids) != 1:
            print "L&P account not found!"
            sys.exit(1)
        vals['parent_id'] = ids[0]
    elif code == '__':
        vals['name'] = 'UTILE (-) O PERDITA (+) DI ESERCIZIO'
    else:
        print "Invalid account code %s" % code
        sys.exit(1)
    return vals


def update_coa(ctx):
    company_id = ctx['company_id']
    model = 'account.account'
    if len(clodoo.searchL8(ctx, model,
                           [('company_id', '=', company_id)])) < 100:
        return
    company = clodoo.browseL8(ctx, 'res.company', company_id)
    print "- Processing company %s" % company.name
    for code in ('__', 'A', 'P', 'R', 'S'):
        ids = clodoo.searchL8(ctx, model, [('code', '=', code),
                                           ('company_id', '=', company_id)])
        if len(ids) > 2:
            print "Warning: invalid account '%s'" % code
            sys.exit(1)
        elif ids:
            vals = get_code_values(ctx, code)
            try:
                clodoo.writeL8(ctx, model, ids[0], vals)
            except BaseException:
                pass
        else:
            vals = get_code_values(ctx, code)
            clodoo.createL8(ctx, model, vals)
    aprs = {}
    for code in ('__', 'A', 'P', 'R', 'S'):
        ids = clodoo.searchL8(ctx, model, [('code', '=', code),
                                           ('company_id', '=', company_id)])
        aprs[code] = ids[0]
    root_id = get_company_account(ctx)
    account_ids = clodoo.searchL8(ctx, model,
                                  [('type', '=', 'view'),
                                   ('parent_id', '=', root_id),
                                   ('id', 'not in', aprs.values())])
    for account_id in account_ids:
        ids = clodoo.searchL8(ctx, model, [('parent_id', '=', account_id)])
        if ids:
            account = clodoo.browseL8(ctx, model, ids[0])
            while account.type == 'view':
                ids = clodoo.searchL8(ctx, model, [('parent_id', '=', ids[0])])
                if ids:
                    account = clodoo.browseL8(ctx, model, ids[0])
                else:
                    account.type = 'asset'
            if account.user_type.code in ('asset', 'bank',
                                          'cash', 'receivable'):
                parent_id = aprs['A']
            elif account.user_type.code in ('equity', 'liability',
                                            'payable', 'tax'):
                parent_id = aprs['P']
            elif account.user_type.code == 'income':
                parent_id = aprs['R']
            elif account.user_type.code == 'expense':
                parent_id = aprs['S']
            else:
                parent_id = False
            if parent_id:
                vals = {}
                vals['parent_id'] = parent_id
                clodoo.writeL8(ctx, model, account_id, vals)


if __name__ == "__main__":
    # pdb.set_trace()
    oerp, uid, ctx = init_n_connect()
    print "Update Chart of Account on DB %s" % (ctx['db_name'])
    ids = clodoo.searchL8(ctx, 'res.company', [])
    for company_id in ids:
        ctx['company_id'] = company_id
        update_coa(ctx)
