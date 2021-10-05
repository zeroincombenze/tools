# flake8: noqa
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import clodoo
try:
    from z0lib import z0lib
except ImportError:
    import z0lib
# import pdb


__version__ = "0.2.1"


TRANSDICT = {
    0: 'ref',
    1: 'name',
    2: 'street',
    3: 'street2',
    4: 'zip',
    5: 'city',
    6: 'state_id',
    7: 'phone',
    8: 'mobile',
    10: 'vat',
    11: 'fiscalcode',
    12: 'email',
    13: 'comment',
    14: 'website',
    15: 'customer-supplier',
    17: 'name_first',
    18: 'name_last',
}


if __name__ == "__main__":
    # pdb.set_trace()
    flavour = 'servizigrafici'
    title = 'Import partners %s' % flavour or ''
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
                        default='demo8')
    parser.add_argument("-e", "--customer",
                        help="Import customers",
                        action="store_true",
                        dest="customers",
                        default=False)
    parser.add_argument("-f", "--filename",
                        help="Filename to import",
                        dest="csv_fn",
                        metavar="file",
                        default=False)
    parser.add_argument("-F", "--flavour",
                        help="Default CSV structure",
                        dest="flavour",
                        metavar="name",
                        default=flavour)
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument("-s", "--supplier",
                        help="Import suppliers",
                        action="store_true",
                        dest="suppliers",
                        default=False)
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    uid, ctx = clodoo.oerp_set_env(ctx=ctx)

    if not ctx['customers'] and not ctx['suppliers']:
        print "You must select customers and/or supplier"
        sys.exit(1)
    if not ctx['csv_fn']:
        if ctx['flavour']:
            sfx = '_'
        else:
            sfx = ''
        if ctx['customers']:
            ctx['csv_fn'] = 'customers%s%s.csv' % (sfx, ctx['flavour'] or '')
        else:
            ctx['csv_fn'] = 'suppliers%s%s.csv' % (sfx, ctx['flavour'] or '')

    print "Import data %s from %s on DB %s" % (ctx['flavour'],
                                               ctx['csv_fn'],
                                               ctx['db_name'])
    o_model = {'model': 'res.partner',
               'model_code': 'ref',
               'model_name': 'name',
               'hide_cid': False,
               }
    ctx['TRANSDICT'] = TRANSDICT
    ctx['MANDATORY'] = ['country_id', 'company_type', 'parent_id']
    ctx['TRX_VALUE'] = {
        'country_id': {'inghilterra': 'Regno Unito',
                       'Inghilterra': 'Regno Unito'}
    }
    ctx['EXPR'] = {
        'is_company': 'csv["CODICE CLIENTE"] != ""',
        'company_type':
            '"company" if csv["CODICE CLIENTE"] != "" else "person"',
        'parent_id':
            '"${header_id}" if csv["CODICE CLIENTE"] == "" else False',
    }
    ctx['DEFAULT'] = {}
    if ctx['customers']:
        ctx['DEFAULT']['customer'] = True
        ctx['MANDATORY'].append('customer')
    if ctx['suppliers']:
        ctx['DEFAULT']['supplier'] = True
        ctx['MANDATORY'].append('supplier')
    clodoo.import_file(ctx, o_model, ctx['csv_fn'])
