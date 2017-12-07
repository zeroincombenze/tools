#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import pdb
from mysql import connector
import oerplib
# from os0 import os0

__version__ = "0.1.6"

try:
    fd = open('./load_cv.conf', 'r')
    lines = fd.read().split()
    for line in lines:
        tkn = line.split('=')
        if tkn[0] == 'my_user':
            MYUSER = tkn[1]
        elif tkn[0] == 'my_password':
            MYPWD = tkn[1]
        elif tkn[0] == 'my_dbname':
            MYDB = tkn[1]
        elif tkn[0] == 'oe_server':
            OESVR = tkn[1]
        elif tkn[0] == 'oe_user':
            OEUSER = tkn[1]
        elif tkn[0] == 'oe_dbname':
            OEDB = tkn[1]
        elif tkn[0] == 'oe_password':
            OEPWD = tkn[1]
        elif tkn[0] == 'oe_port':
            OEPORT = int(tkn[1])
        elif tkn[0] == 'oe_company':
            COMPANY_ID = int(tkn[1])
        elif tkn[0] == 'oe_project':
            PROJECT_ID = int(tkn[1])
    fd.close()
except BaseException:
    MYDB = raw_input('mysql database? ')
    MYUSER = raw_input('mysql username? ')
    MYPWD = raw_input('mysql password? ')
    OESVR = raw_input('odoo server? ')
    OEDB = raw_input('odoo database? ')
    OEUSER = raw_input('odoo username? ')
    OEPWD = raw_input('odoo password? ')
    OEPORT = raw_input('odoo port? ')
    COMPANY_ID = raw_input('odoo company id? ')
    PROJECT_ID = raw_input('odoo CV project id? ')
    fd = open('./load_cv.conf', 'w')
    fd.write('my_user=%s\n' % MYUSER)
    fd.write('my_password=%s\n' % MYPWD)
    fd.write('my_dbname=%s\n' % MYDB)
    fd.write('oe_server=%s\n' % OESVR)
    fd.write('oe_user=%s\n' % OEUSER)
    fd.write('oe_dbname=%s\n' % OEDB)
    fd.write('oe_password=%s\n' % OEPWD)
    fd.write('oe_port=%s\n' % OEPORT)
    fd.write('oe_company=%s\n' % COMPANY_ID)
    fd.write('oe_project=%s\n' % PROJECT_ID)
    fd.close()

cnx = connector.connect(user=MYUSER,
                        password=MYPWD,
                        database=MYDB)

oerp = oerplib.OERP(server=OESVR,
                    port=OEPORT,
                    version='7.0')
user_obj = oerp.login(user=OEUSER,
                      passwd=OEPWD,
                      database=OEDB)

FLDS_LIST = ('Number',
             'Firstname',
             'Surname',
             'Sex',
             'Nationality',
             'DatePlaceofBirth',
             'Language',
             'CountriesofExp',
             'DonorsClients',
             'KeyQualifications',
             'Education',
             'EmploymentHist',
             'Address',
             'Email',
             'Fax',
             'Phone',
             'Remarks',
             'file1',
             'file2',
             'file3',
             'file4',
             'file1_mimetype',
             'file2_mimetype',
             'file3_mimetype',
             'file4_mimetype',
             # 'file1_fulltext'
             )

cursor = cnx.cursor()
cursor.execute('select count(' + FLDS_LIST[0] + ') from ea')
my_field = cursor.next()
max_rec = my_field[0]
cursor.close()

cursor = cnx.cursor(buffered=False)
model = 'project.task'
sqlcmd = 'select'
sep = ' '
for field in FLDS_LIST:
    sqlcmd = sqlcmd + sep + field
    sep = ','
sqlcmd = sqlcmd + ' from ea'
cursor.execute(sqlcmd)
num_rec = 0
for my_field in cursor:
    num_rec += 1
    print "Evaluating %d of %s records " % (num_rec, max_rec)
    vals = {}
    vals['company_id'] = COMPANY_ID
    vals['project_id'] = PROJECT_ID
    for i, field in enumerate(my_field):
        name = FLDS_LIST[i]
        if name == 'file1_fulltext':
            oe_name = 'description'
        else:
            oe_name = 'cv_' + name.lower()
        if field:
            if isinstance(field, basestring):
                vals[oe_name] = field
                for i in range(17, 32):
                    vals[oe_name] = vals[oe_name].replace(unichr(i), ' ')
                for i in range(0, 9):
                    vals[oe_name] = vals[oe_name].replace(unichr(i), ' ')
            else:
                vals[oe_name] = field
            if name == 'Email':
                vals['user_email'] = field
    vals['name'] = vals.get('cv_firstname', '') + ' ' + \
        vals.get('cv_surname', '')
    vals['name'] = vals['name'].strip()
    if vals['name'] == '':
        vals['name'] = '# ' + str(vals['cv_number'])
    if 'cv_firstname' in vals:
        del vals['cv_firstname']
    if 'cv_surname' in vals:
        del vals['cv_surname']
    if 'description' in vals:               # debug
        vals['description'] = vals['description'].replace('\n\n', '\n')
        vals['description'] = vals['description'].replace('\n\n', '\n')
        description = vals['description'].replace('\n', '\\n')
        del vals['description']
    ids = oerp.search(model, [('company_id', '=', COMPANY_ID),
                              ('cv_number', '=', vals['cv_number'])])
    if len(ids):
        try:
            oerp.write(model, [ids[0]], vals)
        except BaseException:
            print vals['cv_number']
            print vals
        for id in ids[1:]:
            oerp.unlink(model, [id])
    else:
        try:
            oerp.create(model, vals)
        except BaseException:
            print vals['cv_number']
            print vals
cursor.close()
cnx.close()
