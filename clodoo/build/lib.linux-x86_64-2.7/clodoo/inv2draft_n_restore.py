#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017-2019, Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from __future__ import print_function       #, unicode_literals
import sys
try:
    from z0lib.z0lib import z0lib
except ImportError:
    from z0lib import z0lib
try:
    from clodoo import clodoo
except ImportError:
    import clodoo


__version__ = "0.3.55"


def get_name_by_ver(ctx, name):
    majver = ctx['majver']
    if name == 'move_name':
        if majver < 10:
            return 'internal_number'
    elif name == 'action_cancel_draft':
        if majver < 10:
            return 'action_invoice_draft'
    # TODO: delete following lines
    elif name == 'internal_number':
        if majver >= 10:
            return 'move_name'
    elif name == 'reference':
        if majver < 10:
            return 'supplier_invoice_number'
    elif name == 'supplier_invoice_number':
        if majver >= 10:
            return 'reference'
    return name


def upd_invoice(ctx, tmp_num=False, cur_num=False, cur_dt=False):
    move_name = get_name_by_ver(ctx, 'move_name')
    # reference = get_name_by_ver(ctx, 'reference')
    if not tmp_num and not cur_num:
        print(">> Missing parameters")
        return
    company_id = ctx['company_id']
    tmp_inv_id = False
    cur_inv_id = False
    if tmp_num:
        inv = clodoo.searchL8(ctx,
                              'account.invoice',
                              [('company_id', '=', company_id),
                               (move_name, '=', tmp_num)])
        if len(inv):
            tmp_inv_id = inv[0]
        else:
            return
        print(">>> tmp_inv=%d" % tmp_inv_id)
    if cur_num:
        inv = clodoo.search(ctx,
                            'account.invoice',
                            [('company_id', '=', company_id),
                             (move_name, '=', cur_num)])
        if len(inv):
            cur_inv_id = inv[0]
        else:
            return
        print(">>> cur_inv=%d" % cur_inv_id)
    if not tmp_inv_id and not cur_inv_id:
        print(">> No invoice found ", tmp_num, cur_num)
        return
    if tmp_inv_id:
        rec_ids = [tmp_inv_id]
        tag = tmp_num
    else:
        rec_ids = [cur_inv_id]
        tag = cur_num
    print(">> Get info tmp invoice %s (%s)" % (str(rec_ids), tag))
    reconcile_dict, move_dict = clodoo.get_reconcile_from_invoices(
        rec_ids, ctx)
    print(">> Unreconcile tmp invoice")
    clodoo.unreconcile_invoices(reconcile_dict, ctx)
    if tmp_inv_id and cur_inv_id and tmp_inv_id != cur_inv_id:
        print(">> Delete tmp invoice")
        try:
            clodoo.writeL8(ctx,
                           'account.invoice',
                           tmp_inv_id,
                           {'state': 'cancel',
                            'number': '', move_name: ''})
        except BaseException:                                # pragma: no cover
            pass
        clodoo.unlinkL8(ctx, 'account.invoice', [tmp_inv_id])
    if cur_inv_id:
        rec_ids = [cur_inv_id]
        tag = cur_num
    else:
        rec_ids = [tmp_inv_id]
        tag = tmp_num
    if cur_inv_id and tmp_inv_id and tmp_inv_id != cur_inv_id:
        print(">> Get info cur invoice %s (%s)" % (str(rec_ids), tag))
        reconcile_dict, move_dict = clodoo.get_reconcile_from_invoices(
            rec_ids, ctx)
        print(">> Unreconcile cur invoices")
        clodoo.unreconcile_invoices(reconcile_dict, ctx)
    print(">> Draft cur invoices")
    clodoo.upd_invoices_2_draft(move_dict, ctx)
    inv_id = rec_ids[0]
    vals = {}
    if cur_dt:
        dt_s = str(cur_dt)
        period_ids = clodoo.executeL8(ctx, 'account.period', 'find', dt_s)
        period_id = period_ids and period_ids[0] or False
        vals['date_invoice'] = dt_s
        vals['registration_date'] = dt_s
        vals['period_id'] = period_id
    if cur_num and tmp_num and tmp_num != cur_num:
        vals[move_name] = tmp_num
    if len(vals):
        print(">> Update values ", inv_id, vals)
        clodoo.writeL8(ctx, 'account.invoice', inv_id, vals)
    print(">> Posted")
    clodoo.upd_invoices_2_posted(move_dict, ctx)
    reconciles = reconcile_dict[inv_id]
    if len(reconciles):
        print(">> Reconcile ")
        cur_reconciles, cur_reconcile_dict = clodoo.refresh_reconcile_from_inv(
            inv_id, reconciles, ctx)
        clodoo.reconcile_invoices(cur_reconcile_dict, ctx)
    return


def set_type_of_id(id, list=None):
    if id == "":
        if list:
            return []
        else:
            return False
    elif id.isdigit():
        if list:
            return [int(id)]
        else:
            return int(id)
    else:
        try:
            return eval(id)
        except BaseException:                                # pragma: no cover
            if list:
                return []
            else:
                return False


def get_ids_from_params(model, company_id, P1=None, P2=None, P3=None):
    msg = "Dbg: search(%s [" % model
    if company_id:
        msg = msg + "(company_id, =, %s)," % company_id
    if P1:
        msg = msg + str(P1) + ','
    if P2:
        msg = msg + str(P2) + ','
    if P3:
        msg = msg + str(P3) + ','
    msg = msg + "]"
    print(msg)

    if P1 is False or P2 is False or P3 is False:
        return []
    where = []
    if company_id:
        where.append(('company_id', '=', company_id))
    if P1:
        where.append(P1)
    if P2:
        where.append(P2)
    if P3:
        where.append(P3)
    return clodoo.searchL8(ctx, model, where)


def set_where_str(name, value, condnot=False):
    if condnot:
        if not value:
            return value
        elif value.find('%') < 0:
            return (name, '!=', value)
        else:
            return (name, 'not ilike', value)
    else:
        if not value:
            return value
        elif value.find('%') < 0:
            return (name, '=', value)
        else:
            return (name, 'ilike', value)


def set_where_int(name, value, condnot=False):
    if isinstance(value, list) and len(value) == 0:
        return False
    elif condnot:
        if not value:
            return value
        elif isinstance(value, list):
            return (name, 'not in', value)
        else:
            return (name, '!=', value)
    else:
        if not value:
            return value
        elif isinstance(value, list):
            return (name, 'in', value)
        else:
            return (name, '=', value)


def get_ids_from_code(model, company_id, target):
    P1 = set_where_str('code', target)
    return get_ids_from_params(model, company_id, P1=P1)


def get_ids_from_name(model, company_id, target):
    where = []
    if company_id:
        where.append(('company_id', '=', company_id))
    if target.find('%') < 0:
        where.append(('name', '=', target))
    else:
        where.append(('name', 'like', target))
    return clodoo.searchL8(ctx, model, where)

def set_date_range(model, target):
    datas = target.split(':')
    P1 = P2 = None
    if datas[0]:
        P1 = ('date_invoice', '>=', datas[0])
    if len(datas) > 1 and datas[1]:
        P2 = ('date_invoice', '<=', datas[1])
    return get_ids_from_params(model, False, P1=P1, P2=P2)

def ask4company(company_id):
    msg = "Company ID (0=all, RET=%d)? " % company_id
    dummy = raw_input(msg)
    if dummy != "":
        company_id = int(dummy)
    return company_id


def ask4period(year):
    msg = "Year (0=all, RET=%d)? " % year
    dummy = raw_input(msg)
    if dummy != "":
        year = int(dummy)
    if year == 0:
        ids = None
    else:
        date_start = str(year) + "-01-01"
        date_stop = str(year) + "-12-31"
        model = 'account.period'
        ids = get_ids_from_params(model,
                                  False,
                                  P1=('date_start', '>=', date_start),
                                  P2=('date_stop', '<=', date_stop)
                                  )
    return year, ids


def ask4target(search_mode, target):
    print("Use prefix :A: to search for account")
    print("           :C: to search for account code")
    print("           :D: to search for date")
    print("           :I: to search for invoice id (default if number)")
    print("           :N: to search for invoice number (default if text)")
    print("           :P: to search for partner ID")
    print("Use number for id or [num,num,...] for ID(s)")
    print(" i.e. ':A:33' means search for invoices which have account id 33")
    print("  ':C:319%' search for invoices with account code like '319%'")
    print("  ':A:[4,6]' search for invoices which have account id in 4 or 6")
    print("  ':D:yyyy-mm-dd:yyy-mm-dd' date range")
    print("  '123' manage invoice which has ID 123")
    print("Press RET to send %s%s" % (search_mode, target))
    dummy = raw_input('Please, type [prefix]ID(s)/Number/Account? ')
    if dummy == "":
        dummy = search_mode + target
    return dummy


def print_invoice_info(inv_id):
    move_name = get_name_by_ver(ctx, 'move_name')
    model = 'account.invoice'
    try:
        inv_obj = clodoo.browseL8(ctx, model, inv_id)
        print("Id=%d, Num='%s'/'%s', supply n.='%s', ref='%s' cid=%d" % (
            inv_id,
            inv_obj.number,
            inv_obj[move_name],
            inv_obj[reference],
            inv_obj.name,
            inv_obj.company_id))
    except BaseException:
        print("Record not found!")


def print_move_info(inv_id):
    model = 'account.move'
    inv_obj = clodoo.browseL8(ctx, model, inv_id)
    print("Id=%d, name=%s cid=%d" % (
        inv_id,
        inv_obj.name,
        inv_obj.company_id))


parser = z0lib.parseoptargs("Set invoice status",
                            "© 2017-2019 by SHS-AV s.r.l.",
                            version=__version__)
parser.add_argument('-h')
parser.add_argument("-c", "--config",
                    help="configuration command file",
                    dest="conf_fn",
                    metavar="file",
                    default='./inv2draft_n_restore.conf')
parser.add_argument("-d", "--dbname",
                    help="DB name",
                    dest="db_name",
                    metavar="file",
                    default='demo')
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument('-V')
parser.add_argument('-v')
ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
uid, ctx = clodoo.oerp_set_env(ctx=ctx)
print("Invoice set Draft and Restore - %s" % __version__)


HDRDTL = {}
for search_mode in (':A:', ':C:', ':D:'):
    HDRDTL[search_mode] = 'D'
for search_mode in (':I:', ':N:', ':P:'):
    HDRDTL[search_mode] = 'H'


INVMOV = {}
for action in ('P', 'U', 'X'):
    INVMOV[action] = 'M'
for action in ('B', 'C', 'D', 'N', 'R', 'S', 'V'):
    INVMOV[action] = 'I'


MODEL = {'MH': 'account.move',
         'MD': 'account.move.line',
         'IH': 'account.invoice',
         'ID': 'account.invoice.line',
         'AC': 'account.account'}


STSNAME = {}
STSNAME['draft'] = {'MD': 'valid', 'MH': 'draft', 'IH': 'draft'}
STSNAME['cancel'] = {'IH': 'cancel'}


NM = {'M': 'name', 'I': 'number'}
search_mode = ""
target = ""
act2 = "?"
company_id = 0
year = 0
period_ids = []
move_name = get_name_by_ver(ctx, 'move_name')
reference = get_name_by_ver(ctx, 'reference')
while True:
    msg = "Cancel,Draft,Number,Quit,UnPublish,Replace,Sts,Validate,teXt,RB? "
    msg = msg + "[!?+] "
    action = raw_input(msg)
    if action == '':
        action = 'H'
    elif action != 'Q' and len(action) == 1:
        action = action + act2
    if action[0] not in ('B', 'C', 'D', 'N', 'P', 'R', 'S', 'U', 'V', 'X'):
        if action == 'Q':
            exit()
        print("Type B* for Bite: set state to draft and restore prior status")
        print("Type C* for Cancel: set state to draft and cancel number")
        print("Type D* for Draft: set state to draft (keep move_name)")
        print("Type N* for Number: set invoice to draft and ask for new number")
        print("Type P* for publish movements")
        print("Type S* for change invoice payment status")
        print("Type R* for Replace account in invoices")
        print("Type V* for validate invoices")
        print("Type X* for copy header reference into line")
        print("* may be ! or + or ?")
        print("? means do nothing")
        print("! means do action and end")
        print("+ means do action, ask for user and restore prior status"
              " (with reconciliation)")
        print("After S* command use:  1=Wait 2=ToPay 3=Sent 4=Rated")
        print("          5=Paid 6=Reconciled 7=Disputed 8=Cancelled")
        print("")
        print("Type RB to do last action Rollback")
        print("Rollback after action *! change action like *+")
        continue

    if action[0] == 'S':
        if len(action) == 3:
            inv_status = action[2]
        else:
            inv_status = ""
        if inv_status not in ('1', '2', '3', '4', '5', '6', '7', '8'):
            print("**** Invalid payment status ****")
            continue
    act2 = action[1]
    rec_ids = []
    if action != 'RB':
        target = ask4target(search_mode, target)
        company_id = ask4company(company_id)
        if target[0:3] in (':A:', ':C:', ':D:', ':I:', ':N:', ':P:'):
            search_mode = target[0:3]
            target = target[3:]
        elif target.isdigit():
            search_mode = ':I:'
        else:
            search_mode = ':N:'

        if search_mode == ':C:':
            account_id = get_ids_from_code(MODEL['AC'], company_id, target)
        elif search_mode == ':A:':
            account_id = set_type_of_id(target, list=True)
        elif search_mode == ':P:':
            partner_id = set_type_of_id(target)
        elif search_mode == ':D:':
            rec_ids = set_date_range('account.invoice', target)
        if search_mode in (':A:', ':C:', ':N:', ':P:'):
            year, period_ids = ask4period(year)
        invmov = INVMOV[action[0]]
        hdrdtl = HDRDTL[search_mode]
        actsrc = invmov + hdrdtl
        model_hdr = MODEL[invmov + 'H']
        model_dtl = MODEL[invmov + 'D']
        print("Dbg:(invmov=%s;hdrdtl=%s;actsrc=%s;models=%s/%s)" %
              (invmov, hdrdtl, actsrc, model_hdr, model_dtl))

        if search_mode == ':D:':
            pass
        elif search_mode == ':I:':
            rec_ids = set_type_of_id(target, list=True)
        else:
            if search_mode in (':A:', ':C:'):
                P1 = set_where_int('account_id', account_id)
            elif search_mode in (':P:', ):
                P1 = set_where_int('partner_id', partner_id)
            elif search_mode in (':N:', ):
                P1 = set_where_str(NM[invmov], target)
            else:
                P1 = None
            if actsrc != 'ID':
                P2 = set_where_int('period_id', period_ids)
            else:
                P2 = None
            P3 = None
            if action[0] in ('B', 'C', 'D', 'N'):
                sts2s = []
                if actsrc in STSNAME['cancel']:
                    sts2s.append(STSNAME['cancel'][actsrc])
                if action[0] != 'N' and actsrc in STSNAME['draft']:
                    sts2s.append(STSNAME['draft'][actsrc])
                if len(sts2s):
                    P3 = ('state', 'not in', sts2s)
            elif actsrc in STSNAME['draft']:
                P3 = ('state', '=', STSNAME['draft'][actsrc])
            if search_mode in (':A:', ':C:'):
                dtl_ids = get_ids_from_params(model_dtl,
                                              company_id,
                                              P1=P1,
                                              P2=P2,
                                              P3=P3)
                hdr_ids = []
                for id in dtl_ids:
                    if invmov == 'M':
                        idd = clodoo.browseL8(ctx, model_dtl, id).move_id.id
                    else:
                        idd = clodoo.browseL8(ctx, model_dtl, id).invoice_id.id
                    if idd not in hdr_ids:
                        hdr_ids.append(idd)
                if len(hdr_ids):
                    P1 = set_where_int('id', hdr_ids)
                    P2 = set_where_int('period_id', period_ids)
                    P3 = None
                    if action[0] == 'S' and invmov == 'I':
                        P3 = set_where_int('x_payment_status',
                                           inv_status,
                                           condnot=True)
                    elif action[0] in ('P', 'U', 'V', 'X'):
                        actsrc = actsrc[0] + 'H'
                        if actsrc in STSNAME['draft']:
                            if action[0] == 'U':
                                P3 = ('state', '!=', STSNAME['draft'][actsrc])
                            else:
                                P3 = ('state', '=', STSNAME['draft'][actsrc])
                    elif action[0] in ('B', 'C', 'D', 'N'):
                        actsrc = actsrc[0] + 'H'
                        sts2s = []
                        if actsrc in STSNAME['cancel']:
                            sts2s.append(STSNAME['cancel'][actsrc])
                        if action[0] != 'N' and actsrc in STSNAME['draft']:
                            sts2s.append(STSNAME['draft'][actsrc])
                        if len(sts2s):
                            P3 = ('state', 'not in', sts2s)
                    rec_ids = get_ids_from_params(model_hdr,
                                                  company_id,
                                                  P1=P1,
                                                  P2=P2,
                                                  P3=P3)
                else:
                    rec_ids = hdr_ids
            else:
                rec_ids = get_ids_from_params(model_hdr,
                                              company_id,
                                              P1=P1,
                                              P2=P2,
                                              P3=P3)
    # Now invoices contains IDs to manage
    if action == 'RB':
        fd = open('./inv2draft_n_restore.his', 'r')
        lines = fd.read().split('\n')
        STATES_2_DRAFT = ['open', 'paid', 'posted']
        rec_ids = []
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
                    rec_ids.append(inv_id)
                    if inv_id in reconciles:
                        reconcile_dict[inv_id] = reconciles[inv_id]
                        for state in moves:
                            if len(moves[state]):
                                move_dict[state] = list(set(move_dict[state]) |
                                                        set(moves[state]))
                    else:
                        print("**** Invalid rollback structure****")
                inv_id = int(line[4:])
                reconciles = {}
                moves = {}
            elif line[0:4] == '-   ':
                reconciles = eval(line[4:])
            elif line[0:4] == '--  ':
                moves = eval(line[4:])
        if inv_id:
            rec_ids.append(inv_id)
            if inv_id in reconciles:
                reconcile_dict[inv_id] = reconciles[inv_id]
                for state in moves:
                    if len(moves[state]):
                        move_dict[state] = list(set(move_dict[state]) |
                                                set(moves[state]))
            else:
                print("**** Invalid rollback structure****")
        fd.close()
    else:
        if len(rec_ids) == 0:
            print("No invoices(s)/movement(s) found!")
            continue
        if action[0] == 'R' and action != 'RB' and action[1] != '?':
            target_acc = raw_input('New account ID or :C:code? ')
            if target_acc[0:3] == ':C:':
                target_acc = target_acc[3:]
                new_account_id = get_ids_from_code(MODEL['AC'],
                                                   company_id,
                                                   target_acc)
                if len(new_account_id) != 1:
                    print("Invalid code replacement!")
                    continue
                new_account_id = new_account_id[0]
            else:
                try:
                    new_account_id = int(target_acc)
                except BaseException:                        # pragma: no cover
                    continue
        # print(rec_ids)
        for id in rec_ids:
            if action[0] in ('P', 'U', 'X'):
                print_move_info(id)
            else:
                print_invoice_info(id)
        res = raw_input('Press RET to process ..')
        if action[0] == 'V':
            reconcile_dict = rec_ids
            move_dict = {}
        elif action[0] in ('P', 'U', 'X'):
            pass
        else:
            print(">> Get info cur invoice %s" % str(rec_ids))
            reconcile_dict, move_dict = clodoo.get_reconcile_from_invoices(
                rec_ids, ctx)
            if action[1] != '?':
                print(">> Saving environment ..")
                fd = open('./inv2draft_n_restore.his', 'w')
                for inv_id in rec_ids:
                    fd.write('inv=%d\n-   %s\n--  %s\n' % (inv_id,
                                                           reconcile_dict,
                                                           move_dict))
                fd.close()
                print(">> Unreconcile cur invoices")
                clodoo.unreconcile_invoices(reconcile_dict, ctx)
                print(">> Draft cur invoices")
                clodoo.upd_invoices_2_draft(move_dict, ctx)
    if action[1] == '?':
        continue

    if action[0] == 'C':
        print(">> Cancel invoice number")
        for inv_id in rec_ids:
            print("Cancelling Invoice number of %d" % inv_id)
        clodoo.writeL8(ctx,
                       'account.invoice',
                       rec_ids,
                       {move_name: False})
    elif action[0] == 'N':
        for inv_id in rec_ids:
            print_invoice_info(inv_id)
            number = raw_input('New invoice number? ')
            clodoo.writeL8(ctx, MODEL['IH'], [inv_id],
                           {move_name: number})
    elif action[0] == 'R' and action != 'RB':
        for inv_id in rec_ids:
            print_invoice_info(inv_id)
            ids = get_ids_from_params(MODEL['ID'],
                                      company_id,
                                      P1=('invoice_id', '=', inv_id)
                                      )
            clodoo.writeL8(ctx, MODEL['ID'], ids,
                           {'account_id': new_account_id})
    elif action[0] == 'S':
        for inv_id in rec_ids:
            print_invoice_info(inv_id)
            clodoo.writeL8(ctx, MODEL['IH'], [inv_id],
                           {'x_payment_status': inv_status})
    elif action[0] == 'P':
        print(">> Posted")
        for move_id in rec_ids:
            print_move_info(move_id)
            clodoo.executeL8(ctx, 'account.move',
                             "button_validate",
                             [move_id])
    elif action[0] == 'U':
        for move_id in rec_ids:
            print_move_info(move_id)
        print(">> Draft")
        clodoo.upd_payments_2_draft(rec_ids, ctx)
    elif action[0] == 'X':
        for move_id in rec_ids:
            print_move_info(move_id)
            inv_obj = clodoo.browseL8(ctx, MODEL['MH'], move_id)
            ref = inv_obj.ref
            moves = clodoo.searchL8(ctx,
                                    MODEL['MD'],
                                    [('move_id', '=', move_id)])
            clodoo.write(ctx, MODEL['MD'], moves,
                         {'ref': ref})
    if action[0] == 'X' or (action[0] != 'B' and
                            action != 'RB' and action[1] != '+'):
        continue
    res = raw_input('Press RET to restore status ..')
    if action[0] == 'P':
        print(">> Draft")
        clodoo.upd_payments_2_draft(rec_ids, ctx)
    elif action[0] == 'U':
        print(">> Posted")
        clodoo.upd_payments_2_posted(rec_ids, ctx)
    else:
        for inv_id in rec_ids:
            try:
                clodoo.executeL8(ctx, 'account.invoice',
                                 "button_reset_taxes",
                                 [inv_id])
            except BaseException:                            # pragma: no cover
                pass
        print(">> Posted")
        clodoo.upd_invoices_2_posted(move_dict, ctx)
        if action[0] != 'V':
            print(">> Reconcile ")
            for inv_id in rec_ids:
                reconciles = reconcile_dict[inv_id]
                if len(reconciles):
                    try:
                        cur_reconciles, cur_reconcile_dict = \
                            clodoo.refresh_reconcile_from_inv(inv_id,
                                                              reconciles,
                                                              ctx)
                        clodoo.reconcile_invoices(cur_reconcile_dict,
                                                  ctx)
                    except BaseException:                    # pragma: no cover
                        print("**** Warning invoice %d ****" % inv_id)
                        print(reconciles)
