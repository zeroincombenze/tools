from openerp.tests.common import TransactionCase


class TestUser(TransactionCase):

    def setUp(self):
        super(TestUser, self).setUp()
        self.res_user = self.env['res.user']
        self.myname = self.res_user.search(
            [('name', '=', 'Me')]).name
        self.m1 = self.res_user.create({'name': self.env.ref('base.it').id})
