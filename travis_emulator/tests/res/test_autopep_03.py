# import pdb
from openerp.osv import osv
import openerp.addons.decimal_precision
from openerp.tools.translate import _
from openerp import netsvc
from openerp import pooler
# from tndb import tndb

const1 = 10
const2 = 20

class res_user(osv.osv_memory):
    def __init__(self, ctx=None):
        if ctx is None:
            ctx = {}
        # tndb.wstamp()
        # pdb.set_trace()
        partner = pooler.get_pool(cr.dbname).get('res.partner')
        # tndb.wlog('return',
        #           partner)
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
