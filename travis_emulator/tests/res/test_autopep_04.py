from openerp.osv import fields, orm

class res_user(osv.osv):
    _columns = {
        'id': fields.integer(),
        'is_base': fields.boolean(),
        'classification': fields.char(),
        'description': fields.text(),
        'architecture': fields.html(),
        'amount': fields.float(),
        'date_rec': fields.date(),
        'expire': fields.datetime(),
        'image': fields.binary(),
        'state': fields.selection(),
        'ref': fields.reference(),
        'inv_ids': fields.many2one(),
        'partner_id': fields.one2many(),
        'relation': fields.many2many(),
    }
