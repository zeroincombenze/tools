import sys
import os
import argparse
import re
import lxml.etree as ET
from python_plus import _b

__version__ = "1.0.5"

MIGRATE_TO_NEW = [
    (
        "from openerp.osv import orm$",
        "from openerp.osv import orm",
        "from odoo import models"
    ),
    ("from openerp", "openerp", "odoo"),
    ("^ *<openerp", "<openerp", "<odoo"),
    ("^ *</openerp", "</openerp", "</odoo"),
]
MIGRATE_TO_OLD = [
    (
        "from odoo import .*models",
        ["models", "orm"],
        ["odoo", "openerp.osv"],
    ),
    (
        "^from odoo.exceptions import UserError",
        "import UserError",
        "import Warning as UserError"
    ),
    ("from odoo", "odoo", "openerp"),
    ("^ *<odoo", "<odoo", "<openerp"),
    ("^ *</odoo", "</odoo", "</openerp"),
]


class MigrateFile(object):

    def __init__(self, ffn, opt_args):
        self.ffn = ffn
        self.opt_args = opt_args
        if opt_args.from_version:
            self.from_major_version = int(opt_args.from_version.split('.')[0])
        else:
            self.from_major_version = 0
        self.to_major_version = int(opt_args.to_version.split('.')[0])
        self.lines = []
        self.source_updated = False
        with open(ffn, 'r') as fd:
            self.lines = fd.read().split('\n')

    def do_migrate_openerp(self):
        self.source_updated = False
        found_tag_odoo = False
        found_tag_openerp = False
        found_tag_data = False
        found_etag_data = False

        nro = 0
        if self.to_major_version <= 8:
            TARGET = MIGRATE_TO_OLD
        else:
            TARGET = MIGRATE_TO_NEW
        while nro < len(self.lines):
            if not self.lines[nro]:
                nro += 1
                continue

            for item in TARGET:
                regex = item[0]
                if re.match(regex, self.lines[nro]):
                    if isinstance(item[1], (list, tuple)):
                        for tokens in item[1:]:
                            src = tokens[0]
                            tgt = tokens[1]
                            self.lines[nro] = self.lines[nro].replace(src, tgt)
                    else:
                        src = item[1]
                        tgt = item[2]
                        self.lines[nro] = self.lines[nro].replace(src, tgt)
                    self.source_updated = True

            if re.match("^ *<odoo", self.lines[nro]):
                found_tag_odoo = True
            elif re.match("^ *<openerp", self.lines[nro]):
                found_tag_openerp = True
                if "noupdate" in self.lines[nro]:
                    x = re.search("noupdate *=\"[01]\"", self.lines[nro])
                    found_tag_openerp = self.lines[nro][x.start():x.end()]
                    self.lines[nro] = self.lines[nro].replace(found_tag_openerp, "")
                    self.lines[nro] = self.lines[nro].replace(" ", "")
            elif re.match("^ *<data", self.lines[nro]):
                if found_tag_odoo:
                    if "noupdate" in self.lines[nro]:
                        x = re.search("noupdate *=\"[01]\"", self.lines[nro])
                        token = " " + self.lines[nro][x.start():x.end()] + ">"
                        self.lines[nro - 1] = self.lines[nro - 1].replace(">", token)
                    del self.lines[nro]
                    continue
                else:
                    found_tag_data = True
            elif re.match("^ *</odoo>", self.lines[nro]):
                if found_etag_data:
                    del self.lines[nro - 1]
                    continue
            elif re.match("^ *</openerp>", self.lines[nro]):
                if not found_etag_data:
                    self.lines.insert(nro, "</data>")
                    nro += 1
            elif re.match("^ *</data>", self.lines[nro]):
                found_etag_data = True
            else:
                if found_tag_openerp and not found_tag_data:
                    if isinstance(found_tag_openerp, str):
                        line = "<data %s>" % found_tag_openerp
                    else:
                        line = "<data>"
                    self.lines.insert(nro, line)
                    nro += 1
                found_tag_odoo = found_tag_openerp = found_tag_data = False
                found_etag_data = False
            nro += 1

    def close(self):
        if self.source_updated:
            bakfile = '%s.bak' % self.ffn
            if os.path.isfile(bakfile):
                os.remove(bakfile)
            if os.path.isfile(self.ffn):
                os.rename(self.ffn, bakfile)
            with open(self.ffn, 'w') as fd:
                if self.ffn.endswith(".xml"):
                    xml = ET.fromstring(
                        _b("\n".join(self.lines).replace('\t', '    '))
                    )
                    fd.write(ET.tostring(
                        xml,
                        encoding="unicode",
                        with_comments=True,
                        pretty_print=True)
                    )
                else:
                    fd.write("\n".join(self.lines))
                if self.opt_args.verbose > 0:
                    print('👽 %s' % self.ffn)


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Migrate source file",
        epilog="© 2021-2022 by SHS-AV s.r.l."
    )
    parser.add_argument('-b', '--to-version', default="12.0")
    parser.add_argument('-F', '--from-version')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-V', '--version', action="version", version=__version__)
    parser.add_argument('path')
    opt_args = parser.parse_args(cli_args)
    sts = 0
    if os.path.isdir(opt_args.path):
        for root, dirs, files in os.walk(opt_args.path):
            if 'setup' in dirs:
                del dirs[dirs.index('setup')]
            for fn in files:
                if not fn.endswith('.py') and not fn.endswith('.xml'):
                    continue
                source = MigrateFile(os.path.join(root, fn), opt_args)
                source.do_migrate_openerp()
                source.close()
    elif os.path.isfile(opt_args.path):
        source = MigrateFile(opt_args.path, opt_args)
        source.do_migrate_openerp()
        source.close()
    else:
        print('Path %s does not exist!' % opt_args.path)
        sts = 2
    return sts


if __name__ == "__main__":
    exit(main())
