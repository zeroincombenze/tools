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
REGEX_HTML = r"(<(/|\w+)[^>]*>|%[^\w]*\w)"
REGEX_SPACE = r"\s+"
REGEX_PUNCT = r"[<\W\S]+"

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
    ("Order(s)", "Ordine/i"),
    ("Invoice n.%s", ""),
    ("Invoice n.%(number)s of %(date)s", ""),
    ("Invoices", ""),
    ("Credit", "Credito"),
    ("Credit", "Avere", "l10n_it"),
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

    def get_hash_key(self, key, module=None):
        kk = key.lower() if key.upper() != key else key
        kk2 = ""
        if module:
            kk2 = module + "@:" + kk
        return kk, kk2

    def adjust_case(self, orig, tnxl):
        if tnxl:
            if orig == orig.upper():
                tnxl = tnxl.upper()
            elif len(tnxl) > 1 and orig[0] == orig[0].upper():
                tnxl = tnxl[0].upper() + tnxl[1:]
        return tnxl

    def set_plural(self, term):
        if term.endswith("ca") or term.endswith("ga"):
            term = term[: -1] + "he"
        elif term.endswith("cia") or term.endswith("gia"):
            if term[-4] in ("a", "e", "i", "o", "u"):
                term = term[: -1] + "ie"
            else:
                term = term[: -1] + "e"
        elif term.endswith("a"):
            term = term[: -1] + "e"
        elif term.endswith("e") or term.endswith("o"):
            term = term[: -1] + "i"
        return term

    def get_term(self, orig, module=None):
        tnxl = orig
        if orig:
            hkey, hkey_mod = self.get_hash_key(orig, module=module)
            if hkey_mod and hkey_mod in self.dict:
                tnxl = self.adjust_case(orig, self.dict[hkey_mod][1])
            elif hkey in self.dict:
                tnxl = self.adjust_case(orig, self.dict[hkey][1])
            elif orig.endswith("s"):
                hkey, hkey_mod = self.get_hash_key(orig[: -1])
                if hkey_mod and hkey_mod in self.dict:
                    tnxl = self.adjust_case(orig, self.dict[hkey_mod][1])
                elif hkey in self.dict:
                    tnxl = self.set_plural(self.adjust_case(orig, self.dict[hkey][1]))
        return tnxl

    def split_items(self, message):
        items = []
        ix = 0
        while ix < len(message):
            for regex in (REGEX_WORD,
                          REGEX_HTML,
                          REGEX_SPACE):
                match = re.match(regex, message[ix:])
                if match:
                    break
            if not match:
                ii = len(message) - ix
                for regex in (REGEX_WORD,
                              REGEX_HTML,
                              REGEX_SPACE):
                    match = re.search(regex, message[ix:])
                    if match:
                        ii = min(ii, match.start())
                kk = message[ix: ii + ix]
                items.append(kk)
                ix += ii
            else:
                kk = message[ix: match.end() + ix]
                items.append(kk)
                ix += match.end()
        return items

    def store_1_item(self, msg_orig, msg_tnxl, override=None, module=None):
        hash_key, hashkey_mod = self.get_hash_key(msg_orig, module=module)
        if hashkey_mod and (
            hashkey_mod not in self.dict
            or override
            or (msg_tnxl and self.dict[hashkey_mod][0] == self.dict[hashkey_mod][1])
        ):
            self.dict[hashkey_mod] = (msg_orig, msg_tnxl)
        elif hash_key and (
            hash_key not in self.dict
            or override
            or (msg_tnxl and self.dict[hash_key][0] == self.dict[hash_key][1])
        ):
            self.dict[hash_key] = (msg_orig, msg_tnxl)
        return self.get_term(msg_tnxl or msg_orig)

    def store_item(self, msg_orig, msg_tnxl, override=None, module=None):
        def islast(ix, terms):
            return ix == (len(terms) - 1)

        # if 'First Name' in msg_orig:
        #     import pdb; pdb.set_trace()
        if not msg_tnxl:
            msg_tnxl = msg_orig
        texts_orig = self.split_items(msg_orig)
        texts_tnxl = self.split_items(msg_tnxl)
        fullterm_orig = fullterm_tnxl = ""
        term_orig = term_tnxl = ""
        ix_orig = ix_tnxl = 0
        target = last_punct = ""
        while ix_orig < len(texts_orig) or ix_tnxl < len(texts_tnxl):
            item_orig = texts_orig[ix_orig] if ix_orig < len(texts_orig) else ""
            item_tnxl = texts_tnxl[ix_tnxl] if ix_tnxl < len(texts_tnxl) else ""
            if not item_orig:
                if self.is_word(item_tnxl):
                    term_tnxl += item_tnxl
                    fullterm_tnxl += item_tnxl
                else:
                    if islast(ix_tnxl, texts_tnxl):
                        last_punct = item_tnxl
                    else:
                        term_tnxl += item_tnxl
                        fullterm_tnxl += item_tnxl
                ix_tnxl += 1
            elif self.is_word(item_orig):
                term_orig += item_orig
                fullterm_orig += item_orig
                ix_orig += 1
                if self.is_word(item_tnxl):
                    item_tnxl = self.get_term(item_tnxl)
                    term_tnxl += item_tnxl
                    fullterm_tnxl += item_tnxl
                    ix_tnxl += 1
            elif self.is_space(item_orig):
                if not islast(ix_orig, texts_orig):
                    term_orig += item_orig
                    fullterm_orig += item_orig
                ix_orig += 1
                if self.is_space(item_tnxl):
                    if islast(ix_tnxl, texts_tnxl):
                        last_punct = item_tnxl
                    else:
                        term_tnxl += item_tnxl
                        fullterm_tnxl += item_tnxl
                    ix_tnxl += 1
            else:
                while self.is_word(item_tnxl) or self.is_space(item_tnxl):
                    fullterm_tnxl += item_tnxl
                    ix_tnxl += 1
                    item_tnxl = texts_tnxl[ix_tnxl] if ix_tnxl < len(texts_tnxl) else ""
                if term_orig and self.is_word(term_orig):
                    target += self.store_1_item(term_orig, term_tnxl, override=override)
                    term_orig = term_tnxl = ""
                if not islast(ix_orig, texts_orig) or self.is_html_tag(item_orig):
                    term_orig += item_orig
                    fullterm_orig += item_orig
                if self.is_html_tag(item_orig) and self.is_html_tag(item_tnxl):
                    term_tnxl += item_tnxl
                    fullterm_tnxl += item_tnxl
                    ix_tnxl += 1
                elif self.is_punct(item_orig) and self.is_punct(item_tnxl):
                    if islast(ix_tnxl, texts_tnxl):
                        last_punct = item_tnxl
                    else:
                        term_tnxl += item_tnxl
                        fullterm_tnxl += item_tnxl
                    ix_tnxl += 1
                ix_orig += 1
        if term_orig:
            if self.is_word(term_orig):
                target += self.store_1_item(term_orig, term_tnxl, override=override)
            elif term_tnxl:
                target += term_tnxl
        elif term_tnxl:
            target += term_tnxl
        if fullterm_orig:
            self.store_1_item(
                fullterm_orig, fullterm_tnxl, override=override, module=module)
            return "%s%s" % (target, last_punct)
        return ""

    def translate_item(self, msg_orig, msg_tnxl, module=None):
        if (
            (module
             and self.get_hash_key(msg_orig, module=module)[1] in self.dict)
            or self.get_hash_key(msg_orig)[0] in self.dict
        ):
            return self.get_term(msg_orig, module=module)
        return self.store_item(msg_orig, msg_tnxl, override=False)

    def translate_pofile(self, po_fn):
        if os.path.isfile(po_fn):
            module = self.opt_args.module
            try:
                catalog = pofile.read_po(open(po_fn, "r"))
            except BaseException as e:
                print("Error %s reading po file %s" % (e, po_fn))
                return
            for message in catalog:
                if not message.id:
                    continue
                print("[%s]->[%s]" % (
                    message.id,
                    self.translate_item(message.id, message.string, module=module)
                ))

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
                self.store_item(row["msgid"], row["msgstr"], module=row["module"])

    def load_terms_for_test(self):
        for items in TEST_DATA:
            items = list(items) + [None]
            message_id, message_str, module = items[0], items[1], items[2]
            self.store_item(message_id, message_str, module=module)

    def do_work_on_path(self, root, base, action=None):
        action = action or "load_terms"
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
            if action == "load_terms":
                self.load_terms_from_pofile(po_fn)
            elif action == "translate":
                self.translate_pofile(po_fn)
            else:
                raise

    def build_dict(self):
        if self.opt_args.file_xslx:
            self.load_terms_from_xlsx(self.opt_args.file_xslx)
        target_path = os.path.abspath(self.opt_args.target_path)
        self.do_work_on_path(target_path, None)
        for root, dirs, files in os.walk(target_path, topdown=True, followlinks=False):
            dirs[:] = [
                d
                for d in dirs
                if d not in (".git", "__to_remove", "doc", "setup", ".idea")
            ]
            for base in dirs:
                self.do_work_on_path(root, base)

    def translate_module(self):
        module = self.opt_args.module
        target_path = os.path.abspath(self.opt_args.target_path)
        if module == "OCB" and os.path.isfile(os.path.join(target_path, "odoo-bin")):
            self.do_work_on_path(target_path, None, action="translate")
        elif module == os.path.basename(target_path):
            self.do_work_on_path(target_path, None, action="translate")
        else:
            for root, dirs, files in os.walk(target_path,
                                             topdown=True,
                                             followlinks=False):
                dirs[:] = [
                    d
                    for d in dirs
                    if d not in (".git", "__to_remove", "doc", "setup", ".idea")
                ]
                for base in dirs:
                    if module == base:
                        self.do_work_on_path(root, base, action="translate")
                        break

    def list_dict(self):
        for hash_key, terms in self.dict.items():
            print("[%s]\n'%s'='%s'" % (hash_key, terms[0], terms[1]))


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
    parser.add_argument("-m", "--module")
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
    # odoo_tnl.list_dict()
    if odoo_tnl.opt_args.module:
        odoo_tnl.translate_module()
    if odoo_tnl.opt_args.test:
        print("")
        print("")
        for items in TEST_DATA:
            items = list(items) + [None]
            message_orig, message_tnxl, module = items[0], items[1], items[2]
            print("[%s]->[%s]" % (
                message_orig,
                odoo_tnl.translate_item(message_orig, message_tnxl, module=module)
            ))
    sts = 0
    return sts


if __name__ == "__main__":
    exit(main())
