#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
Action may be:
- Dictionary
- PO
- End
- Ignore
"""
from __future__ import print_function, unicode_literals
from builtins import input

import os
import time
import re
import sys
import csv
from subprocess import PIPE, Popen
# import xlrd
from openpyxl import load_workbook
from babel.messages import pofile
from os0 import os0
from python_plus import _c
try:
    from z0lib.z0lib import z0lib
except ImportError:
    from z0lib import z0lib
try:
    from clodoo import clodoo
except ImportError:
    import clodoo


__version__ = "1.0.4"

MAX_RECS = 100
PUNCT = [' ', '.', ',', '!', ':']
TNL_DICT = {}
TNL_ACTION = {}
SYNTAX = {
    'string': re.compile(u'"([^"\\\n]|\\.|\\\n)*"'),
}
VERSIONS = ('14.0', '13.0', '12.0', '11.0', '10.0', '9.0', '8.0', '7.0', '6.1')
PROTECT_TOKENS = [
    'Adviser',
    'Apply',
    'Approve',
    'Cancel',
    'Close',
    'Compute',
    'Confirm',
    'Cost of Revenue',
    'Create',
    'Currencies',
    'Currency',
    'Discard',
    'Display',
    'Dominica',
    'done', 'Done',
    'Export',
    'Kenya',
    'Journal',
    'Mauritania',
    'Myanmar',
    'Name',
    'Niger',
    'Partner', 'Partners',
    'Remove',
    'Report',
    'Run',
    'Save',
    'Set',
    'The rate of the currency to the currency of rate 1',
    'Uninstall',
    'Update',
    'You can either upload a file from your computer or copy/paste an internet link to your file',
]
msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print('\t', text)
        msg_time = time.time()


def set_odoo_path(ctx, version):
    if ctx['pofile']:
        return os.path.abspath(
            os.path.join(
                os.path.dirname(
                    ctx['pofile'].replace(ctx['branch'], version)), '..'))
    odoo_path = os.path.expanduser('~/%s' % version)
    if not os.path.exists(odoo_path):
        print('\tPaths of Odoo %s not found' % version)
        return False
    return odoo_path


def change_name(ctx, filename, version):
    filename = filename.replace(ctx['odoo_ver'], version)
    majver = int(ctx['odoo_ver'].split('.')[0])
    if majver >= 10:
        filename = filename.replace('/openerp/addons/', '/odoo/addons/')
    else:
        filename = filename.replace('/odoo/addons/', '/openerp/addons/')
    return filename


def term_wo_punct(msgid, msgstr):
    if msgid and msgid[-1] in PUNCT:
        if msgstr and msgstr[-1] == msgid[-1]:
            msgstr = msgstr[0: -1]
        msgid = msgid[0: -1]
    elif msgstr and msgstr[-1] in PUNCT:
        msgstr = msgstr[0: -1]
    if msgid and msgstr:
        caseid = 'U' if msgid[0].isupper() else 'l'
        casestr = 'U' if msgstr[0].isupper() else 'l'
        if len(msgid) > 1:
            caseid += 'U' if msgid[1].isupper() else 'l'
        if len(msgstr) > 1:
            casestr += 'U' if msgstr[1].isupper() else 'l'
        if casestr != casestr:
            if caseid == 'Ul' and casestr == 'll':
                msgstr = msgstr[0].upper() + msgstr[1:]
            elif caseid == 'll' and casestr == 'Ul':
                msgstr = msgstr[0].lower() + msgstr[1:]
    return msgid, msgstr


def term_with_punct(msgid, msgstr, punct):
    return msgid + punct, msgstr + punct


def load_default_dictionary(ctx, source):

    def process_row(ctx, module_rows, row):
        if isinstance(module_rows, list) and row['module']:
            if row['module'] == ctx['module_name']:
                module_rows.append(row)
            return 0
        if not row['msgid'] or not row['msgstr']:
            return 0
        msgid, TNL_DICT[msgid] = term_wo_punct(
            os0.u(row['msgid']), os0.u(row['msgstr']))
        if not TNL_DICT[msgid]:
            TNL_ACTION[msgid] = 'P'
            return 0
        elif (msgid == TNL_DICT[msgid] or (
                msgid[0] != ' ' and msgid[0] != '\n' and
                msgid[0] == TNL_DICT[msgid][0].lower() and
                msgid[1:] == TNL_DICT[msgid][1:])):
            TNL_ACTION[msgid] = '*'
            return 0
        if ctx['action'] and ctx['action'][0].upper() in (
                'D', 'P', '*'):
            TNL_ACTION[msgid] = ctx['action'][0].upper()
        else:
            TNL_ACTION[msgid] = 'D'
        return 1

    def read_csv(ctx, source):
        ctr = 0
        if ctx['opt_verbose']:
            print("\tReading %s into dictionary" % source)
        csv.register_dialect('dict',
                             delimiter=_c('\t'),
                             quotechar=_c('"'),
                             quoting=csv.QUOTE_MINIMAL)
        csv_fd = open(source, 'rU')
        hdr_read = False
        csv_obj = csv.DictReader(csv_fd,
                                 fieldnames=[],
                                 restkey='undef_name',
                                 dialect='dict')
        module_rows = []
        for row in csv_obj:
            if not hdr_read:
                hdr_read = True
                csv_obj.fieldnames = row['undef_name']
                continue
            ctr += process_row(ctx, module_rows, row)
        for row in module_rows:
            ctr += process_row(ctx, None, row)
        if ctx['opt_verbose']:
            print("\t... Read %d records" % ctr)
        return ctr

    def read_xlsx(ctx, source):
        ctr = 0
        if ctx['opt_verbose']:
            print("\tReading %s into dictionary" % source)
        # wb = xlrd.open_workbook(source)
        wb = load_workbook(source)
        # sheet = wb.sheet_by_index(0)
        for sheet in wb:
            break
        colnames = []
        # for ncol in range(sheet.ncols):
        for ncol in sheet.columns:
            # colnames.append(sheet.cell_value(0, ncol))
            colnames.append(ncol[0].value)
        module_rows = []
        # for nrow in range(1, sheet.nrows):
        hdr = True
        for nrow in sheet.rows:
            if hdr:
                hdr = False
                continue
            row = {}
            # for ncol in range(sheet.ncols):
            for ncol, cell in enumerate(nrow):
                # row[colnames[ncol]] = sheet.cell_value(nrow, ncol)
                row[colnames[ncol]] = cell.value
            ctr += process_row(ctx, module_rows, row)
        for row in module_rows:
            ctr += process_row(ctx, None, row)
        if ctx['opt_verbose']:
            print("\t... Read %d records" % ctr)
        return ctr

    ctr = 0
    if os.path.isfile(source + '.xlsx'):
        source = source + '.xlsx'
        ctr = read_xlsx(ctx, source)
    elif os.path.isfile(source + '.csv'):
        source = source + '.csv'
        ctr = read_csv(ctx, source)
    return ctr


def save_untranslated(ctx, untnl):
    csv.register_dialect('transodoo',
                         delimiter=_c(','),
                         quotechar=_c('\"'),
                         quoting=csv.QUOTE_MINIMAL)
    dict_name = os.path.expanduser('~/odoo_default_tnl.csv')
    with open(dict_name, 'wb') as fd:
        writer = csv.DictWriter(
            fd,
            fieldnames=('module', 'msgid', 'msgstr'),
            dialect='transodoo')
        writer.writeheader()
        if untnl is None:
            sorted_list = sorted(TNL_DICT.keys(), key=lambda x: x.lower())
        else:
            sorted_list = sorted(untnl, key=lambda x: x.lower())
        for item in sorted_list:
            msg_burst(item)
            line = {
                'module': '',
                'msgid': os0.b(item),
                'msgstr': '',
            }
            if untnl is None:
                line['msgstr'] = os0.b(TNL_DICT[item])
            if untnl is not None or (not item.startswith(' ') and
                                     not item.startswith('\n') and
                                     not item.startswith('===')):
                writer.writerow(line)
    if ctx['opt_verbose']:
        print("*** Untranslated dictionary saved at %s ***" % dict_name)


def translate_html(ctx, msgstr):
    return msgstr


def load_dictionary_from_file(ctx, pofn, def_action=None):
    ctr = 0
    trline = '-' * 60
    if os.path.isfile(pofn):
        if ctx['opt_verbose']:
            print("\tReading %s into dictionary" % pofn)
        catalog = pofile.read_po(open(pofn, 'r'))
        for message in catalog:
            if not message.id:
                continue
            msgid = message.id
            msgstr = message.string
            msgid2, msgstr2 = term_wo_punct(msgid, msgstr)
            if ctx['tnl_html']:
                msgstr = translate_html(ctx, msgstr)
            punct = '' if msgid == msgid2 else msgid[-1]
            if msgid2 not in TNL_DICT:
                TNL_DICT[msgid2] = msgstr2
                TNL_ACTION[msgid2] = 'P'
                ctr += 1
            elif msgstr2 != TNL_DICT[msgid2]:
                print('  Duplicate key "%s"' % msgid)
                print('    Dictionary="%s%s"' % (TNL_DICT[msgid2], punct))
                print('    %-60.60s' % trline)
                print('    Po="%s"' % msgstr)
                print('    %-60.60s' % trline)
                dummy = ''
                if msgid2 in PROTECT_TOKENS:
                    dummy = 'D'
                elif def_action:
                    dummy = def_action
                elif not msgstr:
                    dummy = 'D'
                elif not TNL_DICT[msgid2]:
                    dummy = 'P'
                elif msgid2 in TNL_ACTION:
                    dummy = TNL_ACTION[msgid2]
                elif '*' in TNL_ACTION:
                    dummy = TNL_ACTION['*']
                while dummy not in ('D', 'P', 'E', 'I') and \
                        len(dummy) <= 3:
                    dummy = input(
                        '>>> (Dictionary,Po,End,Ignore,<Text>)? ')
                if dummy == 'E':
                    TNL_ACTION['*'] = dummy
                    return
                elif dummy == 'I':
                    TNL_ACTION[msgid2] = dummy
                    continue
                elif len(dummy) >= 3:
                    TNL_DICT[msgid2] = os0.u(dummy)
                    ctr += 1
                elif dummy == 'P':
                    TNL_DICT[msgid2] = msgstr2
                    ctr += 1
                    print('       KEY="%s"' % msgstr)
                else:
                    TNL_ACTION[msgid2] = dummy
        if ctx['opt_verbose']:
            print("\t... Read %d new records" % ctr)
    return ctr


def parse_pofile(ctx, source, untnl):
    if os.path.isfile(source):
        ctr = 0
        if ctx['opt_verbose']:
            print("\tReading %s" % source)
        fdiff = False
        catalog = pofile.read_po(open(source, 'r'))
        for message in catalog:
            msgid = os0.u(message.id)
            msgstr = os0.u(message.string)
            msgid2, msgstr2 = term_wo_punct(msgid, msgstr)
            punct = ''
            if msgid and msgid[-1] in PUNCT:
                punct = msgid[-1]
                msgid, msgstr = term_with_punct(msgid, msgstr, punct)
            if not msgid:
                for k, value in message.__dict__.iteritems():
                    if k == 'string':
                        message.string = ''
                    elif value:
                        setattr(message, k, value)
                ctr += 1
            elif msgid2 in TNL_DICT and msgstr != TNL_DICT[msgid2]:
                for k, value in message.__dict__.iteritems():
                    if k == 'string':
                        message.string = TNL_DICT[msgid2] + punct
                    elif value:
                        setattr(message, k, value)
                ctr += 1
                fdiff = True
            elif msgid and msgid2 not in TNL_DICT and msgid2 not in untnl:
                if ctx['opt_verbose']:
                    print('\tWarning: key <%s> not found in translation!'
                          % msgid2)
                # untnl.append(msgid2)
                untnl[msgid2] = msgstr2
        if ctx['opt_verbose']:
            print("\t... %d records to update" % ctr)
        return fdiff, catalog, untnl
    return False, '', untnl


def rewrite_pofile(ctx, pofn, target, version):
    if ctx['opt_verbose']:
        print("\tWriting %s " % pofn)
    tmpfile = '%s.tmp' % pofn
    bakfile = '%s.bak' % pofn
    pofile.write_po(open(tmpfile, 'w'), target)
    cmd = ['makepo_it.py',
           '-b%s' % version,
           '-m%s' % ctx['module_name'],
           tmpfile]
    out, err = Popen(cmd,
                     stdin=PIPE,
                     stdout=PIPE,
                     stderr=PIPE,
                     shell=False).communicate()
    fd = open(pofn, 'rB')
    lefts = os0.u(fd.read()).split('\n')
    fd.close()
    fd = open(tmpfile, 'rB')
    rights = os0.u(fd.read()).split('\n')
    jj = 0
    for ii in range(len(lefts)):
        line = lefts[ii]
        if line[0:2] == '#.':
            while jj < len(rights) and rights[jj] != line:
                jj += 1
            if jj < len(rights) and rights[jj] == line:
                ii += 1
                while lefts[ii][0:2] == '#:':
                    jj += 1
                    rights.insert(jj, lefts[ii])
                    ii += 1
                jj += 1
    fd = open(tmpfile, 'w')
    fd.write(os0.b('\n'.join(rights)))
    fd.close()
    if os.path.isfile(bakfile):
        os.remove(bakfile)
    if os.path.isfile(pofn):
        os.rename(pofn, bakfile)
    os.rename(tmpfile, pofn)

def get_module_pofile_name(ctx, version):
    odoo_path = set_odoo_path(ctx, version)
    if odoo_path:
        module_path = False
        for root, dirs, files in os.walk(odoo_path):
            if (root.find('__to_remove') < 0 and
                    os.path.basename(root) == ctx['module_name'] and
                    (os.path.isfile(os.path.join(
                        root, '__manifest__.py')) or
                     os.path.isfile(os.path.join(
                         root, '__openerp__.py')))):
                module_path = root
                break
        if not module_path:
            print('*** Module %s not found for Odoo %s !!!' % (
                ctx['module_name'], version))
            return False
        print('Found path %s' % module_path)
        pofn = os.path.join(module_path, 'i18n', 'it.po')
        if not os.path.isfile(pofn):
            print('*** File %s not found !!!' % pofn)
            return False
        return pofn
    return False


def load_dictionary(ctx):
    if os.path.isdir(os.path.expanduser('~/devel')):
        root = os.path.expanduser('~/devel')
    elif os.path.isdir(os.path.expanduser('~/dev')):
        root = os.path.expanduser('~/dev')
    else:
        print('Development directory ~/devel not found!')
        return 1
    if ctx['dbg_template']:
        dict_name = os.path.join(root, 'pypi', 'tools', 'odoo_default_tnl')
    else:
        dict_name = os.path.join(root, 'odoo_default_tnl')
    ctr = load_default_dictionary(ctx, dict_name)
    ctx['pofiles'] = {}
    ctx['ctrs'] = {'0': ctr}
    for version in VERSIONS:
        if ctx['branch'] and version == ctx['branch'] and ctx['pofile']:
            pofn = ctx['pofile']
        else:
            pofn = get_module_pofile_name(ctx, version)
        if pofn:
            ctx['pofiles'][version] = pofn
            ctr = load_dictionary_from_file(ctx, pofn)
            ctx['ctrs'][version] = ctr
    return 0


def refresh_dictionary(ctx):
    if os.path.isdir(os.path.expanduser('~/devel')):
        root = os.path.expanduser('~/devel')
    elif os.path.isdir(os.path.expanduser('~/dev')):
        root = os.path.expanduser('~/dev')
    else:
        print('Development directory ~/devel not found!')
        return 1
    dict_name = os.path.join(root, 'pypi', 'tools', 'odoo_default_tnl')
    load_default_dictionary(ctx, dict_name)
    load_dictionary_from_file(ctx, ctx['ref_pofile'], def_action=ctx['action'])
    save_untranslated(ctx, None)


def set_header_pofile(ctx, pofile):
    polines = pofile.split('\n')
    potext = ''
    for line in polines:
        if line.startswith('"#\t*'):
            potext += r'"# %s\n"' % ctx['module_name'] + '\n'
        elif line.startswith('"# *'):
            potext += r'"# %s\n"' % ctx['module_name'] + '\n'
        elif line.startswith('"Project-Id-Version:'):
            potext += r'"Project-Id-Version: Odoo (%s)\n"' % ctx(
                'branch', '') + '\n'
        elif line.startswith('"Last-Translator:'):
            potext += r'"Last-Translator: %s <%s>\n"' % (
                'Antonio M. Vigliotti',
                'antoniomaria.vigliotti@gmail.com') + '\n'
        elif line.startswith('"Language-Team:'):
            potext += r'"Language-Team: %s (%s)\n"' % (
                'Zeroincombenze',
                'https://www.zeroincombenze.it/') + '\n'
            potext += r'"Language: it_IT\n"' + '\n'
        elif line.startswith('"Language:'):
            pass
        elif line.startswith('"language'):
            pass
        elif line.startswith('"Plural-Forms:'):
            potext += r'"Plural-Forms: nplurals=2; plural=(n != 1);\n"' + '\n'
        else:
            potext += line + '\n'
    return potext


def parse_file(ctx):
    # untnl = []
    untnl = {}
    for version in ctx['pofiles'].keys():
        pofn = ctx['pofiles'][version]
        fdiff, target, untnl = parse_pofile(ctx, pofn, untnl)
        src = '/%s/' % version
        tgt = '/oca%s/' % version.split('.')[0]
        oca_pofn = pofn.replace(src,tgt)
        if not os.path.isfile(oca_pofn):
            oca_pofn = oca_pofn.replace('einvoice', 'fatturapa')
        if os.path.isfile(oca_pofn):
            parse_pofile(ctx, pofn, untnl)
        if not fdiff:
            if ctx['opt_verbose']:
                print("No change done.")
        else:
            rewrite_pofile(ctx, pofn, target, version)
    save_untranslated(ctx, untnl)
    return 0


def connect_db(ctx):
    dbname = ''
    if ctx['branch']:
        version = ctx['branch']
        dbname = ctx['db_prefix']
        if ctx['opt_verbose']:
            print("\tUpgrade DB %s" % dbname)
        ctx['svc_protocol'] = ''
        db_found = False
        try:
            uid, ctx = clodoo.oerp_set_env(ctx=ctx,
                                           db=dbname,
                                           oe_version=version)
            db_found = True
        except BaseException:
            dbname = '%s%s' % (ctx['db_prefix'], version.split('.')[0])
        if not db_found:
            try:
                uid, ctx = clodoo.oerp_set_env(ctx=ctx,
                                               db=dbname,
                                               oe_version=version)
                db_found = True
            except BaseException:
                print("No DB %s found" % ctx['db_prefix'])
                dbname = ''
    return uid, ctx, dbname


def upgrade_db(ctx):

    def write_tnl(ctx, model, ids, msgid, msgstr, ctr):
        if ids and len(ids) < MAX_RECS:
            for id in ids:
                try:
                    clodoo.writeL8(ctx, model, id, {'value': msgstr})
                    ctr += 1
                except IOError as e:
                    print("*** Error %e writing '%s'!!!" % (e, msgstr))
                except BaseException as e:
                    print("*** Fatal error %s writing '%s'!!!" % (e, msgstr))
                    clodoo.unlinkL8(ctx, model, id)
        return ctr

    if ctx['branch']:
        uid, ctx, dbname = connect_db(ctx)
        if not dbname:
            return
        ctr = 0
        # ir.translation contains Odoo translation terms
        # @src: original (english) term
        # @source: evaluated field that seems a copy of src
        # @value: translated term
        # @name: is environment name; value may be:
        #   - type model: "model name,field name"
        #   - type code: "source file name", format 'addons/MODULE_PATH'
        #   - type selection: "MODULE_PATH,field name"
        # @type: may be [code,constraint,model,selection,sql_constraint]
        # @module: module which added term
        # @state: may be [translated, to_translate]
        # @res_id: id of term means:
        #   - type model: record id of model in name
        #   - type code: line number in source code (in name)
        # Report translations are in ir.ui.view model
        #
        model = 'ir.translation'
        # clodoo.unlinkL8(
        #     ctx, model, clodoo.searchL8(
        #         ctx, model, [('lang', '=', 'it_IT'),
        #                      ('name', 'in', ('ir.module.module,description'
        #                                      'ir.module.module,shortdesc',
        #                                      'ir.module.module,summary'))]))
        for msgid2 in TNL_DICT:
            for punct in PUNCT + ['']:
                msgid = msgid2 + punct
                msgstr = TNL_DICT[msgid2] + punct
                if ctx['opt_verbose']:
                    msg_burst(msgid)
                ids = clodoo.searchL8(ctx, model,
                                      [('lang', '=', 'it_IT'),
                                       ('type', '=', 'model'),
                                       ('src', '=', msgid),
                                       ('module', '=', ctx['module_name']),
                                       ('value', '!=', msgstr)])
                ctr = write_tnl(ctx, model, ids, msgid, msgstr, ctr)
                ids = clodoo.searchL8(
                    ctx, model,
                    [('lang', '=', 'it_IT'),
                     ('name', 'in', ('ir.actions.act_window,name',
                                     'ir.model,name',
                                     'ir.module.category,name',
                                     'ir.module.module,description'
                                     'ir.module.module,shortdesc',
                                     'ir.module.module,summary',
                                     'ir.ui.menu,name',
                                     'ir.ui.view,arch_db',
                                     )),
                     ('src', '=', msgid),
                     ('value', '!=', msgstr)])
                ctr = write_tnl(ctx, model, ids, msgid, msgstr, ctr)
        if ctx['opt_verbose']:
            print("\t... %d record upgraded" % ctr)
        if ctx['load_language']:
            clodoo.act_install_language(ctx)
    return 0


def delete_translation(ctx):
    uid, ctx, dbname = connect_db(ctx)
    if not dbname:
        return 0
    if ctx['opt_verbose']:
        print("\tDelete translation from DB %s" % dbname)
    model = 'ir.translation'
    clodoo.unlinkL8(
        ctx, model, clodoo.searchL8(
            ctx, model, [('lang', '=', 'it_IT'),
                         ('module', '=', ctx['module_name'])]))
    return 0


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Translate Odoo Package",
                                "© 2018-2020 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument("-A", "--action",
                        help="Action: Dict,Po,*",
                        dest="action",
                        metavar="name")
    parser.add_argument('-B', '--debug-template',
                        action='store_true',
                        dest='dbg_template')
    parser.add_argument("-b", "--branch",
                        help="Odoo branch",
                        dest="branch",
                        metavar="version")
    parser.add_argument("-c", "--config",
                        help="configuration file",
                        dest="conf_fn",
                        metavar="file",
                        default='./clodoo.conf')
    parser.add_argument('-D', '--delete-translation',
                        action='store_true',
                        dest='del_tnl')
    parser.add_argument("-d", "--dbname",
                        help="DB name",
                        dest="db_prefix",
                        metavar="dbname",
                        default='')
    parser.add_argument('-h')
    parser.add_argument('-H', '--translate-html',
                        action='store_true',
                        dest='tnl_html')
    parser.add_argument('-l', '--load-language',
                        action='store_true',
                        dest='load_language')
    parser.add_argument('-m', '--module_name',
                        action='store',
                        help='filename',
                        dest='module_name')
    parser.add_argument('-n')
    parser.add_argument('-p', '--pofile',
                        action='store',
                        help='pathname',
                        dest='pofile')
    parser.add_argument('-q')
    parser.add_argument('-R', '--ref-pofile',
                        action='store',
                        help='pathname',
                        dest='ref_pofile')
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:])
    if not ctx['module_name']:
        print('*** Missing module name! Please, use -m switch !!!')
        sys.exit(1)
    if ctx['del_tnl']:
        sys.exit(delete_translation(ctx))
    if ctx['ref_pofile']:
        sts = refresh_dictionary(ctx)
    else:
        sts = load_dictionary(ctx)
        if sts == 0:
            sts = parse_file(ctx)
        # if sts == 0 and ctx['db_prefix']:
        #     sts = upgrade_db(ctx)
    sys.exit(sts)
