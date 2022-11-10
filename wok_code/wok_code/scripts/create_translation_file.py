#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create map of Odoo modules
"""
import os
import sys
import argparse
import re
from babel.messages import pofile
from openpyxl import load_workbook

# from python_plus import unicodes

__version__ = "2.0.2.1"

REGEX_WORD = r"\w+"
REGEX_HTML = r"<(/|\w+)[^>]*>"
REGEX_SPACE = r"\s+"
REGEX_PUNCT = r"[-\[\\\]!\"#$%&'()*+,./:;<=>?@^`{|}~]+"
REGEX_OTHER = r"[^%s<\W\S]+" % REGEX_PUNCT[1: -1]

TEST_DATA = [
    ("name", "nome"),
    ("Name", "Nome"),
    ("Name.", "Name."),
    ("Name!!", "Name!!"),
    ("First Name", "Nome di battesimo"),
    ("Last Name", "Cognome"),
    ("UE", "EU"),
    ("Invoice", "Fattura"),
    ("Invoice", ""),
    ("<b>Invoice</b>", "<b>Invoice</b>"),
    ("<b>Invoice</b>", ""),
    ("<b>Invoice</b>", "<b>Fattura</b>"),
    ("Print <b>Invoice</b>!", "Stampa <b>Fattura</b>!"),
]


class OdooTranslation(object):
    """ """

    def __init__(self, opt_args):
        self.opt_args = opt_args
        self.dict = {}

    def ismodule(self, path):
        if os.path.isdir(path):
            if (
                os.path.isfile(os.path.join(path, "__manifest__.py"))
                or os.path.isfile(os.path.join(path, "__openerp__.py"))
            ) and os.path.isfile(os.path.join(path, "__init__.py")):
                return True
        return False

    def is_word(self, item):
        return bool(re.match(REGEX_WORD[: -1], item))

    def is_html_tag(self, item):
        return item.startswith("<") and item.endswith(">")

    def is_space(self, item):
        return bool(re.match(REGEX_SPACE[: -1], item))

    def is_punct(self, item):
        return bool(re.match(REGEX_PUNCT[: -1], item))

    def hash_key(self, key):
        kk = key.lower() if key.upper() != key else key
        return kk

    def join(self, keys, is_key=None):
        term = punct = ""
        prior_alpha = False
        for item in keys:
            if punct:
                term += punct
            punct = ""
            if self.is_html_tag(item):
                term += item
                prior_alpha = False
            elif self.is_punct(item):
                punct = item
                prior_alpha = False
            elif prior_alpha:
                term += " %s" % item
            else:
                term += item
                prior_alpha = True
        if punct and not is_key:
            term += punct
        return term

    def get_term(self, item):
        term = item
        if item:
            hkey = self.hash_key(item)
            if hkey in self.dict:
                term = self.dict[hkey]
                if item == item.upper():
                    term = term.upper()
                elif item[0] == item[0].upper():
                    term = "%s%s" % (term[0].upper(), term[1:])
        return term

    def split_items(self, message):
        items = []
        ix = 0
        while ix < len(message):
            for regex in (REGEX_WORD,
                          REGEX_HTML,
                          REGEX_SPACE,
                          REGEX_PUNCT,
                          REGEX_OTHER):
                match = re.match(regex, message[ix:])
            if not match:
                break
            kk = message[ix : match.end() + ix]
            items.append(kk)
            ix += match.end()
        return items

    def parse_items(self, items, is_key=None):
        keys = []
        texts = []
        hkey = text = punct = ""
        prior_alpha = False
        for item in items:
            if punct:
                hkey += punct
            punct = ""
            if self.is_html_tag(item):
                keys.append(hkey)
                texts.append(text)
                keys.append(item)
                texts.append(item)
                hkey = text = ""
                prior_alpha = False
            else:
                key = self.hash_key(item)
                if self.is_punct(item):
                    punct = key
                    text += item
                    prior_alpha = False
                elif prior_alpha:
                    hkey += (" %s" % key) if hkey else key
                    text += (" %s" % item) if text else item
                else:
                    hkey += key
                    text += item
                    prior_alpha = True
        if punct and not is_key:
            hkey += punct
        if hkey or text:
            keys.append(hkey)
            texts.append(text)
        return keys, texts

    def store_1_item(self, key, message_str, override=None):
        if key and (
            key not in self.dict or override or key == self.hash_key(self.dict[key])
        ):
            self.dict[key] = message_str

    def store_item(self, msg_id, msg_str, override=None):
        texts_id = self.split_items(msg_id)
        texts_str = self.split_items(msg_str)
        hash_key = hash_item =""
        tnlstr_key = tnlstr_item = ""
        ix_id = ix_str = 0
        while ix_id < len(texts_id) and ix_str < len(texts_str):
            termid = texts_id[ix_id] if ix_id < len(texts_id) else ""
            termstr = texts_str[ix_id] if ix_str < len(texts_str) else ""
            if self.is_word(termid):
                if self.is_word(termstr):
                    hash_key += self.hash_key(termid)
                    tnlstr_key += termstr
                    hash_item += self.hash_key(termid)
                    tnlstr_item += termstr
                    ix_id += 1
                    ix_str += 1
                else:
                    hash_key += self.hash_key(termid)
                    hash_item += self.hash_key(termid)
                    ix_id += 1
            elif self.is_html_tag(termid):
                hash_key += termid
                tnlstr_key += termstr
                self.store_1_item(hash_item, tnlstr_item, override=override)
                hash_item = ""
                tnlstr_item = ""
                ix_id += 1
                ix_str += 1
            elif self.is_punct(termid):
                pass
            elif self.is_space(termid):
                pass
            else:
                pass

    def translate_item(self, msg_id, msg_str):
        return self.store_item(msg_id, msg_str, override=False)

    def load_terms_from_pofile(self, po_fn, override=None):
        if os.path.isfile(po_fn):
            try:
                catalog = pofile.read_po(open(po_fn, "r"))
            except BaseException as e:
                print("Error %s reading po file %s" % (e, po_fn))
                return
            for message in catalog:
                if not message.id:
                    continue
                self.store_item(message.id, message.string, override=override)

    def load_terms_from_xlsx(self, dict_fn):
        if os.path.isfile(dict_fn):
            wb = load_workbook(dict_fn)
            sheet = wb.active
            colnames = []
            for ncol in sheet.columns:
                colnames.append(ncol[0].value)
            hdr = True
            for nrow in sheet.rows:
                if hdr:
                    hdr = False
                    continue
                row = {}
                for ncol, cell in enumerate(nrow):
                    row[colnames[ncol]] = (
                        cell.value.replace("\\n", "\n") if cell.value else cell.value
                    )
                if not row["msgid"] or not row["msgstr"]:
                    continue
                self.store_item(row["msgid"], row["msgstr"])

    def load_terms_for_test(self):
        for (message_id, message_str) in TEST_DATA:
            self.store_item(message_id, message_str)

    def build_dict(self):
        def do_dir_work(root, base):
            path = os.path.join(root, base) if base else root
            if self.ismodule(path):
                i18n_path = os.path.join(path, "i18n")
                po_fn = os.path.join(i18n_path, "%s.po" % self.opt_args.lang)
                if not os.path.isfile(po_fn):
                    po_fn = os.path.join(
                        i18n_path, "%s.po" % self.opt_args.lang.split("_")[0]
                    )
                if not os.path.isfile(po_fn):
                    print("Module %s without translation" % os.path.basename(path))
                    return
                self.load_terms_from_pofile(po_fn)

        if self.opt_args.file_xslx:
            self.load_terms_from_xlsx(self.opt_args.file_xslx)
        target_path = os.path.abspath(self.opt_args.target_path)
        do_dir_work(target_path, None)
        for root, dirs, files in os.walk(target_path, topdown=True, followlinks=False):
            dirs[:] = [
                d
                for d in dirs
                if d not in (".git", "__to_remove", "doc", "setup", ".idea")
            ]
            for base in dirs:
                do_dir_work(root, base)

    def list_dict(self):
        for kk, term in self.dict.items():
            print("'%s'='%s'" % (kk, term))


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Create translation file", epilog="© 2022-2023 by SHS-AV s.r.l."
    )
    parser.add_argument(
        "-b",
        "--odoo-branch",
        dest="odoo_branch",
        default="12.0",
        help="Default Odoo version",
    )
    parser.add_argument("-c", "--config", help="Odoo configuration file")
    parser.add_argument(
        "-G",
        "--git-orgs",
        help="Git organizations, comma separated - " "May be: oca librerp or zero",
    )
    parser.add_argument("-l", "--lang", default="it_IT", help="Language")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-p", "--target-path", help="Local directory")
    parser.add_argument("-T", "--test", action="store_true")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument("-x", "--file-xslx", help="Default dictionary")
    odoo_tnl = OdooTranslation(parser.parse_args(cli_args))
    if odoo_tnl.opt_args.test:
        odoo_tnl.load_terms_for_test()
    else:
        odoo_tnl.build_dict()
    odoo_tnl.list_dict()
    if odoo_tnl.opt_args.test:
        print("")
        for (message_id, message_str) in TEST_DATA:
            print(
                "[%s]->[%s]"
                % (message_id, odoo_tnl.translate_item(message_id, message_str))
            )
    sts = 0
    return sts


if __name__ == "__main__":
    exit(main())
