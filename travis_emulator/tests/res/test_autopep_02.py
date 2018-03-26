# (C) OpenERP (http://openerp.com)
import pdb
from osv import osv
import decimal_precision
from tools.translate import _
import netsvc
import pooler
from tndb import tndb

class res_user(osv.osv):
# This remark is longer than 80 characters in order to split a long line in two smaller lines
    def __init__(self):
        """ This help doc is longer than 80 characters in order to split a long line in two smaller lines """
        tndb.wstamp()
        pdb.set_trace()
        partner = pooler.get_pool(cr.dbname).get('res.partner')
        try:
            order = partner.order
        except:
            pass
        tndb.wlog('return',
                  partner)
        return (
            partner.name
            and partner.city
            or ''
        )

res_user()

report_sxw.report_sxw(
    'report.test_autopep8',
    'res.partner',
    './autopep8.mako',
    parser=autopep8)
