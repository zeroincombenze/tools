#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
     Prototypes builder
     Creates prototype files for a new module named 'prototypes'.
     Run as schell script, not as web application (see 1.st line in this file)

"""

# import pdb
import argparse
import ConfigParser


_version = "V0.1.0"


class Builder():

    def __init__(self):
        pass

    def list_paths(self, prm):
        self.get_odoo_conf(prm)
        for i, p in enumerate(self.odoo_math):
            print i, p

    def install_new_module(self, prm):
        self.get_odoo_conf(prm)
        if len(self.odoo_math) == 1:
            prm['module_path'] = self.odoo_math[0]
        elif prm['sel_path']:
            prm['module_path'] = self.odoo_math[prm['sel_path']]
        else:
            print('Invalid pathname for module {0}!'.format(prm['modname']))
            print('  use --path option')
            return
        print ('Module {0}->{1}'.format(prm['modname'],
                                        prm['module_path']))

    def get_odoo_conf(self, prm):
        if 'odoo_conf' in prm:
            odoo_conf = prm['odoo_conf']
        else:
            odoo_conf = "/etc/openerp-server.conf"
        odoo_cfg_obj = ConfigParser.SafeConfigParser()
        s = "options"
        if not odoo_cfg_obj.has_section(s):
            odoo_cfg_obj.add_section(s)
        odoo_cfg_obj.read(odoo_conf)
        mpath = odoo_cfg_obj.get(s, "addons_path")
        self.odoo_math = mpath.split(',')
        return odoo_cfg_obj

    def mkdir(self, prm):
        # modname = prm['modname']
        self.get_odoo_conf(prm)

Builder()


def main():
    parser = argparse.ArgumentParser(
        description="Zeroincombenze® Odoo Module Builder.",
        epilog="© 2015 by SHS-AV s.r.l."
               " - http://www.zeroincombenze.it",
        argument_default=argparse.SUPPRESS)

    parser.add_argument("-i", "--install",
                        help="module paths",
                        action="store_true",
                        dest="o_install",
                        default=False)
    parser.add_argument("-l", "--list",
                        help="module paths",
                        action="store_true",
                        dest="o_list",
                        default=False)
    parser.add_argument("-n", "--name",
                        help="module name",
                        dest="modname",
                        metavar="name",
                        default="midea")
    parser.add_argument("-p", "--path",
                        help="select path number",
                        dest="sel_path",
                        metavar="int",
                        default=None)
    parser.add_argument("-V", "--version",
                        action="version",
                        version="%(prog)s " + _version)
    opt_obj = parser.parse_args()
    prm = {}
    prm['modname'] = opt_obj.modname
    prm['action'] = 'help'
    prm['sel_path'] = False
    if opt_obj.o_list:
        prm['action'] = 'list'
    elif opt_obj.o_install:
        prm['action'] = 'install'
    if opt_obj.sel_path:
        prm['sel_path'] = int(opt_obj.sel_path)
    B = Builder()
    if prm['action'] == "help":
        parser.print_help()
    elif prm['action'] == "list":
        B.list_paths(prm)
    elif prm['action'] == "install":
        B.install_new_module(prm)

#
# Run main if executed as a script
if __name__ == "__main__":
    main()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
