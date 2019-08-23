# flake8: noqa
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
# import os
import time
import clodoo
try:
    from z0lib import z0lib
except ImportError:
    import z0lib
from pygments.lexers import sql
# import pdb


__version__ = "0.0.1.6"


msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print text
        msg_time = time.time()


def field_in_sql(field, i, STRUCT):
    if field in ('user', 'limit', 'references', 'default', 'group'):
        field = '"%s"' % field
    elif field != field.lower():
        field = '"%s"' % field
    type = STRUCT['type'][i]
    if type == 'numeric':
        if STRUCT['scale'][i]:
            sql = "    %s %s(%d,%d)" % (field,
                                        STRUCT['type'][i],
                                        STRUCT['precision'][i],
                                        STRUCT['scale'][i])
        elif STRUCT['precision'][i]:
            sql = "    %s %s(%d)" % (field,
                                     STRUCT['type'][i],
                                     STRUCT['precision'][i])
        else:
            sql = "    %s %s" % (field, STRUCT['type'][i])
    elif type in ('varchar', 'character varying'):
        if STRUCT['len'][i]:
            sql = "    %s %s(%d)" % (field,
                                     STRUCT['type'][i],
                                     STRUCT['len'][i])
        else:
            sql = "    %s %s" % (field, STRUCT['type'][i])
    elif type in ('timestamp', 'time'):
        sql = "    %s %s without time zone" % (field, STRUCT['type'][i])
    else:
        sql = "    %s %s" % (field, STRUCT['type'][i])
    if STRUCT['null'][i] == 'NO':
        sql += " NOT NULL"
    return sql


parser = z0lib.parseoptargs("Rebuild postgres DB from corrupt DB",
                            "© 2017-2018 by SHS-AV s.r.l.",
                            version=__version__)
parser.add_argument('-h')
parser.add_argument("-c", "--config",
                    help="configuration command file",
                    dest="conf_fn",
                    metavar="file",
                    default='./recover.conf')
parser.add_argument("-d", "--dbname",
                    help="DB name to create",
                    dest="new_db",
                    metavar="file",
                    default='test_cscs2016')
parser.add_argument('-n')
parser.add_argument("-o", "--olddb",
                    help="original DB",
                    dest="old_db",
                    metavar="file",
                    default='cscs2016')
parser.add_argument('-q')
parser.add_argument("-t", "--table",
                    help="table to select",
                    dest="sel_tbl",
                    metavar="file",
                    default='')
parser.add_argument('-V')
parser.add_argument('-v')
# Connect to DB
ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
oerp, uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                                     db=ctx['new_db'],
                                     ctx=ctx)
ctx['db_name'] = ctx['old_db']
cr_old = clodoo.psql_connect(ctx)
ctx['db_name'] = ctx['new_db']
cr_new = clodoo.psql_connect(ctx)
print "Recover DB %s from DB %s" % (ctx['new_db'], ctx['old_db'])

SCHEMA_NAME = 'public'
SCHEMA_SQL = "SELECT table_name FROM information_schema.tables " \
             "WHERE table_schema='%s'  and table_type<>'VIEW';"
COLUMN_SQL = "SELECT column_name,data_type,is_nullable,numeric_precision," \
             "numeric_scale,character_maximum_length " \
             "from information_schema.columns " \
             "where table_schema = '%s' and table_name='%s'"
COL_STRUCT = ('type', 'null', 'precision', 'scale', 'len')
query = SCHEMA_SQL % SCHEMA_NAME
OLD_TABLES = []
cr_old.execute(query)
for x in cr_old:
    OLD_TABLES.append(x[0])
NEW_TABLES = []
cr_new.execute(query)
for x in cr_new:
    NEW_TABLES.append(x[0])
for table in OLD_TABLES:
    print 'Analyzing %s ...' % table
    query = COLUMN_SQL % (SCHEMA_NAME, table)
    cr_old.execute(query)
    OLD_COLUMNS = []
    OLD_STRUCT = {}
    for n in COL_STRUCT:
        OLD_STRUCT[n] = []
    for x in cr_old:
        OLD_COLUMNS.append(x[0])
        for i, n in enumerate(COL_STRUCT):
            OLD_STRUCT[n].append(x[i + 1])
    if table not in NEW_TABLES:
        print '-- Table not exists in destination DB!'
        if table == 'account_analytic_analysis_summary_user':
            pass
        if table != table.lower():
            sql = 'CREATE TABLE "%s" ' % table
        else:
            sql = 'CREATE TABLE %s ' % table
        sep = '(\n'
        for i, field in enumerate(OLD_COLUMNS):
            sql += sep
            sep = ',\n'
            sql += field_in_sql(field, i, OLD_STRUCT)
        sql += ');\n'
        # print sql
        try:
            cr_new.execute(sql)
        except BaseException:
            print "SQL error"
            print sql
            raw_input('press RET to continue')
        continue
    cr_new.execute(query)
    NEW_COLUMNS = []
    for x in cr_new:
        NEW_COLUMNS.append(x[0])
    for x in OLD_COLUMNS:
        if x not in NEW_COLUMNS:
            print '-- Missed field %s ...' % x
