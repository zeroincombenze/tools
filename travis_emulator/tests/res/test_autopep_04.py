from openerp.osv import fields, orm

class res_user(osv.osv):
    _columns = {
        'is_base': fields.boolean()
    }
