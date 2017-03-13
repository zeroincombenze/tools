#!/usr/bin/env python
# -*- coding: utf-8 -*-
import oerplib
import clodoo
# import pdb


__version__ = "0.1.5.8"

oerp = oerplib.OERP()
try:
    fd = open('./inv2draft_n_restore.conf', 'r')
    lines = fd.read().split('\n')
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


def set_type_of_id(id, list=None):
    if id == "":
        return False
    elif id.isdigit():
        if list:
            return [int(id)]
        else:
            return int(id)
    else:
        try:
            return eval(id)
        except:
            return False


def get_ids_from_params(model, company_id, P1=None, P2=None, P3=None):
    where = []
    if company_id:
        where.append(('company_id', '=', company_id))
    if P1:
        where.append(P1)
    if P2:
        where.append(P2)
    if P3:
        where.append(P3)
    return oerp.search(model, where)


def get_ids_from_code(model, company_id, target):
    where = []
    if company_id:
        where.append(('company_id', '=', company_id))
    if target.find('%') < 0:
        where.append(('code', '=', target))
    else:
        where.append(('code', 'like', target))
    return oerp.search(model, where)


def get_ids_from_name(model, company_id, target):
    where = []
    if company_id:
        where.append(('company_id', '=', company_id))
    if target.find('%') < 0:
        where.append(('name', '=', target))
    else:
        where.append(('name', 'like', target))
    return oerp.search(model, where)


def ask4company():
    company_id = raw_input('Company ID? ')
    if company_id == "":
        company_id = "0"
    company_id = int(company_id)
    return company_id


def ask4period():
    year = raw_input('Year? ')
    if year == "":
        return False
    year = int(year)
    date_start = str(year) + "-01-01"
    date_stop = str(year) + "-12-31"
    model = 'account.period'
    return get_ids_from_params(model,
                               False,
                               P1=('date_start', '>=', date_start),
                               P2=('date_stop', '<=', date_stop)
                               )


def ask4target():
    print "Use prefix :A: to search for account,"
    print "           :C: to search for account code"
    print "           :I: to search for invoice id (default if number)"
    print "           :N: to search for invoice number (default if text)"
    print "Use number for id or [num,num,...] for ID(s)"
    print " i.e. ':A:33' means search for invoices which have account id  33"
    print " ':C:3199%' search for invoices which have account code like 3199"
    print " 123 manage invoice which has ID 123"
    return raw_input('Please, type [prefix]ID(s)/Number/Account? ')


ctx = {}
ctx['level'] = 4
ctx['dry_run'] = False
print "Invoice set Draft and Restore - %s" % __version__
while True:
    msg = "Byte,Cancel[+],Draft,Help,Number[+],Quit,Replace[+],RB? "
    action = raw_input(msg)
    if action not in ('B', 'C', 'C+', 'D', 'N', 'N+', 'R', 'R+', 'RB'):
        if action == "Q":
            exit()
        print "Type B for Byte: set state to draft and restore prior status"
        print "Type C for Cancel: cancel number and set state to draft"
        print "Type C+ for same of Cancel but wait to restore prior status"
        print "Type D for Draft: set state to draft (keep internal_number)"
        print "Type N for Number: ask for new number (set invoice to draft)"
        print "Type N+ for same of Number but wait to restore prior status"
        print "Type R for Replace account in invoices (set invoice to draft)"
        print "Type R+ for same of Replace but wait to restore prior status"
        print "Type RB to do last action Rollback"
        print ""
        print "Action Byte, C+, N+ and R+ ask for user action,"
        print "then restore prior status (with reconciliation)"
        continue
    if len(action) == 1:
        action = action + "!"

    model = 'account.invoice'
    model0 = 'account.invoice.line'
    model1 = 'account.move'
    model2 = 'account.move.line'
    model3 = 'account.account'
    if action != 'RB':
        target = ask4target()
        company_id = ask4company()
        if target[0:3] == ":A:" or \
                target[0:3] == ":C:" or \
                target[0:3] == ":N:" or \
                target[0:3] == ":N:":
            search_mode = target[0:3]
            target = target[3:]
        elif target.isdigit():
            search_mode = ":I:"
        else:
            search_mode = ":N:"
        if search_mode == ":C:":
            account_id = get_ids_from_code(model3, company_id, target)
        elif search_mode == ":A:":
            account_id = set_type_of_id(target)
            if not account_id:
                continue
        if search_mode == ":C:" or search_mode == ":A:":
            period_ids = ask4period()
            print ">> Search for invoice with account"
            if isinstance(account_id, list):
                ids = get_ids_from_params(model0,
                                          company_id,
                                          # P1=('period_id', 'in', period_ids),
                                          P1=('account_id', 'in', account_id)
                                          )
            else:
                ids = get_ids_from_params(model0,
                                          company_id,
                                          # P1=('period_id', 'in', period_ids),
                                          P1=('account_id', '=', account_id)
                                          )
            invoices = []
            for id in ids:
                inv_line = oerp.browse(model0, id)
                inv_id = inv_line.invoice_id.id
                inv_obj = oerp.browse(model, inv_id)
                if inv_obj.period_id and \
                        inv_obj.period_id.id in period_ids and \
                        inv_id not in invoices:
                    invoices.append(inv_id)
        elif search_mode == ":N:":
            if isinstance(account_id, list):
                invoices = get_ids_from_params(model,
                                               company_id,
                                               P1=('number', '=', target)
                                               )
            else:
                invoices = get_ids_from_params(model,
                                               company_id,
                                               P1=('number', 'like', target)
                                               )
        else:
            invoices = set_type_of_id(target, list=True)
            if not invoices:
                continue

    # Now invoices contains IDs to manage
    if action == 'RB':
        fd = open('./inv2draft_n_restore.his', 'r')
        lines = fd.read().split('\n')
        STATES_2_DRAFT = ['open', 'paid', 'posted']
        invoices = []
        reconcile_dict = {}
        move_dict = {}
        for state in STATES_2_DRAFT:
            move_dict[state] = []
        inv_id = 0
        reconciles = {}
        moves = {}
        for line in lines:
            if line[0:4] == 'inv=':
                if inv_id:
                    invoices.append(inv_id)
                    reconcile_dict[inv_id] = reconciles
                    for state in moves:
                        if len(moves[state]):
                            move_dict[state] = list(set(move_dict[state]) |
                                                    set(moves[state]))
                inv_id = int(line[4:])
                reconciles = {}
                moves = {}
            elif line[0:4] == '-   ':
                reconciles = eval(line[4:])
            elif line[0:4] == '--  ':
                moves = eval(line[4:])
        if inv_id:
            invoices.append(inv_id)
            reconcile_dict[inv_id] = reconciles
            for state in moves:
                if len(moves[state]):
                    move_dict[state] = list(set(move_dict[state]) |
                                            set(moves[state]))
        fd.close()
    else:
        if len(invoices) == 0:
            print "Invoice number not found!"
            continue
        if action[0] == 'R' and action != 'RB':
            target = raw_input('New account ID or :C:code? ')
            if target[0:3] == ":C:":
                target = target[3:]
                new_account_id = get_ids_from_code(model3, company_id, target)
                if len(new_account_id) != 1:
                    print "Invalid code replacement!"
                    continue
                new_account_id = new_account_id[0]
            else:
                try:
                    new_account_id = int(target)
                except:
                    continue
        print ">> Get info cur invoice %s" % str(invoices)
        reconcile_dict, move_dict = clodoo.get_reconcile_from_invoices(
            oerp, invoices, ctx)
        print ">> Saving environment .."
        fd = open('./inv2draft_n_restore.his', 'w')
        for inv_id in invoices:
            fd.write('inv=%d\n-   %s\n--  %s\n' % (inv_id,
                                                   reconcile_dict,
                                                   move_dict))
        fd.close()
        print ">> Unreconcile cur invoices"
        clodoo.unreconcile_invoices(oerp, reconcile_dict, ctx)
        print ">> Draft cur invoices"
        clodoo.upd_invoices_2_draft(oerp, move_dict, ctx)

    if action[0] == 'C':
        print ">> Cancel invoice number"
        oerp.write('account.invoice', invoices, {'internal_number': ''})
    elif action[0] == 'N':
        for inv_id in invoices:
            inv_obj = oerp.browse(model, inv_id)
            print "Num=%s, supply n.=%s, ref=%s cid=%d" % (
                inv_obj.number,
                inv_obj.supplier_invoice_number,
                inv_obj.name,
                inv_obj.company_id)
            number = raw_input('New invoice number? ')
            oerp.write(model, [inv_id],
                       {'internal_number': number})
    elif action[0] == 'R' and action != 'RB':
        # pdb.set_trace()
        for inv_id in invoices:
            inv_obj = oerp.browse(model, inv_id)
            print "Num=%s, supply n.=%s, ref=%s cid=%d" % (
                inv_obj.number,
                inv_obj.supplier_invoice_number,
                inv_obj.name,
                inv_obj.company_id)
            ids = get_ids_from_params(model0,
                                      company_id,
                                      P1=('invoice_id', '=', inv_id)
                                      )
            oerp.write(model0, ids,
                       {'account_id': new_account_id})
    if action[0] != 'N' and action[0] != 'R' and action != 'RB':
        for inv_id in invoices:
            inv_obj = oerp.browse(model, inv_id)
            print "Num=%s, supply n.=%s, ref=%s cid=%d" % (
                inv_obj.number,
                inv_obj.supplier_invoice_number,
                inv_obj.name,
                inv_obj.company_id)
    if action != 'B' and action != 'RB' and action[1] != '+':
        continue
    res = raw_input('Press RET to continue ..')
    for inv_id in invoices:
        try:
            oerp.execute('account.invoice',
                         "button_reset_taxes",
                         [inv_id])
        except:
            pass
    print ">> Posted"
    clodoo.upd_invoices_2_posted(oerp, move_dict, ctx)
    print ">> Reconcile "
    for inv_id in invoices:
        reconciles = reconcile_dict[inv_id]
        try:
            cur_reconciles, cur_reconcile_dict = \
                clodoo.refresh_reconcile_from_inv(oerp,
                                                  inv_id,
                                                  reconciles,
                                                  ctx)
            clodoo.reconcile_invoices(oerp, cur_reconcile_dict, ctx)
        except:
            print "**** Warning invoice %d ****" % inv_id
            print reconciles
