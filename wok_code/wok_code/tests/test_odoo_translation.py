# -*- coding: utf-8 -*-
# flake8: noqa - pylint: skip-file
# Copyright (C) 2015-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
import os
import sys

from z0lib import z0lib
from zerobug import z0test, z0testodoo

__version__ = "2.0.15"

MODULE_ID = "wok_code"
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
    "msgid \"Invoices\"": "msgstr \"Fatture\"",
    "msgid \"<b>Invoice<b>\"": "msgstr \"<b>Fattura<b>\"",
    "msgid \"Dear ${name}\"": "msgstr \"Gentile ${name}\"",
    "msgid \"&gt; 100%%\"": "msgstr \"&gt; 100%%\"",
    "msgid \"Invoice n.%s\"": "msgstr \"Fattura n.%s\"",
    "msgid \"invoice n.%(number)s of %(date)s\"":
        "msgstr \"fattura n.%(number)s di %(date)s\"",
    "msgid \"# invoice lines\"": "msgstr \"N. righe fattura\"",
    "msgid \"/usr/name/line\"": "msgstr \"/usr/name/line\"",
    "msgid \"account.tax\"": "msgstr \"account.tax\"",
}

def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        self.Z = z0bug
        self.Z.inherit_cls(self)

    def setup(self, z0ctx):
        z0lib.run_traced(
            "build_cmd %s" % os.path.join(
                self.Z.rundir, "scripts", "odoo_translation.py")
        )

    def get_fqn(self, fn):
        return os.path.join(self.Z.testdir, "data", fn)

    def rm_data_file(self, fn):
        fqn = self.get_fqn(fn)
        if os.path.isfile(fqn):
            os.unlink(fqn)

    def read_data_file(self, fn):
        fqn = self.get_fqn(fn)
        with open(fqn, "r") as fd:
            contents = fd.read()
        return contents

    def test_01(self, z0ctx):
        base_cmd = os.path.join(self.Z.rundir, "scripts", "odoo_translation.py")
        ref_template = self.read_data_file("ref_odoo_template_tnl.csv")
        ref_tnl = self.read_data_file("ref_odoo_translation.csv")
        for odoo_version in ODOO_VERSIONS:
            if not z0ctx["dry_run"]:
                self.root = z0testodoo.build_odoo_env(z0ctx, odoo_version)
                odoo_root = os.path.join(self.root, odoo_version)
                repodir = z0testodoo.create_repo(
                    z0ctx, odoo_root, "test_repo", odoo_version
                )
                moduledir = z0testodoo.create_module(
                    z0ctx, repodir, "test_module", "%s.0.1.0" % odoo_version
                )
                i18n_dir = os.path.join(moduledir, "i18n")
                it_po_file = os.path.join(moduledir, "i18n", "it.po")

                if not os.path.isdir(i18n_dir):
                    os.mkdir(i18n_dir)
                if os.path.isfile(it_po_file):
                    os.unlink(it_po_file)
                self.rm_data_file("odoo_template_tnl.csv")
                self.rm_data_file("odoo_translation.csv")
                os.chdir(moduledir)

                cmd = "%s %s -WT" % (sys.executable, base_cmd)
                sts, stdout, stderr = z0lib.run_traced(cmd)
                self.assertEqual(sts, 0, msg_info=cmd)
                template = self.read_data_file("odoo_template_tnl.csv")
                tnl = self.read_data_file("odoo_translation.csv")

                self.assertEqual(
                    template, ref_template, msg="odoo_template_tnl contents"
                )
                self.assertEqual(
                    tnl, ref_tnl, msg="odoo_translation contents"
                )

                with open(it_po_file, "w") as fd:
                    fd.write(PO_FILE)
                cmd = "%s %s -T" % (sys.executable, base_cmd)
                sts, stdout, stderr = z0lib.run_traced(cmd)
                self.assertEqual(sts, 0, msg_info=cmd)
                with open(it_po_file, "r") as fd:
                    po_contents = fd.read()
                test_value = ""
                for ln in po_contents.split("\n"):
                    if test_value:
                        self.assertEqual(ln, test_value)
                        test_value = ""
                    else:
                        test_value = PO_TEST_VALUE.get(ln)

        return self.ret_sts()


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )





