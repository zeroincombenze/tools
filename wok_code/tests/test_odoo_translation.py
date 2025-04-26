# -*- coding: utf-8 -*-
# flake8: noqa - pylint: skip-file
# Copyright (C) 2015-2025 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
import os
import sys

from z0lib import z0lib
from zerobug import z0test, z0testodoo

__version__ = "2.0.21"

TEST_FAILED = 1
TEST_SUCCESS = 0

ODOO_VERSIONS = ("12.0", "10.0", "7.0")

PO_FILE = """# Translation of Odoo Server.
# This file contains the translation of the following modules:
# * test_module
#
msgid ""
msgstr ""

#. module: test_module
#: model:ir.model.fields:test_module.account_id
msgid "account"
msgstr ""

#. module: test_module
#: model:ir.model.fields,field_description:test_module.test_model_account_id
msgid "Account"
msgstr ""

#. module: test_module
#: model:ir.model.fields,field_description:test_module.test_model_account_id
msgid "Account."
msgstr ""

#. module: test_module
#: model:ir.model.fields,field_description:test_module.test_model_account_id
msgid "tax"
msgstr ""

#. module: test_module
#: model:ir.model.fields,field_description:test_module.test_model_account_id
msgid "Credit"
msgstr ""

#. module: test_module
#: model:ir.model.fields,field_description:test_module.test_model_account_id
msgid "Invoices"
msgstr ""

#. module: test_module
#: model:ir.model.web,field_description:test_module.test_model_account_id
msgid "<b>Invoice</b>"
msgstr ""

#. module: test_module
#: model:ir.model.web,field_description:test_module.test_model_account_id
msgid "Dear ${name}"
msgstr ""

#. module: test_module
#: model:ir.model.web,field_description:test_module.test_model_account_id
msgid "Dear ${partner}"
msgstr ""

#. module: test_module
#: model:ir.model.web,field_description:test_module.test_model_account_id
msgid "&gt; 100%%"
msgstr ""

#. module: test_module
#: model:ir.model.web,field_description:test_module.test_model_account_id
msgid "Invoice n.%s"
msgstr ""

#. module: test_module
#: model:ir.model.web,field_description:test_module.test_model_account_id
msgid "invoice n.%(number)s of %(date)s"
msgstr ""

#. module: test_module
#: model:ir.model.web,field_description:test_module.test_model_account_id
msgid "# invoice lines"
msgstr ""

#. module: test_module
#: model:ir.model.web,field_description:test_module.test_model_account_id
msgid "Purchase"
msgstr "Purchase invoice"

#. module: test_module
#: model:ir.model.web,field_description:test_module.test_model_account_id
msgid "Sale Order"
msgstr ""

#. module: test_module
#: model:ir.model.web,field_description:test_module.test_model_account_id
msgid "/usr/name/line"
msgstr ""

#. module: test_module
#: model:ir.model.web,field_description:test_module.test_model_account_id
msgid "account.tax"
msgstr ""
"""

PO_TEST_VALUE = {
    "msgid \"account\"": "msgstr \"conto\"",
    "msgid \"Account\"": "msgstr \"Conto\"",
    "msgid \"Account.\"": "msgstr \"Conto.\"",
    "msgid \"tax\"": "msgstr \"IVA\"",
    "msgid \"Credit\"": "msgstr \"Credito\"",
    "msgid \"Invoices\"": "msgstr \"Fatture\"",
    "msgid \"<b>Invoice<b>\"": "msgstr \"<b>Fattura<b>\"",
    "msgid \"Dear ${name}\"": "msgstr \"Gentile ${name}\"",
    "msgid \"Dear ${partner}\"": "msgstr \"Gentile ${partner}\"",
    "msgid \"&gt; 100%%\"": "msgstr \"&gt; 100%%\"",
    "msgid \"Invoice n.%s\"": "msgstr \"Fattura n.%s\"",
    "msgid \"n. fattura%(number)s of %(date)s\"":
        "msgstr \"fattura n.%(number)s di %(date)s\"",
    "msgid \"# invoice lines\"": "msgstr \"N. righe fattura\"",
    "msgid \"Purchase\"": "msgstr \"Acquisto\"",
    "msgid \"Sale Order\"": "msgstr \"Ordine vendite\"",
    "msgid \"/usr/name/line\"": "msgstr \"/usr/name/line\"",
    "msgid \"account.tax\"": "msgstr \"account.tax\"",
}


def version():
    return __version__


class RegressionTest:

    def setup(self):
        if os.path.basename(os.getcwd()) == "tests":
            self.testdir = os.getcwd()
            self.rundir = os.path.dirname(os.getcwd())
        else:
            self.testdir = os.path.join(os.getcwd(), "tests")
            self.rundir = os.getcwd()
        z0lib.os_system(
            "build_cmd %s" % os.path.join(
                self.rundir, "scripts", "odoo_translation.py")
        )

    def get_fqn(self, fn):
        return os.path.join(self.testdir, "data", fn)

    def rm_data_file(self, fn):
        fqn = self.get_fqn(fn)
        if os.path.isfile(fqn):
            os.unlink(fqn)

    def read_data_file(self, fn):
        fqn = self.get_fqn(fn)
        with open(fqn, "r") as fd:
            contents = fd.read()
        contents = contents.split("\n")
        return "\n".join([contents[0]] + sorted(contents[1:]))

    def test_01(self):
        ref_template = self.read_data_file("ref_odoo_template_tnl.csv")
        ref_tnl = self.read_data_file("ref_odoo_translation.csv")
        for odoo_version in ODOO_VERSIONS:
            os.chdir(self.testdir)
            self.root = z0testodoo.build_odoo_env({}, odoo_version)
            odoo_root = os.path.join(self.root, odoo_version)
            repodir = z0testodoo.create_repo(
                {}, odoo_root, "test_repo", odoo_version
            )
            moduledir = z0testodoo.create_module(
                {}, repodir, "test_module", "%s.0.1.0" % odoo_version
            )
            i18n_dir = os.path.join(moduledir, "i18n")
            it_po_file = os.path.join(moduledir, "i18n", "it.po")

            if not os.path.isdir(i18n_dir):
                os.mkdir(i18n_dir)
            if os.path.isfile(it_po_file):
                os.unlink(it_po_file)
            self.rm_data_file("odoo_template_tnl.csv")
            self.rm_data_file(self.get_fqn(".odoo_template_tnl_cache.csv"))
            os.chdir(moduledir)

            cmd = "odoo_translation -WT"
            sts, stdout, stderr = z0lib.os_system_traced(cmd)
            self.assertEqual(sts, 0, msg_info="%s> %s" % (moduledir, cmd))
            template = self.read_data_file("odoo_template_tnl.csv")
            self.assertEqual(
                template, ref_template,
                msg="Files %s != %s" % ("odoo_template_tnl.csv",
                                        "ref_odoo_template_tnl.csv")
            )

            tnl = self.read_data_file(self.get_fqn(".odoo_template_tnl_cache.csv"))
            self.assertEqual(
                tnl, ref_tnl,
                msg="Files %s != %s" % (".odoo_template_tnl_cache.csv",
                                        "ref_odoo_translation.csv")
            )

            with open(it_po_file, "w") as fd:
                fd.write(PO_FILE)
            cmd = "odoo_translation -T"
            sts, stdout, stderr = z0lib.os_system_traced(cmd)
            self.assertEqual(sts, 0, msg_info="%s> %s" % (moduledir, cmd))
            with open(it_po_file, "r") as fd:
                po_contents = fd.read()
            test_value = ""
            for ln in po_contents.split("\n"):
                if test_value:
                    self.assertEqual(ln, test_value)
                    test_value = ""
                else:
                    test_value = PO_TEST_VALUE.get(ln)

    def test_02(self):
        odoo_version = "12.0"
        moduledir = os.path.join(self.root, odoo_version, "test_repo", "test_module")
        po_file = os.path.join(moduledir, "i18n", "it.po")
        with open(po_file, "r") as fd:
            contents = fd.read()
        contents = contents.replace("msgstr \"IVA\"", "msgstr \"CI\"")
        with open(po_file, "w") as fd:
            fd.write(contents)
        os.chdir(moduledir)
        cmd = "odoo_translation -WT -p %s -C" % moduledir
        sts, stdout, stderr = z0lib.os_system_traced(cmd)
        self.assertEqual(sts, 0, msg_info="%s> %s" % (moduledir, cmd))
        template = self.read_data_file("odoo_template_tnl.csv")
        self.assertIn("\ttax\tCI", template)


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )





