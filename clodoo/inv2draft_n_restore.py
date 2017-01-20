#!/usr/bin/env python
# -*- coding: utf-8 -*-
import oerplib
import clodoo


__version__ = "0.1.2"

oerp = oerplib.OERP()
try:
    fd = open('./inv2draft_n_restore.conf', 'r')
    lines = fd.read().split()
    for line in lines:
        tkn = line.split('=')
        if tkn[0] == 'login_user':
            user = tkn[1]
        elif tkn[0] == 'login_password':
            passwd = tkn[1]
        elif tkn[0] == 'db_name':
            database = tkn[1]
    fd.close()
except:
    database = raw_input('database? ')
    user = raw_input('username? ')
    passwd = raw_input('password? ')
uid = oerp.login(user=user,
                 passwd=passwd, database=database)
fd = open('./inv2draft_n_restore.conf', 'w')
fd.write('login_user=%s\n' % user)
fd.write('login_password=%s\n' % passwd)
fd.write('db_name=%s\n' % database)
fd.close()


def upd_invoice(ctx, tmp_num=False, cur_num=False, cur_dt=False):
    if not tmp_num and not cur_num:
        print ">> Missing parameters"
        return
    company_id = ctx['company_id']
    tmp_inv_id = False
    cur_inv_id = False
    if tmp_num:
        inv = oerp.search('account.invoice', [
                          ('company_id', '=', company_id),
                          ('internal_number', '=', tmp_num)])
        if len(inv):
            tmp_inv_id = inv[0]
        else:
            return
        print ">>> tmp_inv=%d" % tmp_inv_id
    if cur_num:
        inv = oerp.search('account.invoice', [
                          ('company_id', '=', company_id),
                          ('internal_number', '=', cur_num)])
        if len(inv):
            cur_inv_id = inv[0]
        else:
            return
        print ">>> cur_inv=%d" % cur_inv_id
    if not tmp_inv_id and not cur_inv_id:
        print ">> No invoice found ", tmp_num, cur_num
        return
    if tmp_inv_id:
        invoices = [tmp_inv_id]
        tag = tmp_num
    else:
        invoices = [cur_inv_id]
        tag = cur_num
    print ">> Get info tmp invoice %s (%s)" % (str(invoices), tag)
    reconcile_dict, move_dict = clodoo.get_reconcile_from_invoices(
        oerp, invoices, ctx)
    print ">> Unreconcile tmp invoice"
    clodoo.unreconcile_invoices(oerp, reconcile_dict, ctx)
    if tmp_inv_id and cur_inv_id and tmp_inv_id != cur_inv_id:
        print ">> Delete tmp invoice"
        try:
            oerp.write('account.invoice', tmp_inv_id, {
                       'state': 'cancel', 'number': '', 'internal_number': ''})
            pass
        except:
            pass
        oerp.unlink('account.invoice', [tmp_inv_id])
    if cur_inv_id:
        invoices = [cur_inv_id]
        tag = cur_num
    else:
        invoices = [tmp_inv_id]
        tag = tmp_num
    if cur_inv_id and tmp_inv_id and tmp_inv_id != cur_inv_id:
        print ">> Get info cur invoice %s (%s)" % (str(invoices), tag)
        reconcile_dict, move_dict = clodoo.get_reconcile_from_invoices(
            oerp, invoices, ctx)
        print ">> Unreconcile cur invoices"
        clodoo.unreconcile_invoices(oerp, reconcile_dict, ctx)
    print ">> Draft cur invoices"
    clodoo.upd_invoices_2_draft(oerp, move_dict, ctx)
    inv_id = invoices[0]
    vals = {}
    if cur_dt:
        dt_s = str(cur_dt)
        period_ids = oerp.execute('account.period', 'find', dt_s)
        period_id = period_ids and period_ids[0] or False
        vals['date_invoice'] = dt_s
        vals['registration_date'] = dt_s
        vals['period_id'] = period_id
    if cur_num and tmp_num and tmp_num != cur_num:
        vals['internal_number'] = tmp_num
    if len(vals):
        print ">> Update values ", inv_id,  vals
        oerp.write('account.invoice', inv_id, vals)
    print ">> Posted"
    clodoo.upd_invoices_2_posted(oerp, move_dict, ctx)
    reconciles = reconcile_dict[inv_id]
    if len(reconciles):
        print ">> Reconcile "
        cur_reconciles, cur_reconcile_dict = clodoo.refresh_reconcile_from_inv(
            oerp, inv_id, reconciles, ctx)
        clodoo.reconcile_invoices(oerp, cur_reconcile_dict, ctx)
    return


ctx = {}
ctx['level'] = 4
ctx['dry_run'] = False
company_id = 3
inv_id = raw_input('ID fattura? ')
if inv_id == "":
    exit()
inv_id = int(inv_id)
inv_obj = oerp.browse('account.invoice', inv_id)
print "Numb=%s, supply num=%s, ref=%s" % (inv_obj.number,
                                          inv_obj.supplier_invoice_number,
                                          inv_obj.name)
invoices = [inv_id]
print ">> Get info cur invoice %s" % str(invoices)
reconcile_dict, move_dict = clodoo.get_reconcile_from_invoices(
    oerp, invoices, ctx)
print ">> Unreconcile cur invoices"
clodoo.unreconcile_invoices(oerp, reconcile_dict, ctx)
print ">> Draft cur invoices"
clodoo.upd_invoices_2_draft(oerp, move_dict, ctx)
raw_input('Press RET to continue ...')
print ">> Posted"
clodoo.upd_invoices_2_posted(oerp, move_dict, ctx)
print ">> Reconcile "
reconciles = reconcile_dict[inv_id]
cur_reconciles, cur_reconcile_dict = clodoo.refresh_reconcile_from_inv(
    oerp, inv_id, reconciles, ctx)
clodoo.reconcile_invoices(oerp, cur_reconcile_dict, ctx)
