#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
Action may be:
- Dictionary (formerly Current)
- PO (formerly New)
- End
- Ignore
"""
from __future__ import print_function, unicode_literals
import os
import time
import re
import sys
import csv
import xlrd
from subprocess import PIPE, Popen
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


__version__ = "0.2.3.2"

MAX_RECS = 100
TNL_DICT = {}
TNL_ACTION = {}
SYNTAX = {
    'string': re.compile(u'"([^"\\\n]|\\.|\\\n)*"'),
}
msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print(text)
        msg_time = time.time()


def set_odoo_path(ctx, version):
    odoo_path = os.path.expanduser('~/%s' % version)
    if not os.path.exists(odoo_path):
        print('Paths of Odoo %s not found' % version)
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


def load_default_dictionary(ctx, source):

    def term_with_punct(row, msgid, punct):
        if msgid[-1] == punct:
            msg2 = os0.u(msgid[:-1])
            if row['msgstr'][-1] == punct:
                des2 = os0.u(row['msgstr'][:-1])
            else:
                des2 = os0.u(row['msgstr'])
        else:
            msg2 = os0.u(msgid + punct)
            if row['msgstr'][-1] == punct:
                des2 = os0.u(row['msgstr'])
            else:
                des2 = os0.u(row['msgstr']) + punct
        TNL_DICT[msg2] = des2
        TNL_ACTION[msg2] = 'D'

    def set_terms_n_punct(row, msgid):
        if msgid == '%s%s' % (msgid[0].upper(), msgid[1:].lower()):
            msg2 = os0.u(msgid.lower())
            TNL_DICT[msg2] = os0.u(row['msgstr']).lower()
            TNL_ACTION[msg2] = 'D'
            for punct in (':', '.'):
                term_with_punct(row, os0.u(row['msgstr']).lower(), punct)
        for punct in (':', '.'):
            term_with_punct(row, os0.u(row['msgstr']), punct)

    def process_row(ctx, row):
        if not row['status'] or row['status'] == ctx['module_name']:
            if not row['msgid'] or not row['msgstr']:
                return 0
            msgid = os0.u(row['msgid'])
            TNL_DICT[msgid] = os0.u(row['msgstr'])
            if msgid == TNL_DICT[msgid]:
                return 0
            try:
                if (msgid[0] != ' ' and
                        msgid[0] == TNL_DICT[msgid][0].lower() and
                        msgid[1:] == TNL_DICT[msgid][1:]):
                    return 0
            except BaseException:
                pass
            TNL_ACTION[msgid] = 'D'
            if ctx['action'] and ctx['action'][0].upper() in (
                    'D', 'P', '*'):
                TNL_ACTION[msgid] = ctx['action'][0].upper()
            set_terms_n_punct(row, msgid)
            return 1
        return 0

    def read_csv(ctx, source):
        ctr = 0
        if ctx['opt_verbose']:
            print("Reading %s into dictionary" % source)
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
        for row in csv_obj:
            if not hdr_read:
                hdr_read = True
                csv_obj.fieldnames = row['undef_name']
                continue
            ctr += process_row(ctx, row)
        if ctx['opt_verbose']:
            print(" ... Read %d records" % ctr)
        return ctr

    def read_xlsx(ctx, source):
        ctr = 0
        if ctx['opt_verbose']:
            print("Reading %s into dictionary" % source)
        wb = xlrd.open_workbook(source)
        sheet = wb.sheet_by_index(0)
        colnames = []
        for ncol in range(sheet.ncols):
            colnames.append(sheet.cell_value(0, ncol))
        for nrow in range(1, sheet.nrows):
            row = {}
            for ncol in range(sheet.ncols):
                row[colnames[ncol]] = sheet.cell_value(nrow, ncol)
            ctr += process_row(ctx, row)
        if ctx['opt_verbose']:
            print(" ... Read %d records" % ctr)
        return ctr

    ctr = 0
    if os.path.isfile(source + '.xlsx'):
        source = source + '.xlsx'
        ctr = read_xlsx(ctx, source)
    elif os.path.isfile(source + '.csv'):
        source = source + '.csv'
        ctr = read_csv(ctx, source)
    return ctr


def save_new_dictionary(ctx):

    def term_with_punct(TNL_DICT, msgid):
        punct = msgid[-1]
        msg2 = os0.b(msgid[:-1])
        if TNL_DICT[msgid][-1] == punct:
            des2 = os0.b(TNL_DICT[msgid][:-1])
        else:
            des2 = os0.b(TNL_DICT[msgid])
        return os0.b(''), msg2, des2

    dict_name = os.path.expanduser('~/odoo_default_tnl.csv')
    fd = open(dict_name, 'w')
    fd.write('status\tmsgid\tmsgstr\n')
    prior_msgid = ''
    for msgid in sorted(TNL_DICT.keys()):
        msg_burst(msgid)
        if msgid == TNL_DICT[msgid]:
            continue
        msg2 = '%s%s' % (msgid[0].upper(), msgid[1:].lower())
        if msgid == msgid.lower() and msg2 in TNL_DICT:
            continue
        if (msgid.endswith('.') or
                msgid.endswith(':')):
            if msgid[0: -1] == prior_msgid:
                continue
            fd.write(b'%s\t%s\t%s\n' % (
                term_with_punct(TNL_DICT, msgid)))
            prior_msgid = msgid[0: -1]
            continue
        fd.write(b'%s\t%s\t%s\n' % (
            b'', os0.b(msgid), os0.b(TNL_DICT[msgid])))
        prior_msgid = msgid
    fd.close()
    if ctx['opt_verbose']:
        print("New dictionary saved at %s" % dict_name)


def load_dictionary_from_file(ctx, pofn):
    ctr = 0
    if os.path.isfile(pofn):
        if ctx['opt_verbose']:
            print("Reading %s into dictionary" % pofn)
        catalog = pofile.read_po(open(pofn, 'r'))
        for message in catalog:
            msgid = message.id
            msgstr = message.string
            if msgid in TNL_DICT:
                if msgstr != TNL_DICT[msgid]:
                    print('  Duplicate key "%s"' % msgid)
                    print('    Dictionary="%s"' % TNL_DICT[msgid])
                    print('    Po="%s"' % msgstr)
                    dummy = ''
                    if '*' in TNL_ACTION:
                        dummy = TNL_ACTION['*']
                    elif msgid in TNL_ACTION:
                        dummy = TNL_ACTION[msgid]
                    while dummy not in ('D', 'P', 'E', 'I') and \
                            len(dummy) <= 3:
                        dummy = raw_input(
                            '>>> (Dictionary,Po,End,Ignore,<Text>)? ')
                    if dummy == 'E':
                        TNL_ACTION['*'] = dummy
                        return
                    elif dummy == 'I':
                        TNL_ACTION[msgid] = dummy
                        continue
                    elif len(dummy) >= 3:
                        TNL_DICT[msgid] = dummy
                        ctr += 1
                    elif dummy == 'P':
                        TNL_DICT[msgid] = msgstr
                        ctr += 1
                        print('       KEY="%s"' % msgstr)
                    else:
                        TNL_ACTION[msgid] = dummy
                else:
                    TNL_DICT[msgid] = msgstr
                    ctr += 1
        if ctx['opt_verbose']:
            print(" ... Read %d new records" % ctr)
    return ctr


def parse_pofile(ctx, source):
    if os.path.isfile(source):
        ctr = 0
        if ctx['opt_verbose']:
            print("Reading %s for upgrade" % source)
        fdiff = False
        catalog = pofile.read_po(open(source, 'r'))
        for message in catalog:
            msgid = os0.u(message.id)
            msgstr = os0.u(message.string)
            if msgid in TNL_DICT and msgstr != TNL_DICT[msgid]:
                for k, value in message.__dict__.iteritems():
                    if k == 'string':
                        message.string = TNL_DICT[msgid]
                    elif value:
                        setattr(message, k, value)
                ctr += 1
                fdiff = True
        if ctx['opt_verbose']:
            print(" ... %d records to update" % ctr)
        return fdiff, catalog
    return False, ''


def rewrite_pofile(ctx, pofn, target, version):
    if ctx['opt_verbose']:
        print("Writing %s " % pofn)
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


def load_dictionary(ctx):
    if ctx['dbg_template']:
        dict_name = os.path.expanduser('~/dev/pypi/tools/odoo_default_tnl')
    else:
        dict_name = os.path.expanduser('~/dev/odoo_default_tnl')
    ctr = load_default_dictionary(ctx, dict_name)
    ctx['pofiles'] = {}
    ctx['ctrs'] = {'0': ctr}
    if ctx['branch']:
        versions = [ctx['branch']]
    else:
        versions = ('13.0', '12.0', '11.0', '10.0', '9.0', '8.0', '7.0', '6.1')
    for version in versions:
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
                print('*** Module %s not found in Odoo %s !!!' % (
                    ctx['module_name'], version))
                continue
            print('Found path %s' % module_path)
            pofn = os.path.join(module_path, 'i18n', 'it.po')
            if not os.path.isfile(pofn):
                print('*** File %s not found !!!' % pofn)
                return 0
            ctx['pofiles'][version] = pofn
            ctr = load_dictionary_from_file(ctx, pofn)
            ctx['ctrs'][version] = ctr
    return 0


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
    for version in ctx['pofiles'].keys():
        pofn = ctx['pofiles'][version]
        fdiff, target = parse_pofile(ctx, pofn)
        if not fdiff:
            if ctx['opt_verbose']:
                print("No change done")
        else:
            rewrite_pofile(ctx, pofn, target, version)
    return 0


def upgrade_db(ctx):

    def write_tnl(ctx, model, ids, msgid, ctr):
        if ids and len(ids) < MAX_RECS:
            for id in ids:
                try:
                    clodoo.writeL8(ctx, model, id, {'value': TNL_DICT[msgid]})
                    ctr += 1
                except IOError as e:
                    print("*** Error %e writing '%s'!!!" % (e, TNL_DICT[msgid]))
                except BaseException as e:
                    print("*** Fatal error %s writing '%s'!!!" % (
                        e, TNL_DICT[msgid]))
                    clodoo.unlinkL8(ctx, model, id)
        return ctr

    for version in ctx['pofiles'].keys():
        ctr = 0
        dbname = ctx['db_prefix']
        if ctx['opt_verbose']:
            print("Upgrade DB %s" % dbname)
        xmlrpc_port = 8160 + int(version.split('.')[0])
        ctx['svc_protocol'] = ''
        db_found = False
        try:
            uid, ctx = clodoo.oerp_set_env(ctx=ctx,
                                           db=dbname,
                                           xmlrpc_port=xmlrpc_port,
                                           oe_version=version)
            db_found = True
        except BaseException:
            dbname = '%s%s' % (ctx['db_prefix'], version.split('.')[0])
        if not db_found:
            try:
                uid, ctx = clodoo.oerp_set_env(ctx=ctx,
                                               db=dbname,
                                               xmlrpc_port=xmlrpc_port,
                                               oe_version=version)
                db_found = True
            except BaseException:
                print("No DB %s found" % ctx['db_prefix'])
                return
        # ir.translation contains Odoo translation terms
        # @src: original (english) term
        # @source: evaluated field that seems a copy of src
        # @value: translated term
        # @name: is environment name; content may be:
        #   - type model: model name,field name
        #   - type code: source file name, format 'addons/MODULE_PATH'
        #   - type selection: MODULE_PATH,field name
        # @type: may be [code,constraint,model,selection,sql_constraint]
        # @module: module which added term
        # @state: may be [translated, to_translate]
        # @res_id: id of termm means:
        #   - type model: record id of model in name
        #   - type code: linenumber in source code (in name)
        # Report translations are in ir.ui.view model
        #
        model = 'ir.translation'
        # clodoo.unlinkL8(
        #     ctx, model, clodoo.searchL8(
        #         ctx, model, [('lang', '=', 'it_IT'),
        #                      ('name', 'in', ('ir.module.module,description'
        #                                      'ir.module.module,shortdesc',
        #                                      'ir.module.module,summary'))]))
        for msgid in TNL_DICT:
            msg_burst(msgid)
            ids = clodoo.searchL8(ctx, model,
                                  [('lang', '=', 'it_IT'),
                                   ('type', '=', 'model'),
                                   ('src', '=', msgid),
                                   ('module', '=', ctx['module_name']),
                                   ('value', '!=', TNL_DICT[msgid])])
            ctr = write_tnl(ctx, model, ids, msgid, ctr)
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
                 ('value', '!=', TNL_DICT[msgid])])
            ctr = write_tnl(ctx, model, ids, msgid, ctr)
        if ctx['opt_verbose']:
            print(" ... %d record upgraded" % ctr)
        if ctx['load_language']:
            clodoo.act_install_language(ctx)


def delete_translation(ctx):
    dbname = ctx['db_prefix']
    if ctx['opt_verbose']:
        print("Delete translation from DB %s" % dbname)
    version = ctx['branch']
    xmlrpc_port = 8160 + int(version.split('.')[0])
    ctx['svc_protocol'] = ''
    db_found = False
    try:
        uid, ctx = clodoo.oerp_set_env(ctx=ctx,
                                       db=dbname,
                                       xmlrpc_port=xmlrpc_port,
                                       oe_version=version)
        db_found = True
    except BaseException:
        dbname = '%s%s' % (ctx['db_prefix'], version.split('.')[0])
    if not db_found:
        try:
            uid, ctx = clodoo.oerp_set_env(ctx=ctx,
                                           db=dbname,
                                           xmlrpc_port=xmlrpc_port,
                                           oe_version=version)
            db_found = True
        except BaseException:
            print("No DB %s found" % ctx['db_prefix'])
            return 1
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
    parser.add_argument('-l', '--load-language',
                        action='store_true',
                        dest='load_language')
    parser.add_argument('-m', '--module_name',
                        action='store',
                        help='filename',
                        dest='module_name')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:])
    if not ctx['module_name']:
        print('*** Missing module name! Please, use -m switch !!!')
        sys.exit(1)
    if ctx['del_tnl']:
        sys.exit(delete_translation(ctx))
    sts = load_dictionary(ctx)
    if sts == 0:
        sts = parse_file(ctx)
    if sts == 0 and ctx['db_prefix']:
        sts = upgrade_db(ctx)
    if sts == 0:
        sts = save_new_dictionary(ctx)
    sys.exit(sts)
