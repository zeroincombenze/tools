#!/home/odoo/devel/venv/bin/python2
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://ww.zeroincombenze.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either versiofn 3 of the
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
    Sniff python code for specific token

"""

# import pdb
import os.path
import sys
import ConfigParser
import argparse
from pytok import pytok


__version__ = "0.2.4"
# Apply for configuration file (True/False)
APPLY_CONF = True
# Default configuration file (i.e. myfile.conf or False for default)
CONF_FN = False
# Read Odoo configuration file (False or /etc/openerp-server.conf)
ODOO_CONF = "/etc/openerp-server.conf"


class File_System():

    def parse_src_file(self, prm):
        data_path = prm['data_path']
        sts = 0
        for path in data_path:
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f[-3:] == ".py":
                        fn = os.path.join(root, f)
                        src = pytok.open(fn)
                        # if (prm['no_num_line'] or
                        #       (prm['inclass'] and prm['inclass'] != '.*') or
                        #         (prm['infun'] and prm['infun'] != '.*') or
                        #         (prm['token'] and prm['token'] != '.*') or
                        #        prm['model']):
                        src.decl_options(prm)
                        src.parse_src()
                        res = src.tostring()
                        if res:
                            print res
        return sts

File_System()


#############################################################################
# Custom parser functions
#
def default_conf():
    """Default configuration values"""
    d = {"addons_path": "./"}
    return d


def create_parser():
    """Return command-line parser.
    Some options are standard:
    -h --help       show help
    -V --version    show version
    """
    parser = argparse.ArgumentParser(
        description=docstring_summary(__doc__),
        epilog="© 2015 by SHS-AV s.r.l."
               " - http://www.zeroincombenze.org",
        argument_default=argparse.SUPPRESS)
    parser.add_argument("--class",
                        help="Search in class(es)",
                        dest="inclass",
                        metavar="name[,..]",
                        default=".*")
    parser.add_argument("--def",
                        help="Search in function(s)",
                        dest="infun",
                        metavar="name[,..]",
                        default=".*")
    parser.add_argument("--model",
                        help="Search classes with model",
                        dest="model",
                        metavar="name[,..]",
                        default="")
    parser.add_argument("-n", "--no-num-line",
                        help="display w/o line numbers",
                        action="store_true",
                        dest="no_num_line",
                        default=False)
    parser.add_argument("-p", "--data_path",
                        help="Source files path",
                        dest="data_path",
                        metavar="dir",
                        default="")
    parser.add_argument("-v", "--verbose",
                        help="run with debugging output",
                        action="store_true",
                        dest="dbg_mode",
                        default=False)
    parser.add_argument("-V", "--version",
                        action="version",
                        version="%(prog)s " + __version__)
    parser.add_argument("tokens",
                        help="token(s) to search",
                        nargs='?',
                        default='.*')
    return parser


def create_params_dict(opt_obj, conf_obj):
    """Create all params dictionary"""
    prm = {}
    s = "options"
    if not conf_obj.has_section(s):
        conf_obj.add_section(s)
    for p in ('addons_path',):
        prm[p] = conf_obj.get(s, p)

    if opt_obj.data_path:
        prm['data_path'] = map(lambda x: x.strip(),
                               opt_obj.data_path.split(','))
    else:
        prm['data_path'] = map(lambda x: x.strip(),
                               prm['addons_path'].split(','))
    svr_path_list = []
    for p1 in ('v7', 'v8', 'lp', 'git', 'odoo', 'openerp'):
        for p2 in ('odoo', 'openerp', 'server',
                   'openerp-server', 'odoo-server'):
            svr_path_list.append(p1 + '/' + p2)
    # engage server path
    server_path = []
    for p1 in prm['data_path']:
        for p2 in svr_path_list:
            i = p1.find(p2)
            if i >= 0:
                i = i + len(p2)
                svr_path = p1[:i]
                if svr_path not in server_path:
                    server_path.append(svr_path)
    for p1 in server_path:
        prm['data_path'].append(p1)

    prm['dbg_mode'] = opt_obj.dbg_mode
    prm['no_num_line'] = opt_obj.no_num_line
    prm['inclass'] = opt_obj.inclass
    prm['infun'] = opt_obj.infun
    prm['tokens'] = opt_obj.tokens
    prm['model'] = opt_obj.model
    prm['_opt_obj'] = opt_obj
    return prm


#############################################################################
# Common parser functions
#
def nakedname(fn):
    """Return nakedename (without extension)"""
    i = fn.rfind('.')
    if i >= 0:
        j = len(fn) - i
        if j <= 4:
            fn = fn[:i]
    return fn


def docstring_summary(docstring):
    """Return summary of docstring."""
    for text in docstring.split('\n'):
        if text.strip():
            break
    return text.strip()


def parse_args(arguments, apply_conf=False):
    """Parse command-line options."""
    parser = create_parser()
    opt_obj = parser.parse_args(arguments)
    if apply_conf:
        if hasattr(opt_obj, 'conf_fn'):
            conf_fn = opt_obj.conf_fn
            conf_obj, conf_fn = read_config(opt_obj, parser, conf_fn=conf_fn)
        else:
            conf_obj, conf_fn = read_config(opt_obj, parser)
        opt_obj = parser.parse_args(arguments)
    prm = create_params_dict(opt_obj, conf_obj)
    if 'conf_fn' in globals():
        prm['conf_fn'] = conf_fn
    return prm


def read_config(opt_obj, parser, conf_fn=None):
    """Read both user configuration and local configuration."""
    if conf_fn is None or not conf_fn:
        if CONF_FN:
            conf_fn = CONF_FN
        else:
            conf_fn = nakedname(os.path.basename(__file__)) + ".conf"
    d = default_conf()
    conf_obj = ConfigParser.SafeConfigParser(d)
    if ODOO_CONF:
        conf_fns = (ODOO_CONF, conf_fn)
    else:
        conf_fns = conf_fn
    conf_obj.read(conf_fns)
    return conf_obj, conf_fn


def main():
    """Tool main."""
    prm = parse_args(sys.argv[1:], apply_conf=APPLY_CONF)
    F = File_System()
    sts = F.parse_src_file(prm)
    return sts

if __name__ == "__main__":
    sts = main()
    sys.exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
