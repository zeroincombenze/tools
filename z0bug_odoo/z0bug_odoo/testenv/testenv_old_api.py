# -*- coding: utf-8 -*-
"""Test Environment v2.0.12

Copy this file in tests directory of your module.
Please copy the documentation testenv.rst file too in your module.
The __init__.py must import testenv.
Your python test file should have to contain some following example lines:

::

    import os
    import logging
    from .testenv import MainTest as SingleTransactionCase

    _logger = logging.getLogger(__name__)

    TEST_RES_PARTNER = {...}
    TEST_SETUP_LIST = ["res.partner", ]

    class MyTest(SingleTransactionCase):

        def setUp(self):
            super().setUp()
            # Add following statement just for get debug information
            self.debug_level = 2
            data = {"TEST_SETUP_LIST": TEST_SETUP_LIST}
            for resource in TEST_SETUP_LIST:
                item = "TEST_%s" % resource.upper().replace(".", "_")
                data[item] = globals()[item]
            self.declare_all_data(data)                 # TestEnv swallows the data
            self.setup_env()                            # Create test environment

        def tearDown(self):
            super().tearDown()
            if os.environ.get("ODOO_COMMIT_TEST", ""):  # pragma: no cover
                # Save test environment, so it is available to dump
                self.env.cr.commit()                    # pylint: disable=invalid-commit
                _logger.info("✨ Test data committed")

        def test_mytest(self):
            _logger.info(
                "🎺 Testing test_mytest"    # Use unicode char to best log reading
            )
            ...

        def test_mywizard(self):
            self.wizard(...)                # Test requires wizard simulator

External reference
~~~~~~~~~~~~~~~~~~

Every record is tagged by an external reference.
The external reference may be:

* Ordinary Odoo external reference (a), called xref, format "module.name"
* Test reference, format "z0bug.name" (b)
* Key value, format "external.key" (c)
* 2 keys reference, for header/detail relationship (d)
* Magic reference for 'product.template' / 'product.product' (e)
* Magic 3 level Odoo xref, format "module.name.field" (f)

Ordinary Odoo external reference (a) is a record of 'ir.model.data';
you can see them from Odoo GUI interface.

Test reference (b) are like external reference (a) but they are visible just in the
test environment. They are identified by "z0bug." prefix module name.

External key reference (c) is identified by "external." prefix followed by
the key value used to retrieve the record. The field "code" or "name" are usually used
to search record; for account.tax the "description" field is used.
Please set self.debug_level = 2 (or more) to log these field keys.

The 2 keys reference (d) needs to address child record inside header record
at 2 level model (header/detail) relationship.
The key MUST BE the couple of header key plus "_" and plus line key (usually 'sequence'
field); the header key is the same key of the parent record. The line key may be:

* the sequence value (if present n model)
* the most meaningful field value
* an index value

i.e. "z0bug.invoice_1_3" means: line with sequence 3 of 'account.invoice.line'
which is child of record "z0bug.invoice_1" of 'account.invoice'.
i.e.: "EUR.2023-06-26" should be the key for res.currency.rate where "EUR" is the header
key (res.currency) and "2023-06-26" is the date of rate.
Please set self.debug_level = 2 (or more) to log these relationships.

For 'product.template' (product) you must use '_template' text in reference (e).
TestEnv inherit 'product.product' (variant) external reference (read above
'Magic relationship).

The magic 3 level Odoo xref is a special reference applicable on all kind of data.
The format is like standard odoo xref with a 3th level which is the field name.
i.e. "base.partner_1.name" means the field name of the standard Odoo external reference
"base.partner_1". Notice:

* every field of xref may be used
* TestEnv does not match the type of current field and xref field
* External reference may one of above (a) (b) (c) (d) or (e)

For furthermore information, please:

* Read file testenv.rst in this directory (if supplied)
* Visit https://zeroincombenze-tools.readthedocs.io
* Visit https://github.com/zeroincombenze/tools
* Visit https://github.com/zeroincombenze/zerobug-test
"""
from __future__ import unicode_literals

import base64
import inspect
import json
import logging
import os
import re
import sys
from datetime import datetime, date

from future.utils import PY2, PY3
from past.builtins import basestring, long

try:
    import odoo.release as release
except ImportError:
    try:
        import openerp.release as release
    except ImportError:
        release = None
if release:
    if int(release.major_version.split('.')[0]) < 10:
        if int(release.major_version.split('.')[0]) > 7:
            from openerp import api                                        # noqa: F401
        import openerp.tests.common as test_common
        from openerp import workflow  # noqa: F401
        from openerp.modules.module import get_module_resource             # noqa: F401
    else:
        from odoo import api                                               # noqa: F401
        import odoo.tests.common as test_common
        from odoo.modules.module import get_module_resource                # noqa: F401
        from odoo.tools.safe_eval import safe_eval

import python_plus
from z0bug_odoo import z0bug_odoo_lib

_logger = logging.getLogger(__name__)

BITTER_COLUMNS = [
    "mail_message_id",
    "message_bounce",
    "message_channel_ids",
    "message_follower_ids",
    "message_ids",
    "message_is_follower",
    "message_last_post",
    "message_needaction",
    "message_needaction_counter",
    "message_partner_ids",
    "message_type",
    "message_unread",
    "message_unread_counter",
    "report_rml",
    "report_rml_content",
    "report_rml_content_data",
    "report_sxw",
    "report_sxw_content",
    "report_sxw_content_data",
    "search_view",
    "search_view_id",
    "seen_message_id",
]
LOG_ACCESS_COLUMNS = ["create_uid", "create_date", "write_uid", "write_date"]
MAGIC_COLUMNS = ["id"] + LOG_ACCESS_COLUMNS
SUPERMAGIC_COLUMNS = MAGIC_COLUMNS + BITTER_COLUMNS
BLACKLIST_COLUMNS = SUPERMAGIC_COLUMNS + ["parent_left", "parent_right", "state"]
RESOURCE_WO_COMPANY = (
    "res.currency",
    "res.currency.rate",
    "res.users",
    "res.partner",
    "product.template",
    "product.product",
)
# Please, do not change fields order
KEY_CANDIDATE = (
    "acc_number",
    "code_prefix",
    "default_code",
    "sequence",
    "login",
    "depreciation_type_id",
    "number",
    "move_name",
    "partner_id",
    "product_id",
    "product_tmpl_id",
    "agent",
    "commission",
    "ref",
    "reference",
    "account_id",
    "tax_src_id",
    "tax_dest_id",
    "code",
    "name",
)
KEY_INCANDIDATE = {
    "code": ["product.product"],
    "partner_id": ["account.move.line", "stock.location"],
    "ref": ["res.partner"],
    "reference": ["sale.order"],
}
KEY_OF_RESOURCE = {
    "account.tax": "description",
    "account.rc.type.tax": "purchase_tax_id",
    "res.users": "login",
    "stock.location": "name",
}
REC_KEY_NAME = {"id", "code", "name"}
if PY3:  # pragma: no cover
    text_type = unicode = str
    bytestr_type = bytes
elif PY2:  # pragma: no cover
    # unicode exist only for python2
    text_type = unicode
    bytestr_type = str


def is_iterable(obj):
    return hasattr(obj, "__iter__")


class MainTest(test_common.TransactionCase):

    def setUp(self):
        super(MainTest, self).setUp()
        self.odoo_major_version = release.version_info[0] if release else 0
        self.debug_level = 0
        self.PYCODESET = "utf-8"
        self._logger = _logger
        # List of stored data by groups: grp1: [a,b,c], grp2: [d,e,f]
        self.setup_data_list = {}
        # Data keys by group, resource, xref
        self.setup_data = {}
        # List of (group, resource) for every xref
        self.setup_xrefs = {}
        # Database structure (fields) by resource
        self.struct = {}
        # Resource search keys: the first key is the child xref search key
        self.skeys = {}
        # Parent resource field name for every resource
        self.parent_name = {}
        # Parent resource name for every resource
        self.parent_resource = {}
        # Childs one2many field name for every resource
        self.childs_name = {}
        # Child resource name for every resource
        self.childs_resource = {}
        self.uninstallable_modules = []
        self.convey_record = {}
        if not hasattr(self, "assert_counter"):
            self.assert_counter = 0
        for item in self.__module__.split("."):
            if item not in ("odoo", "openerp", "addons"):
                self.module = self.env["ir.module.module"].search(
                    [("name", "=", item)]
                )[0]
                if self.module:
                    break

    def tearDown(self):
        super(MainTest, self).tearDown()
        self._logger.info("🏆🥇 %d tests SUCCESSFULLY completed" % self.assert_counter)

    # ---------------------------------------
    # --  Unicode encode/decode functions  --
    # ---------------------------------------
    def u(self, s):  # pragma: no cover
        if isinstance(s, bytestr_type):
            if PY3:
                return s.decode(self.PYCODESET)
            return unicode(s, self.PYCODESET)
        return s

    def unicodes(self, src):  # pragma: no cover
        if isinstance(src, dict):
            src2 = src.copy()
            for x in src2.keys():
                if isinstance(x, bytestr_type):
                    del src[x]
                src[self.u(x)] = self.u(src2[x])
        elif isinstance(src, (list, tuple)):
            for i, x in enumerate(src):
                src[i] = self.u(x)
        return src

    # ---------------------------
    # -- log/tracing functions --
    # ---------------------------
    def dict_2_print(self, values):  # pragma: no cover
        def to_str(obj):
            x = str(obj)
            return x if (hasattr(obj, "len") and len(x) < 150) else "[...]"

        if isinstance(values, dict):
            return json.dumps(values, default=to_str, indent=4)
        return values

    def log_lvl_3(self, mesg, strict=None):  # pragma: no cover
        if (self.debug_level >= 3 and not strict) or self.debug_level == 3:
            self._logger.info(mesg)

    def log_lvl_2(self, mesg, strict=None):  # pragma: no cover
        if (self.debug_level >= 2 and not strict) or self.debug_level == 2:
            self._logger.info(mesg)

    def log_lvl_1(self, mesg, strict=None):  # pragma: no cover
        if (self.debug_level >= 1 and not strict) or self.debug_level == 1:
            self._logger.info(mesg)

    def log_stack(self):
        stack = inspect.stack()
        ctr = 0
        for ix in range(10):
            if os.path.basename(stack[ix][1]).startswith("testenv"):
                continue
            self.log_lvl_2("🚧 %s(%s)/%s()\n%s" % (
                os.path.basename(stack[ix][1]),
                stack[ix][2],
                stack[ix][3],
                stack[ix][4]
            ))
            ctr += 1
            if ctr > 0:
                break

    def raise_error(self, mesg):  # pragma: no cover
        self._logger.info("🛑 " + mesg)
        raise ValueError(mesg)

    # ----------------------------------
    # --  Counted assertion functions --
    # ----------------------------------

    def assertFalse(self, expr, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertFalse(expr, msg=msg)

    def assertTrue(self, expr, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertTrue(expr, msg=msg)

    def assertRaises(self, expected_exception, *args, **kwargs):     # pragma: no cover
        self.assert_counter += 1
        return super(MainTest, self).assertRaises(expected_exception, *args, **kwargs)

    def assertEqual(self, first, second, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertEqual(first, second, msg=msg)

    def assertNotEqual(self, first, second, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertNotEqual(first, second, msg=msg)

    def assertIn(self, member, container, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertIn(member, container, msg=msg)

    def assertNotIn(self, member, container, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertNotIn(member, container, msg=msg)

    def assertIs(self, expr1, expr2, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertIs(expr1, expr2, msg=msg)

    def assertIsNot(self, expr1, expr2, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertIsNot(expr1, expr2, msg=msg)

    def assertLess(self, a, b, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertLess(a, b, msg=msg)

    def assertLessEqual(self, a, b, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertLessEqual(a, b, msg=msg)

    def assertGreater(self, a, b, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertGreater(a, b, msg=msg)

    def assertGreaterEqual(self, a, b, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertGreaterEqual(a, b, msg=msg)

    def assertIsNone(self, obj, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertIsNone(obj, msg=msg)

    def assertIsNotNone(self, obj, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertIsNotNone(obj, msg=msg)

    def assertIsInstance(self, obj, cls, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertIsInstance(obj, cls, msg=msg)

    def assertNotIsInstance(self, obj, cls, msg=None):
        self.assert_counter += 1
        return super(MainTest, self).assertNotIsInstance(obj, cls, msg=msg)

    # ----------------------------
    # --  Conveyance functions  --
    # ----------------------------
    # def translate(self, resource, source, ttype=None, fld_name=False):
    #     if self.decl_version == self.odoo_version:
    #         return source
    #     return transodoo.translate_from_to(
    #         self.tnldict,
    #         resource,
    #         source,
    #         self.decl_version,
    #         self.odoo_version,
    #         ttype=ttype,
    #         fld_name=fld_name,
    #     )

    def _move_conveyed_xref(self, resource, xref, conveyed_xref, group=None):
        group = group or "base"
        if conveyed_xref != xref:
            if (
                group in self.setup_data
                and resource in self.setup_data[group]
                and xref in self.setup_data[group][resource]
            ):
                self.setup_data[group][resource][conveyed_xref] = self.setup_data[
                    group
                ][resource][xref]
                del self.setup_data[group][resource][xref]

    def _add_conveyance(self, resource, field, convey):
        if isinstance(convey, basestring):
            self._logger.info("⚠ %s.%s(%s)" % (resource, convey, field))
        else:
            self._logger.info(
                "⚠ %s[%s]: '%s' -> '%s'" % (resource, field, convey[0], convey[1])
            )
        if field == "all" and (
            not isinstance(convey, basestring)
            or convey != ("_cvt_%s" % resource.replace(".", "_"))
            or not hasattr(self, convey)
        ):  # pragma: no cover
            self.raise_error("Invalid name %s or function not found!" % convey)
        if resource not in self.convey_record:
            self.convey_record[resource] = {}
        self.convey_record[resource][field] = convey

    def add_alias_xref(self, xref, conveyed_xref, resource=None, group=None):
        self._logger.info("⚠ xref '%s' -> '%s'" % (xref, conveyed_xref))
        ir_resource = "ir.model.data"
        if ir_resource not in self.convey_record:
            self.convey_record[ir_resource] = {}
        self.convey_record[ir_resource][xref] = conveyed_xref
        self._move_conveyed_xref(resource, xref, conveyed_xref, group=group)

    def _get_conveyed_value(self, resource, field, value, fmt=None):
        if (
            resource in self.convey_record
            and field == "all"
            and field in self.convey_record[resource]
            and isinstance(value, dict)
            and hasattr(self, self.convey_record[resource][field])
        ):
            value = getattr(self, self.convey_record[resource][field])(value)
        elif (
            resource in self.convey_record
            and field in self.convey_record[resource]
            and value == self.convey_record[resource][field][0]
        ):
            value = self.convey_record[resource][field][1]
        elif (
            self._is_xref(value)
            and "ir.model.data" in self.convey_record
            and value in self.convey_record["ir.model.data"]
        ):
            value = self.convey_record["ir.model.data"][value]
        else:
            value = self.u(value)
        return value

    def _convert_test_data(self, group=None):
        if not self.env["ir.module.module"].search(
            [("name", "=", "stock"), ("state", "=", "installed")]
        ):
            for resource in ("product.product", "product.template"):
                self._add_conveyance(resource, "type", ["product", "consu"])
        if not self.env["ir.module.module"].search(
            [
                ("name", "=", "account_payment_term_extension"),
                ("state", "=", "installed"),
            ]
        ):
            self._add_conveyance(
                "account.payment.term.line", "all", "_cvt_account_payment_term_line"
            )

    def _cvt_account_payment_term_line(self, values):
        if values.get("months"):
            values["days"] = values["months"] * 30
            values["months"] = ""
            if values.get("option") in (
                "fix_day_following_month",
                "after_invoice_month",
            ):  # pragma: no cover
                values["days"] -= 2
        return values

    # ------------------------------
    # --  Hierarchical functions  --
    # ------------------------------

    def _search4parent(self, resource, parent_resource=None):
        if resource == "product.product":
            parent_resource = "product.template"
        else:
            parent_resource = parent_resource or resource.rsplit(".", 1)[0]
        if parent_resource not in self.env:
            parent_resource = None
        if parent_resource and resource not in self.parent_resource:
            for field in self.struct[resource].keys():
                if self.struct[resource][field].get("relation", "/") == parent_resource:
                    self.parent_name[resource] = field
                    self.parent_resource[resource] = parent_resource
                    self.log_lvl_2(
                        " 🌍 parent_resource[%s] = %s"
                        % (resource, self.parent_resource[resource])
                    )
                    self.log_lvl_2(" 🌍 parent_name[%s] = %s" % (resource, field))
                    break

    def _search4childs(self, resource, childs_resource=None):
        def _relation_prio(resource):
            return childs_resource.index(resource)

        childs_resource = childs_resource or []
        if not childs_resource:
            if resource == "product.template":
                childs_resource = ["product.product"]
            else:
                for suffix in (".line", ".rate", ".state", ".tax"):
                    childs_resource.append(resource + suffix)
        if not isinstance(childs_resource, (list, tuple)):
            childs_resource = [childs_resource]  # pragma: no cover
        if resource not in self.childs_resource:
            for field in self.struct[resource].keys():
                if self.struct[resource][field].get("relation", "/") in childs_resource:
                    candidate = self.struct[resource][field]["relation"]
                    if (
                        resource not in self.childs_name
                        or _relation_prio(candidate) < _relation_prio(
                            self.childs_resource[resource])
                        or (_relation_prio(candidate) == _relation_prio(
                            self.childs_resource[resource])
                            and len(field) < len(self.childs_name[resource]))
                    ):
                        self.childs_name[resource] = field
                        self.childs_resource[resource] = candidate
                        self.log_lvl_2(
                            " 🌍 childs_resource[%s] = %s"
                            % (resource, self.childs_resource[resource])
                        )
                        self.log_lvl_2(" 🌍 childs_name[%s] = %s" % (resource, field))

    def _add_child_records(self, resource, xref, values, group=None):
        if resource not in self.childs_name:
            return values
        field = self.childs_name[resource]
        if values.get(field):
            return values
        values[field] = []
        childs_resource = self.childs_resource[resource]
        for child_xref in self.get_resource_data_list(childs_resource, group=group):
            if child_xref.startswith(xref):
                record = self.resource_browse(
                    child_xref,
                    raise_if_not_found=False,
                    resource=childs_resource,
                    group=group,
                )
                if record:
                    values[field].append((1, record.id, child_xref))
                else:
                    values[field].append((0, 0, child_xref))
        return values

    # --------------------------------
    # --  Data structure functions  --
    # --------------------------------

    def _is_xref(self, xref):
        return (
            isinstance(xref, basestring)
            and re.match(r"[\w]+\.[\w][^\s]+$", xref)
        )

    def _unpack_xref(self, xref):
        # This is a 3 level external reference for header/detail relationship
        try:
            xref, ln = xref.rsplit("_", 1)
        except ValueError:
            self.log_lvl_1(" 🌍 Invalid detail xref %s" % xref)
            ln = ""
        if ln.isdigit():
            ln = int(ln) or False
        elif isinstance(ln, basestring) and self._is_xref(ln):
            ln = self._get_xref_id(self._get_model_of_xref(xref), xref=ln, fmt="id")
        return xref, ln

    def _is_transient(self, resource):
        if isinstance(resource, basestring):
            return self.env[resource]._transient                     # pragma: no cover
        return resource._transient

    def _add_xref(self, xref, xid, resource):
        """Add external reference ID that will be used in next tests.
        If xref exist, result ID will be upgraded"""
        module, name = xref.split(".", 1)
        if module == "external":
            return False
        ir_model = self.env["ir.model.data"]
        values = {
            "module": module,
            "name": name,
            "model": resource,
            "res_id": xid,
        }
        xrefs = ir_model.search([("module", "=", module), ("name", "=", name)])
        if not xrefs:
            return ir_model.create(values)
        xrefs[0].write(values)  # pragma: no cover
        return xrefs[0]  # pragma: no cover

    def _get_xref_id(self, resource, xref, fmt=None, group=None):
        res = xref
        if xref.isdigit() or (xref.startswith("-") and xref[1:].isdigit()):
            res = int(xref)
        elif self._is_xref(xref):
            if fmt:
                res = self.resource_browse(
                    xref,
                    raise_if_not_found=False,
                    resource=resource,
                    group=group,
                )
                if not res and not self.get_resource_data(resource, xref):
                    self._logger.info("⚠ External reference %s not found" % xref)
            else:
                # if not resource:
                #     resource = self._get_model_of_xref(xref)
                res = self.env.ref(
                    self._get_conveyed_value(resource, None, xref),
                    raise_if_not_found=False,
                )
            res = res.id if res else False if fmt else xref
        return res

    def _get_model_of_xref(self, xref):
        resource = name = ln = None
        if xref in self.setup_xrefs:
            group, resource = self.setup_xrefs[xref]
        if not resource:
            name, ln = self._unpack_xref(xref)
            if ln and name in self.setup_xrefs:
                group, resource = self.setup_xrefs[name]
                resource = self.childs_resource.get(resource, resource)
        if not resource:
            resource, res_id = self.env['ir.model.data'].xmlid_to_res_model_res_id(
                xref, raise_if_not_found=False)
            if not resource and name and ln:
                resource, res_id = self.env['ir.model.data'].xmlid_to_res_model_res_id(
                    name, raise_if_not_found=False)
                resource = self.childs_resource.get(resource, resource)
            if resource:
                self.setup_xrefs[xref] = (None, resource)
        return resource

    def _get_depending_xref(self, resource, xref):
        resource_child = xref_child = field_child = field_parent = False
        if resource == "product.template":
            xref_child = xref.replace("_template", "_product")
            if xref_child == xref:
                xref_child = xref.replace("template_", "product_")  # pragma: no cover
            if xref_child == xref:
                xref_child = xref.replace("template", "product")  # pragma: no cover
            if xref_child == xref:  # pragma: no cover
                self._logger.info(
                    (
                        "⚠ wrong xref pattern '%s':"
                        " please use something like 'z0bug.product_template_1"
                    )
                    % xref
                )
                xref_child = False
            else:
                self._logger.info(
                    "xref ('product.template') '%s' -> ('product.product') '%s'"
                    % (xref, xref_child)
                )
                resource_child = self.childs_resource[resource]
                field_child = self.childs_name[resource]
                field_parent = "product_tmpl_id"
        return resource_child, xref_child, field_child, field_parent

    def _load_field_struct(self, resource):
        """Load Odoo field definition"""
        if resource not in self.struct:
            if resource not in self.env:
                self.raise_error(
                    "Model %s not found in the system" % resource
                )  # pragma: no cover
            self.struct[resource] = self.env[resource].fields_get()
            self._search4parent(resource)
            if resource in self.parent_resource:
                self._load_field_struct(self.parent_resource[resource])
                self._search4childs(self.parent_resource[resource])
            self._search4childs(resource)
            if resource in self.childs_resource:
                self._load_field_struct(self.childs_resource[resource])
                self._search4parent(self.childs_resource[resource])
            if resource in KEY_OF_RESOURCE:
                field = KEY_OF_RESOURCE[resource]
                self.skeys[resource] = [field]
                self.log_lvl_2(
                    " 🌍 skeys[%s] = %s" % (resource, self.skeys[resource])
                )
            else:
                multi_key = True if self.parent_name.get(resource) else False
                hdr_key = True if self.childs_name.get(resource) else False
                self.skeys[resource] = []
                for field in KEY_CANDIDATE:
                    if (
                        field == self.parent_name.get(resource)
                        or field in ("product_id", "partner_id") and hdr_key
                        or (field == "sequence" and not multi_key)
                        or resource in KEY_INCANDIDATE.get(field, [])
                    ):
                        continue  # pragma: no cover
                    if field in self.struct[resource]:
                        self.skeys[resource].append(field)
                        self.log_lvl_2(
                            " 🌍 skeys[%s] = %s" % (resource, self.skeys[resource])
                        )
                        if (
                            not multi_key
                            or field == "sequence"
                            or len(self.skeys[resource]) >= 3
                        ):
                            break

    # ---------------------------------------------
    # --  Type <char> / <text> / base functions  --
    # ---------------------------------------------
    # Return unicode even on python2

    def _cast_field(self, resource, field, value, fmt=None, group=None):
        ftype = self.struct[resource][field]["type"]
        if ftype not in ("text", "binary", "html"):
            value = self._get_conveyed_value(resource, field, value, fmt=fmt)
        if ((isinstance(value, str) or (sys.version_info[0] == 2
                                        and isinstance(value, unicode)))
                and value.startswith("<?odoo")
                and value.endswith("?>")
                and len(value.split(".")) == 3):
            xref, field = [x.strip() for x in value[6: -2].rsplit(".", 1)]
            value = self.resource_browse(xref=xref)[field]
        if value is None or (
            isinstance(value, basestring)
            and (value in ("None", r"\N") or field == "id")
        ):
            value = None
        elif (
            field == "company_id"
            and fmt
            and not value
            and resource not in RESOURCE_WO_COMPANY
        ):
            value = self.default_company().id
        else:
            method = "_cast_field_%s" % ftype
            method = method if hasattr(self, method) else "_cast_field_base"
            value = getattr(self, method)(resource, field, value, fmt=fmt, group=group)
        return value

    def _convert_field_to_write(self, record, field):
        value = record[field]
        if value is not None and value is not False:
            method = "_convert_%s_to_write" % record._fields[field].type
            method = method if hasattr(self, method) else "_convert_base_to_write"
            value = getattr(self, method)(record, field, value)
        return value

    def _cast_field_base(self, resource, field, value, fmt=None, group=None):
        return value

    def _upgrade_field_base(self, record, field, value):
        return value

    def _convert_base_to_write(self, record, field, value):
        return value

    # ----------------------------------
    # --  Type <selection> functions  --
    # ----------------------------------
    # Return unicode even on python2

    def _cast_field_selection(self, resource, field, value, fmt=None, group=None):
        if fmt and resource == "res.partner" and field == "lang":
            if not self.env["res.lang"].search([("code", "=", value)]):
                self._logger.info("⚠ Invalid value %s" % value)
                value = None
        return value

    # --------------------------------
    # --  Type <boolean> functions  --
    # --------------------------------
    # Return boolean

    def _cast_field_boolean(self, resource, field, value, fmt=None, group=None):
        if isinstance(value, basestring):
            if value.isdigit():
                value = int(value)
            elif (
                not value
                or value.lower().startswith("f")
                or value.lower().startswith("n")
            ):
                value = False
            else:
                value = True
        return value

    # --------------------------------
    # --  Type <integer> functions  --
    # --------------------------------
    # Return integer and/or long on python2

    def _cast_field_integer(self, resource, field, value, fmt=None, group=None):
        if value and isinstance(value, basestring):
            value = int(value)
        return value

    # ------------------------------
    # --  Type <float> functions  --
    # ------------------------------
    # Return float

    def _cast_field_float(self, resource, field, value, fmt=None, group=None):
        if value and isinstance(value, basestring):
            value = eval(value)
        return value

    # ---------------------------------
    # --  Type <monetary> functions  --
    # ---------------------------------
    # Return float

    def _cast_field_monetary(self, resource, field, value, fmt=None, group=None):
        return self._cast_field_float(resource, field, value, fmt=fmt, group=group)

    # ---------------------------------
    # --  Type <datetime> functions  --
    # ---------------------------------
    # Return datetime (cast / upgrade)
    # Return datetime (convert Odoo 11+) or string (convert Odoo 10-)

    def _cvt_to_datetime(self, value):
        if isinstance(value, date):
            if isinstance(value, datetime):
                value = datetime(value.year,
                                 value.month,
                                 value.day,
                                 value.hour,
                                 value.minute,
                                 value.second)
            else:
                value = datetime(value.year, value.month, value.day, 0, 0, 0)
        elif isinstance(value, basestring):
            if len(value) <= 10:
                value += " 00:00:00"
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return value

    def _cast_field_datetime(self, resource, field, value, fmt=None, group=None):
        if isinstance(value, (list, tuple)) and fmt:
            value = self._cvt_to_datetime(self.compute_date(value[0], refdate=value[1]))
        else:
            value = self._cvt_to_datetime(self.compute_date(value))
        if PY2 and isinstance(value, datetime) and fmt == "cmd":     # pragma: no cover
            value = datetime.strftime(value, "%Y-%m-%d %H:%M:%S")
        return value

    def _convert_datetime_to_write(self, record, field, value):
        return self._cvt_to_datetime(value)

    # -----------------------------
    # --  Type <date> functions  --
    # -----------------------------
    # Return date (cast / upgrade)
    # Return date (convert Odoo 11+) or string (convert Odoo 10-)

    def _cvt_to_date(self, value):
        if isinstance(value, datetime):
            value = value.date()
        elif isinstance(value, basestring):
            value = datetime.strptime(value[:10], "%Y-%m-%d").date()
        return value

    def _cast_field_date(self, resource, field, value, fmt=None, group=None):
        if isinstance(value, (list, tuple)) and fmt:
            value = self._cvt_to_date(self.compute_date(value[0], refdate=value[1]))
        else:
            value = self._cvt_to_date(self.compute_date(value))
        if PY2 and isinstance(value, date) and fmt == "cmd":         # pragma: no cover
            value = datetime.strftime(value, "%Y-%m-%d")
        return value

    def _convert_date_to_write(self, record, field, value):
        return self._cvt_to_date(value)

    # -------------------------------
    # --  Type <binary> functions  --
    # -------------------------------
    # Return base64 (binary data) or string (filename with len<=64)

    def _get_binary_filename(self, xref, bin_types=None):
        binary_root = get_module_resource(self.module.name, "tests", "data")
        if not bin_types:
            binary_file = os.path.join(binary_root, xref)
            if os.path.isfile(binary_file):
                return binary_file
        bin_types = bin_types or ["png", "jpg", "xml"]
        if not is_iterable(bin_types):
            bin_types = [bin_types]  # pragma: no cover
        for btype in bin_types:
            binary_file = os.path.join(binary_root, "%s.%s" % (xref, btype))
            if os.path.isfile(binary_file):
                return binary_file
        return False  # pragma: no cover

    def _get_binary_contents(self, value):
        if (
            not isinstance(value, basestring)
            or (PY3 and isinstance(value, bytes))
            or len(value) > 64
        ):
            return value
        bin_file = self._get_binary_filename(value)
        if bin_file:
            with open(bin_file, "rb") as fd:
                bin_contents = python_plus._b(fd.read())
            return base64.b64encode(bin_contents)
        return False  # pragma: no cover

    def _cast_field_binary(self, resource, field, value, fmt=None, group=None):
        bin_contents = self._get_binary_contents(value)
        if bin_contents:
            value = bin_contents
        else:
            value = None
        return value

    # ---------------------------------
    # --  Type <many2one> functions  --
    # ---------------------------------
    # Return int (fmt), string (for xref before bind)

    def _cast_field_many2one(self, resource, field, value, fmt=None, group=None):
        if isinstance(value, basestring):
            value = self._get_xref_id(
                self.struct[resource][field].get("relation", resource),
                value,
                fmt=fmt,
                group=group,
            )
        elif (
            fmt in ("cmd", "py", "id")
            and not isinstance(value, (int, long))
            and is_iterable(value)
            and "id" in value
        ):
            # Odoo 14.0 NewId requires origin
            value = value.id if isinstance(value.id, (int, long)) else value.id.origin
        return value if value else None

    def _convert_many2one_to_write(self, record, field, value):
        if not value:
            return None
        # Odoo 14.0 NewId requires origin
        return value.id if isinstance(value.id, (int, long)) else value.id.origin

    # -----------------------------------------------
    # --  Type <one2many> / <many2many> functions  --
    # -----------------------------------------------
    # Return [*] (fmt), string (for xref before bind)

    def _value2dict(self, resource, value, fmt=None, group=None, field2rm=None):
        if isinstance(value, dict):
            return self._purge_values(
                self.cast_types(resource, value, fmt=fmt), fieldname=field2rm)
        elif isinstance(value, basestring):
            return self._purge_values(
                self.cast_types(
                    resource,
                    self.get_resource_data(resource, value, group=group),
                    fmt=fmt,
                    group=group,
                ),
                fieldname=field2rm
            )
        return value                                                 # pragma: no cover

    def _cast_2many(self, resource, field, value, fmt=None, group=None, levl=0):
        """ "One2many and many2many may have more representations.
        standard Odoo 2many:

        * [0, 0, values (dict)]               # CREATE record and link
        * [1, ID (int), values (dict)]        # UPDATE linked record
        * [2, ID (int)]                       # DELETE linked record by ID
        * [3, ID (int)]                       # UNLINK record ID (do not delete record)
        * [4, ID (int)]                       # LINK record by ID
        * [5, x] or [5]                       # CLEAR unlink all record IDs
        * [6, x, IDs (list)]                  # SET link record IDs

        TestEnv accepts external reference (str) to replace every int or dict value.

        Please, read cast_types docs, about value casting.
        """

        def mergelist(value):
            # itertool.chain.from_iterable cannot work with [int, int, ...]
            res = []
            for item in value:
                if hasattr(item, "__iter__"):
                    for x in mergelist(item):
                        res.append(x)
                else:
                    res.append(item)
            return res

        def value2list(value):
            if isinstance(value, basestring):
                value = [x for x in value.split(",")]
            elif not is_iterable(value):
                value = [value]
            return value

        res = []
        is_cmd = False
        items = value2list(value)
        child_resource = self.struct[resource][field].get("relation", resource)
        if levl == 1:
            if (
                    len(items) == 3
                    and items[0] in (0, 1)
                    and isinstance(items[1], (int, long))
            ):
                # (0|1,x,dict) -> (0|1,x,dict) / dict
                # (0|1,x,xref) -> (0|1,x,dict) / dict
                res1 = self._value2dict(
                    child_resource,
                    items[2], fmt="id" if fmt else None,
                    field2rm=self.parent_name.get(child_resource))
                res = (items[0], items[1], res1) if fmt in ("cmd", None) else res1
                is_cmd = True
                items = []
            elif len(items) == 2 and items[0] in (2, 3, 4, 5):
                # (2|3|4|5,id)  -> as is
                # (2|3|4|5,xref) -> (2|3|4|5,int)
                res = (
                    items[0],
                    self._cast_field_many2one(
                        resource, field, items[1], fmt="id" if fmt else None)
                )
                is_cmd = True
                items = []
            elif len(items) == 3 and items[0] == 6 and items[1] == 0:
                # (6,0,ids)        -> as is
                # (6,0,xref)       -> (6,0,[id]) / [id]
                # (6,0,[xref,...]) -> (6,0,[ids])  / [ids]
                res1 = mergelist(self._cast_2many(
                    resource, field, items[2],
                    fmt="id" if fmt else None, levl=levl + 1))
                res = (items[0], items[1], res1) if fmt in ("cmd", None) else res1
                is_cmd = True
                items = []
        elif levl == 0 and isinstance(items, dict):
            # dict  -> [(0,0,dict)]  / [dict]
            res1 = self.cast_types(resource, items, fmt="cmd" if fmt else None)
            if res1:
                res.append((0, 0, res1) if fmt == "cmd" else res1)
            is_cmd = True
            items = []
        for item in items:
            if isinstance(item, basestring):
                # xref (exists)           -> (6,0,[id])       / [id]
                # xref (not exists)       -> (0,0,dict)       / dict
                xid = self._get_xref_id(child_resource, item, fmt=fmt, group=group)
                if not xid and self.get_resource_data(child_resource, item):
                    res1 = self._value2dict(
                        child_resource,
                        item,
                        fmt="cmd" if fmt else None,
                        field2rm=self.parent_name.get(child_resource))
                    if res1:
                        res.append((0, 0, res1) if fmt == "cmd" else res1)
                elif xid == item and fmt:                            # pragma: no cover
                    self.raise_error("Unknown value %s of %s" % (item, items))
                elif xid:
                    res.append((6, 0, [xid]) if fmt == "cmd" else xid)
                is_cmd = True
                levl = 0
            elif isinstance(item, dict):
                # dict  -> (0,0,dict)  / dict
                res1 = self.cast_types(child_resource, item, fmt="cmd" if fmt else None)
                if res1:
                    res.append((0, 0, res1) if fmt == "cmd" else res1)
                is_cmd = True
                levl = 0
            elif isinstance(item, (list, tuple)) and levl == 0:
                # [xref] (exists)         -> (6,0,[id])       / [id]
                # [xref] (not exists)     -> (0,0,dict)       / dict
                # [xref,...] (exists)     -> (6,0,[ids])      / [ids]
                # [xref,...] (not exists) -> (0,0,dict),(...) / dict,...
                res.append(self._cast_2many(
                    resource, field, item, group=group, fmt=fmt, levl=levl + 1))
            elif isinstance(item, (list, tuple)) and levl > 0:
                # '§(6,0,§ ids )'         -> ids
                res.append(self._cast_2many(
                    resource, field, item, group=group, fmt="id", levl=levl + 1))
            # elif isinstance(item, (int, long)) and levl == 0:
            #     res.append((4, item) if fmt == "cmd" else item)
            else:
                res.append(item)

        if len(res):
            if (
                levl == 0 and fmt == "cmd" and not is_cmd
                and all([isinstance(x, (int, long)) for x in items])
            ):
                res = [(6, 0, res)]
            elif (levl == 0 and fmt == "cmd" and len(res) > 1
                  and all([isinstance(x, (list, tuple)) and x[0] == 6 and x[1] == 0
                           for x in res])):
                res = [(6, 0, mergelist([x[2] for x in res]))]
            elif levl == 1 and not is_cmd:
                if fmt == "cmd":
                    if isinstance(res[0], dict):
                        res = (0, 0, res)
                    else:
                        res = (6, 0, res)
                elif fmt == "py":
                    ids = res[2:] if levl >= 0 and res[0] in (0, 1, 6) else res
                    res = self.env[resource]
                    if self.odoo_major_version <= 7:
                        for id in ids:
                            res |= self.registry(resource).browse(self.cr, self.uid, id)
                    else:
                        for id in ids:
                            res |= self.env[resource].browse(id)
        else:
            res = False
            if fmt:
                self._logger.info("⚠ No *2many value for %s.%s" % (resource, value))
        return res

    def _cast_field_one2many(self, resource, field, value, fmt=None, group=None):
        value = self._cast_2many(
            resource,  # self.struct[resource][field]["relation"],
            field,
            value,
            fmt=fmt,
            group=group,
        )
        if not value:
            value = None
        return value

    def _cast_field_many2many(self, resource, field, value, fmt=None, group=None):
        return self._cast_2many(
            resource,  # self.struct[resource][field]["relation"],
            field,
            value,
            fmt=fmt,
            group=group
        )

    def _convert_one2many_to_write(self, record, field, value):
        if value:
            return [(6, 0, [
                x.id if isinstance(x.id, (int, long)) else x.id.origin
                for x in value])]
        return False

    def _convert_many2many_to_write(self, record, field, value):
        return self._convert_one2many_to_write(record, field, value)

    # -------------------------------------
    # --  ir.model / resource functions  --
    # -------------------------------------

    def cast_types(self, resource, values, fmt=None, group=None):
        """Convert resource fields in appropriate type, based on Odoo type.
        The parameter fmt declares the purpose of casting: 'cmd' means convert to Odoo
        API format; <2many> fields are prefixed with 0|1|2|3|4|5|6 value (read
        _cast_2many docs).
        'id' is like 'cmd': prefix are added inside dict not at the beginning.
        'py' means convert to native python (remove all Odoo command prefixes). It is
        used for comparison.
        When no format is required (fmt=None), some conversion may be not applicable:
        <many2one> field will be left unchanged when invalid xref is issued and <2many>
        field me will be left unchanged when one or more invalid xref are issued.
        str, int, long, selection, binary, html fields are always left as is
        date, datetime fields and fmt=='cmd' and python2 (odoo 10.0-) return ISO format
        many2one fields, if value is (int|long) are left as is; if value is (xref) the
        id of xref is returned.
                                        | fmt=='cmd'         | fmt=='id'  | fmt=='py'
        <2many> [(0|1,x,dict)]          | [(0|1,x,dict)] *   | [dict] *   | [dict] *
        <2many> [(0|1,x,xref)]          | [(0|1,x,dict)]     | [dict]     | [dict]
        <2many> [(2|3|4|5,id)]          | as is              | as is      | as is
        <2many> [(2|3|4|5,xref)]        | [(2|3|4|5,id)]     | as is      | as is
        <2many> [(6,0,[ids])]           | as is              | [ids]      | [ids]
        <2many> [(6,0,xref)]            | [(6,0,[id])]       | [id]       | [id]
        <2many> [(6,0,[xref,...])]      | [(6,0,[ids])]      | [ids]      | [ids]
        <2many> dict                    | [(0,0,dict)        | [dict]     | [dict]
        <2many> xref (exists)           | [(6,0,[id])]       | [id]       | [id]
        <2many> xref (not exists)       | [(0,0,dict)]       | [dict]     | [dict]
        <2many> [xref] (exists)         | [(6,0,[id])]       | [id]       | [id]
        <2many> [xref] (not exists)     | [(0,0,dict)]       | [dict]     | [dict]
        <2many> [xref,...] (exists)     | [(6,0,[ids])]      | [ids]      | [ids]
        <2many> [xref,...] (not exists) | [(0,0,dict),(...)] | [dict,...] | [dict,...]
        <2many> [ids] **                | [(6,0,[ids])]      | [ids]      | [ids]
        <2many> id                      | [(6,0,[id])]       | [id]       | [id]
        <2many> "xref,..." (exists)     | [(6,0,[ids])]      | [ids]      | [ids]
        <2many> "xref,..." (not exists) | [(0,0,dict),(...)] | [dict,...] | [dict,...]
        Caption: dict -> {'a': 'A', ..}, xref -> "abc.def", id -> 10, ids -> 1,2,...
        * fields of dict are recursively processed
        ** ids 1-6 have processed as Odoo cmd
        Notice: Odoo one2many valid cmd are: 0,1 and 2 (not checked)

        Args:
            resource (str): Odoo model name
            values (dict): record data
            fmt (selection): output format (read above)
            group (str): used to manager group data; default is "base"

        Returns:
            Appropriate values
        """
        if not isinstance(values, dict):
            self.raise_error(
                "Invalid dict %s for %s!"
                % (values, resource)  # pragma: no cover
            )
        if values:
            self._load_field_struct(resource)
            values = self._get_conveyed_value(resource, "all", values, fmt=fmt)
            for field in [x for x in list(values.keys())]:
                if field not in self.struct[resource]:
                    del values[field]
                    self.log_lvl_2(
                        " 🕶️ field %s does not exist in %s" % (field, resource))
                    continue

                value = self._cast_field(
                    resource, field, values[field], fmt=fmt, group=group
                )
                if value is None:
                    del values[field]
                    if field != "id":
                        self.log_lvl_3(" 🕶️ del %s.vals[%s]" % (resource, field))
                    continue
                values[field] = value
            if not values:  # pragma: no cover
                self.log_lvl_2(" 🕶️ %s.cast_type() = {}" % resource)

        return values

    def _convert_to_write(self, record, new=None, orig=None):
        values = {}
        for field in list(record._fields.keys()):
            if (
                field in BLACKLIST_COLUMNS
                or record._fields[field].readonly
            ):
                continue
            value = self._convert_field_to_write(record, field)
            if value is None:  # pragma: no cover
                continue
            elif value is False:
                if new or (orig and value == self._convert_field_to_write(orig, field)):
                    continue
                values[field] = value
            elif not orig or value != self._convert_field_to_write(orig, field):
                values[field] = value
        return values

    def _upgrade_record(self, record, values, default={}):
        for field in list(values.keys()):
            if field in SUPERMAGIC_COLUMNS:  # pragma: no cover
                continue
            if field not in default:
                method = "_upgrade_field_%s" % record._fields[field].type
                method = method if hasattr(self, method) else "_upgrade_field_base"
                value = getattr(self, method)(record, field, values[field])
                # if not value and default.get(field):
                #     value = getattr(self, method)(record, field, default[field])
                if value is not None:
                    setattr(record, field, value)
        return record

    def _purge_values(self, values, timed=None, fieldname=None):
        for field in BITTER_COLUMNS + [fieldname]:
            if field in values:
                del values[field]
        if timed:  # pragma: no cover
            for field in LOG_ACCESS_COLUMNS:
                if field in values:
                    del values[field]
        return values

    # --------------------------------------
    # --  Wizard/Form internal functions  --
    # --------------------------------------

    def _ctx_active_ids(self, records, ctx={}):
        if records:
            if is_iterable(records):
                ctx["active_ids"] = [x.id for x in records]
                if len(records) == 1:
                    ctx["active_id"] = records[0].id
                else:
                    ctx["active_id"] = False
            else:
                ctx["active_id"] = records.id
        return ctx

    def _finalize_ctx_act_windows(self, records, act_windows, ctx={}):
        if isinstance(act_windows.get("context"), basestring):
            _ctx = self.env["ir.actions.actions"]._get_eval_context()
            _ctx.update(self._ctx_active_ids(records, ctx))
            _ctx.update(safe_eval(act_windows["context"], _ctx))
            act_windows["context"] = _ctx
            if (
                self.odoo_major_version < 13
                and isinstance(records, (int, long)) != act_windows["multi"]
            ):
                self._logger.info("⚠ act_windows['multi'] does not match # of records!")
        elif "context" not in act_windows:
            act_windows["context"] = {}

    def _create_object(self, resource, default={}, origin=None, ctx={}):
        if self.odoo_major_version < 13:
            if ctx:
                record = self.env[resource].with_context(ctx).new(values=default)
            else:
                record = self.env[resource].new(values=default)
            if origin:
                record._origin = origin
            else:
                record._origin = self.env[resource].with_context(ctx)
        else:
            if ctx:
                record = self.env[resource].with_context(ctx).new(
                    values=default,
                    origin=origin or self.env[resource].with_context(ctx))
            else:
                record = self.env[resource].new(
                    values=default,
                    origin=origin or self.env[resource].with_context(ctx))
        if hasattr(record, "default_get"):
            self._upgrade_record(
                record, record.default_get(record.fields_get_keys()), default
            )
        for field in record._onchange_methods.values():
            for method in field:
                method(record)
        return record

    def for_xml_id(self, module, name):
        if self.odoo_major_version < 13:
            return self.env["ir.actions.act_window"].for_xml_id(module, name)
        else:
            record = self.env.ref("%s.%s" % (module, name))
            return record.read()[0]

    def _set_origin(self, record, ctx={}):
        resource_model = self._get_model_from_records(record)
        origin = self.env[resource_model]
        if is_iterable(record) and len(record) == 1:
            origin = self._create_object(
                resource_model,
                default=self._convert_to_write(record[0], new=True),
                origin=origin,
                ctx=ctx,
            )
        return origin

    def _exec_action(self, record, action, default={}, web_changes=[], origin=None,
                     ctx={}):
        resource_model = self._get_model_from_records(record)
        origin = origin or self.env[resource_model]
        if isinstance(record, basestring):
            record = self._create_object(
                resource_model,
                default=self.cast_types(resource_model, default or {}, fmt="cmd"),
                origin=origin,
                ctx=ctx,
            )
        elif is_iterable(record):
            if not self._is_transient(origin):
                if not isinstance(record, (list, tuple)):
                    _ctx = self.env["ir.actions.actions"]._get_eval_context()
                    _ctx.update(self._ctx_active_ids(record, ctx))
                    record = record.with_context(_ctx)
                if not origin or origin._name != resource_model:
                    origin = self._set_origin(record, ctx=ctx)
        if self._is_transient(origin) and action in ("save", "create", "discard"):
            self.raise_error(
                "Invalid action %s for %s!"
                % (action, resource_model)  # pragma: no cover
            )
        self._load_field_struct(resource_model)
        for args in web_changes:
            self._wiz_edit(
                record,
                resource_model,
                args[0],
                args[1],
                args[2] if len(args) > 2 else None,
            )
        if action == "save":
            vals = self._convert_to_write(record, orig=origin)
            record.write(vals)
            return record
        elif action == "create":
            vals = self._convert_to_write(record, new=True)
            record.unlink()
            return self.env[resource_model].create(vals)
        elif action == "discard":
            return False  # pragma: no cover
        elif action and hasattr(record, action):
            self.log_lvl_2("🚴‍♂️  %s.%s()" % (resource_model, action))
            act_windows = getattr(record, action)()
            # Weird bug: this is a workaround!!!
            if action == "action_invoice_draft" and record.state != "draft":
                record.state = "draft"
            elif action == "action_invoice_open" and record.state != "open":
                record.state = "open"
        elif self._is_xref(action):
            module, name = action.split(".", 1)
            act_windows = self.for_xml_id(module, name)
            self.log_lvl_2("🐜  act_windows(%s)" % action)
            self._finalize_ctx_act_windows(record, act_windows)
        else:  # pragma: no cover
            self.raise_error(
                "Invalid action %s for %s!"
                % (action, resource_model)  # pragma: no cover
            )
        return act_windows

    def _get_model_from_act_windows(self, act_windows):
        return act_windows.get(
            "model_name", act_windows.get("res_model", act_windows.get("model"))
        )

    def _get_src_model_from_act_windows(self, act_windows):
        model_name = act_windows.get("src_model")
        if not model_name and act_windows.get("binding_model_id"):
            model_name = self.env.ref(act_windows["binding_model_id"])["model"]
        if not model_name or self._is_transient(model_name):
            model_name = None
            value = "%s,%d" % (act_windows["type"], act_windows["id"])
            if "ir.values" in self.env:
                records = self.env["ir.values"].search([("value", "=", value)])
                if len(records) == 1:
                    model_name = records[0].model
        return model_name

    def _get_model_from_records(self, records):
        if not records:  # pragma: no cover
            resource_model = None
        elif isinstance(records, basestring):
            resource_model = records
        elif isinstance(records, (list, tuple)):
            resource_model = records[0]._name
        else:
            resource_model = records._name
        return resource_model

    def _wiz_launch(self, act_windows, records=None, default=None, ctx={}):
        """Start a wizard from a windows action.

        This function simulates the wizard or action server starting web interface.
        It creates the wizard record with default values.
        It is useful to test:
            * view names
            * wizard structure
            * wizard code

        Args:
            act_windows (dict): Odoo windows action
            records (obj): objects required by action server
            default (dict): default value to assign
            ctx (dict): context to pass to wizard during execution

        Returns:
            Odoo windows action to pass to wizard execution
        """
        if not isinstance(act_windows, dict):  # pragma: no cover
            self.raise_error("Invalid act_windows")
        self.log_lvl_2("🐞wizard starting(%s)" % act_windows.get("name"), strict=True)
        self.log_lvl_3(
            "🐞wizard starting(%s,%s,\nrec=%s,\ndef=%s,\nctx=%s)"
            % (
                act_windows.get("name"),
                self.dict_2_print(act_windows),
                self.dict_2_print(records),
                self.dict_2_print(default),
                self.dict_2_print(ctx),
            ),
            strict=True,
        )
        if (
            records
            and isinstance(records, (list, tuple))
            and any([isinstance(x, (list, tuple)) for x in records])
        ):  # pragma: no cover
            self.raise_error("Invalid records type issued!")
        self._finalize_ctx_act_windows(records, act_windows, ctx)
        if ctx and ctx.get("res_id"):
            act_windows["res_id"] = ctx.pop("res_id")

        if records:
            # The record type have to be the same of the action windows model
            # Warning: action windows may not contain any model declaration
            # Please, do not remove test, because if model is declared in action windows
            # must match with record model type
            rec_model = self._get_model_from_records(records)
            act_model = self._get_model_from_act_windows(act_windows)
            src_model = self._get_src_model_from_act_windows(act_windows)
            if src_model:
                # Check only for Odoo 10.0-
                if rec_model != src_model:  # pragma: no cover
                    self.raise_error(
                        "Records model %s differs from declared model %s in %s"
                        % (rec_model, src_model, act_model)
                    )
                if (
                    act_model != src_model
                    and self._is_transient(act_model)
                    and not act_windows.get("src_model")
                ):  # pragma: no cover
                    self.log_lvl_1(
                        "💡 You should specify the src_model %s for the action %s"
                        % (src_model, act_windows.get("name"))
                    )
                    act_windows["src_model"] = src_model
            if "active_ids" not in act_windows["context"]:
                act_windows["context"].update(
                    self._ctx_active_ids(records, ctx=act_windows["context"])
                )
            if not is_iterable(records):                             # pragma: no cover
                records = [records]
        if act_windows["type"] == "ir.actions.server":               # pragma: no cover
            if not records:
                self.raise_error("No any records supplied")
        else:
            res_model = self._get_model_from_act_windows(act_windows)
            vals = self.cast_types(res_model, default or {}, fmt="cmd")
            res_id = act_windows.get("res_id")
            if res_id and isinstance(res_id, (int, long)):
                wizard = (
                    self.env[res_model]
                    .with_context(act_windows["context"])
                    .browse(res_id)
                )
            else:
                wizard = (
                    self.env[res_model]
                    .with_context(act_windows["context"])
                    .create(
                        self._purge_values(
                            self._convert_to_write(
                                self._create_object(
                                    res_model, default=vals, ctx=act_windows["context"]
                                ),
                                new=True,
                            )
                        )
                    )
                )
                act_windows["res_id"] = wizard.id
        act_windows["res_id"] = wizard.id
        # Save wizard for furthermore use
        act_windows["_wizard_"] = wizard
        if act_windows.get("view_id"):
            # This code is just executed to test valid view structure
            self.env["ir.ui.view"].browse(act_windows["view_id"])  # pragma: no cover
        return act_windows

    def _wiz_launch_by_act_name(
        self,
        module,
        action_name,
        records=None,
        default=None,
        ctx={},
    ):
        """Start a wizard from an action name.

        Validate the action name for xml view file, then call <wizard_start>

        *** Example ***

        XML view file:
            <record id="action_example" model="ir.actions.act_window">
                <field name="name">Example</field>
                <field name="res_model">wizard.example</field>
                [...]
            </record>

        Python code:
            act_windows = self.wizard_start_by_act_name(
                "module_example",   # Module name
                "action_example",   # Action name from xml file
            )

        Args:
            module (str): module name with wizard to test
            action_name (str): action name
            records (obj): objects supplied for action server

        Returns:
            Same of <wizard_start>
        """
        # act_model = "ir.actions.act_window"
        module = self.module.name if module == "." else module
        try:
            act_windows = self.for_xml_id(module, action_name)
        except BaseException:
            # if not records or len(records) != 1:
            self.raise_error(
                "Invalid action_name %s" % action_name)
        return self._wiz_launch(
            act_windows,
            default=default,
            ctx=ctx,
            records=records,
        )

    def _wiz_edit(self, wizard, resource, field, value, onchange=None):
        """Simulate view editing on a field.

        Assign value to field, then engage all onchange functions on current field and
        on all updated fields.
        Finally, run onchange function issued by caller.
        Internal function of <wizard_execution>

        Args:
            wizard (object): execution wizard image
            field (str): field name which value is to assign
            value (any): value to assign to field; if None no assignment is made
            onchange (str): onchange function to execute after assignment

        Returns:
            None
        """
        self.log_lvl_3("🐜  %s.onchange(%s=%s)" % (wizard, field, value))
        cur_vals = {}
        for name in wizard._fields.keys():
            if name not in SUPERMAGIC_COLUMNS:
                try:
                    cur_vals[name] = getattr(wizard, name)
                except BaseException:
                    self.raise_error(
                        "Wrong compute for %s.%s! Forgot @multi?" % (wizard._name,
                                                                     name))
        value = self._cast_field(resource, field, value, fmt="id")
        if value is not None:
            if wizard._fields[field].type in ("one2many", "many2many"):
                setattr(wizard, field, False)
            setattr(wizard, field, value)
        user_act = True
        while user_act:
            user_act = False
            for field in wizard._fields.keys():
                if (
                    field not in SUPERMAGIC_COLUMNS
                    and cur_vals[field] != getattr(wizard, field)
                    and field in wizard._onchange_methods
                ):
                    user_act = True
                    for method in wizard._onchange_methods[field]:
                        method(wizard)
                cur_vals[field] = getattr(wizard, field)
        if onchange:  # pragma: no cover
            getattr(wizard, onchange)()

    def _wiz_execution(
        self,
        act_windows,
        button_name=None,
        web_changes=[],
        button_ctx={},
    ):
        """Simulate wizard execution issued by an action."""
        self.log_lvl_3(
            " 🐜 wizard running(%s, %s)"
            % (act_windows.get("name"), self.dict_2_print(act_windows))
        )
        wizard = act_windows.pop("_wizard_")
        if button_name:
            return self._exec_action(wizard, button_name, web_changes=web_changes)
        return False

    #############################################
    #                                           #
    #     MODEL/FIELDS ENVIRONMENT TEST API     #
    #                                           #
    #############################################

    def store_resource_data(self, resource, xref, values, group=None, name=None):
        """Store a record data definition for furthermore use.
        Data stored is used by setup_env() function and/or by:

        * resource_create() without values
        * resource_write() without values
        * resource_make() without values

        Args:
            resource (str): Odoo model name
            xref (str): external reference
            values (dict): record data
            group (str): used to manager group data; default is "base"
            name (str): label of dataset; default is resource name
        """
        group = self.u(group) or "base"
        name = self.u(name) or self.u(resource)
        xref = self._get_conveyed_value(resource, None, xref)
        if resource == "account.account" and "code" not in values:
            record = self.env.ref(xref, raise_if_not_found=False)
            if record:
                values["code"] = record.code
        if group not in self.setup_data_list:
            self.setup_data_list[group] = []
            self.setup_data[group] = {}
        if name not in self.setup_data[group]:
            self.setup_data[group][name] = {}
        resource_child = self.childs_resource.get(resource)
        if resource_child:
            field_child = self.childs_name.get(resource)
            child_values = [
                x for x in self.get_resource_data_list(resource_child, group=group)
                if x.startswith(xref)
            ]
            if child_values:
                values[field_child] = child_values
        self.setup_data[group][name][xref] = self._purge_values(
            self.cast_types(resource, values, group=group)
        )
        self.log_lvl_2(
            "💼 %s.store_resource_data(%s,name=%s,group=%s)"
            % (resource, xref, name, group)
        )
        resource_parent = self.parent_resource.get(resource)
        if (
            resource_parent
            and resource_parent in self.setup_data[group]
            and self.childs_name.get(resource_parent)
        ):
            field_child = self.childs_name[resource_parent]
            xref_parent, ln = self._unpack_xref(xref)
            if xref_parent in self.setup_data[group][resource_parent]:
                parent = self.setup_data[group][resource_parent][xref_parent]
                if field_child not in parent:
                    parent[field_child] = []
                if xref not in parent[field_child]:
                    parent[field_child].append(xref)
            if isinstance(ln, (int, long)) and "sequence" in self.struct[resource]:
                self.setup_data[group][name][xref]["sequence"] = ln
        if name not in self.setup_data_list[group]:
            self.setup_data_list[group].append(name)
        self.setup_xrefs[xref] = (group, resource)

    def default_company(self):
        return self.env.user.company_id

    def compute_date(self, date, refdate=None):
        """Compute date

        Args:
            date (date or string or integer): formula
            refdate (date or string): reference date

        Returns:
            ISO format string with result date
        """
        return python_plus.compute_date(self.u(date), refdate=self.u(refdate))

    def resource_browse(self, xref, raise_if_not_found=True, resource=None, group=None):
        """Bind record by xref or searching it or browsing it.
        This function returns a record using issued parameters. It works in follow ways:

        * With valid xref it work exactly like self.env.ref()
        * If xref is an integer it works exactly like self.browse()
        * I xref is invalid, xref is used to search record
            * xref is searched in stored data
            * xref ("MODULE.NAME"): if MODULE == "external", NAME is the record key

        Args:
            xref (str): external reference
            raise_if_not_found (bool): raise exception if xref not found or
                                       if more records found
            resource (str): Odoo model name, i.e. "res.partner"
            group (str): used to manager group data; default is "base"

        Returns:
            obj: the Odoo model record

        Raises:
            ValueError: if invalid parameters issued
        """
        def build_domain(domain, k1, values):
            kk = True
            for field in self.skeys[resource]:
                if k1 and kk:
                    domain.append((field, "=", k1))
                    kk = False
                elif field in values:
                    domain.append((field, "=", self._cast_field(
                        resource, field, values[field], fmt="cmd")))
            if domain and (
                    resource not in RESOURCE_WO_COMPANY
                    and "company_id" in self.struct[resource]
            ):
                domain.append("|")
                domain.append(("company_id", "=", self.default_company().id))
                domain.append(("company_id", "=", False))
            return domain

        self.log_stack()
        self.log_lvl_3("🐞%s.resource_browse(%s)" % (resource, xref))
        # Search for Odoo standard external reference
        record = None
        if isinstance(xref, (int, long)):
            if not resource:  # pragma: no cover
                self.raise_error("No model issued for binding")
                return False
            if self.odoo_major_version <= 7:
                record = self.registry(resource).browse(self.cr, self.uid, xref)
            else:
                record = self.env[resource].browse(xref)
        elif isinstance(xref, basestring):
            record = self.env.ref(
                self._get_conveyed_value(None, None, xref), raise_if_not_found=False
            )
        if record:
            return record
        # Simulate external reference
        if not resource and not group:
            resource = self._get_model_of_xref(xref)
        if not resource:                                             # pragma: no cover
            if raise_if_not_found:
                self.raise_error("No model issued for binding")
            return False
        if resource not in self.env:                                 # pragma: no cover
            if raise_if_not_found:
                self.raise_error("Model %s not found in the system" % resource)
            return False
        self._load_field_struct(resource)
        if resource not in self.skeys:                               # pragma: no cover
            if raise_if_not_found:
                self.raise_error("Model %s without search key" % resource)
            self._logger.info("⚠ Model %s without search key" % resource)
            return False

        values = self.get_resource_data(resource, xref, group=group)
        module, name = xref.split(".", 1)
        parent_name = self.parent_name.get(resource)
        if parent_name and self.parent_resource[resource] in self.childs_resource:
            name, ln = self._unpack_xref(name)
            parent_rec = self.resource_browse(
                "%s.%s" % (module, name),
                resource=self.parent_resource[resource],
                raise_if_not_found=False,
                group=group,
            )
            if not parent_rec:                                       # pragma: no cover
                if raise_if_not_found:
                    self.raise_error(
                        "Parent xref %s.%s not found for %s" % (module, name, resource))
                self._logger.info(
                    "⚠ Parent xref %s.%s not found for %s" % (module, name, resource))
                return False
            domain = [(parent_name, "=", parent_rec.id)]
        else:
            domain = []
            ln = parent_rec = False
        domain = build_domain(domain, ln, values)
        if not domain:                                               # pragma: no cover
            if raise_if_not_found:
                self.raise_error("Invalid search keys %s for model %s"
                                 % (self.skeys[resource], resource))
            self._logger.info("⚠ Invalid search keys %s for model %s"
                              % (self.skeys[resource], resource))
            return False
        record = self.env[resource].search(domain, limit=3)
        if len(record) != 1 and parent_rec and isinstance(ln, (int, long)):
            domain = [(parent_name, "=", parent_rec.id)]
            domain = build_domain(domain, False, values)
            if domain:
                record = self.env[resource].search(domain)
        if len(record) == 1:
            if self.odoo_major_version <= 7:
                return self.registry(resource).browse(self.cr, self.uid, record[0].id)
            return self.env[resource].browse(record[0].id)
        if raise_if_not_found:
            self.raise_error("External ID %s not found" % xref)  # pragma: no cover
        return False

    def resource_create(self, resource, values=None, xref=None, group=None):
        """Create a test record and set external ID to next tests.
        This function works as standard Odoo create() with follow improvements:

        * It can create external reference too
        * It can use stored data if no values supplied
        * Use new api even on Odoo 7.0 or less

        Args:
            resource (str): Odoo model name, i.e. "res.partner"
            values (dict): record data (default stored data)
            xref (str): external reference to create
            group (str): used to manager group data; default is "base"

        Returns:
            obj: the Odoo model record, if created
        """
        self.log_stack()
        self._load_field_struct(resource)
        xref = self._get_conveyed_value(resource, None, xref)
        values = self.unicodes(values)
        if not values and xref:
            values = self.get_resource_data(resource, xref, group=group)
            values = self._add_child_records(resource, xref, values, group=group)
        if not values:  # pragma: no cover
            self.raise_error("No values supplied for %s create" % resource)
        self.log_lvl_3(
            "🐞%s.resource_create(%s,xref=%s)"
            % (resource, self.dict_2_print(values), xref)
        )
        values = self.cast_types(resource, values, fmt="cmd", group=group)
        try:
            if resource.startswith("account.move") and "line_ids" not in values:
                res = (
                    self.env[resource]
                    .with_context(check_move_validity=False)
                    .create(values)
                )
            elif self.odoo_major_version <= 7:
                res = self.registry(resource).browse(
                    self.cr, self.uid,
                    self.registry(resource).create(self.cr, self.uid, values))
            else:
                res = self.env[resource].create(values)
        except BaseException as e:
            self.raise_error("Resource '%s' create error '%s'\n%s"
                             % (resource, e, self.dict_2_print(values)))
            return None
        if self._is_xref(xref):
            self._add_xref(xref, res.id, resource)
            self.store_resource_data(resource, xref, values, group=group)
            (
                resource_child,
                xref_child,
                field_child,
                field_parent,
            ) = self._get_depending_xref(resource, xref)
            if resource_child and xref_child:
                self._add_xref(
                    xref_child, getattr(res, field_child)[0].id, resource_child
                )
                values_child = {k: v for (k, v) in values.items()}
                values_child[field_parent] = res.id
                self.store_resource_data(
                    resource_child, xref_child, values_child, group=group
                )
        return res

    def resource_write(
        self, resource, xref=None, values=None, raise_if_not_found=True, group=None
    ):
        """Update a test record.
        This function works as standard Odoo write() with follow improvements:

        * If resource is a record, xref is ignored (it should be None)
        * It resource is a string, xref must be a valid xref or an integer
        * If values is not supplied, record is restored to stored data values
        * Use new api even on Odoo 7.0 or less

        Args:
            resource (str|obj): Odoo model name or record to update
            xref (str): external reference to update: required id resource is string
            values (dict): record data (default stored data)
            raise_if_not_found (bool): raise exception if xref not found or
                           if more records found
            group (str): used to manager group data; default is "base"

        Returns:
            obj: the Odoo model record

        Raises:
            ValueError: if invalid parameters issued
        """
        self.log_stack()
        if resource is None or isinstance(resource, basestring):
            if not xref and not values:                              # pragma: no cover
                self.raise_error("%s.write() without values and xref" % resource)
            record = self.resource_browse(
                xref,
                resource=resource,
                raise_if_not_found=raise_if_not_found,
                group=group,
            )
        else:
            record = resource
            resource = resource._name
        if record:
            if values:
                values = self.unicodes(values)
            else:
                values = self._purge_values(
                    self.get_resource_data(resource, xref, group=group))
            values = self._add_child_records(resource, xref, values, group=group)
            values = self.cast_types(resource, values, fmt="cmd", group=group)
            self.log_lvl_3(
                "🐞%s.resource_write(%s,%s,xref=%s)"
                % (resource, record.id, self.dict_2_print(values), xref)
            )
            try:
                if resource.startswith("account.move"):
                    record.with_context(check_move_validity=False).write(values)
                elif self.odoo_major_version <= 7:
                    self.registry(resource).write(self.cr, self.uid, [id], values)
                else:
                    record.write(values)
            except BaseException as e:
                self.raise_error("Resource '%s' write error '%s'\n%s"
                                 % (resource, e, self.dict_2_print(values)))

                return None
        return record

    def resource_make(self, resource, xref, values=None, group=None):
        """Create or write a test record.
        This function is a hook to resource_write() or resource_create().
        """
        self.log_stack()
        self.log_lvl_3(
            "🐞%s.resource_make(%s,xref=%s)"
            % (resource, self.dict_2_print(values), xref)
        )
        record = self.resource_write(
            resource, xref, values=values, raise_if_not_found=False, group=group
        )
        if not record:
            record = self.resource_create(
                resource, values=values, xref=xref, group=group
            )
        return record

    def declare_resource_data(self, resource, data, name=None, group=None, merge=None):
        """Declare data to load on setup_env().

        Args:
            resource (str): Odoo model name, i.e. "res.partner"
            data (dict): record data
            name (str): label of dataset; default is resource name
            group (str): used to manager group data; default is "base"
            merge (str): merge data with public data (currently just "zerobug")

        Raises:
            TypeError: if invalid parameters issued
        """
        if not isinstance(data, dict):  # pragma: no cover
            self.raise_error("Dictionary expected")
        if merge and merge != "zerobug":  # pragma: no cover
            self.raise_error("Invalid merge value: please use 'zerobug'")
        data = self.unicodes(data)
        for xref in list(sorted(data.keys())):
            if merge == "zerobug":
                zerobug = z0bug_odoo_lib.Z0bugOdoo().get_test_values(resource, xref)
                for field in list(zerobug.keys()):
                    if (
                        field not in data[xref]
                        and zerobug[field]
                        and zerobug[field] not in ("None", r"\N")
                    ):
                        data[xref][field] = zerobug[field]
            tnxl_xref = self._get_conveyed_value(None, None, xref)
            if tnxl_xref != xref:
                data[tnxl_xref] = self.unicodes(data[xref])
                del data[xref]
            else:
                data[xref] = self.unicodes(data[xref])
            self.store_resource_data(
                resource, xref, data[tnxl_xref], group=group, name=name
            )

    def declare_all_data(self, message, group=None, merge=None):
        """Declare all data to load on setup_env().

        Args:
            message (dict): data message
                TEST_SETUP_LIST (list): resource list to load
                TEST_* (dict): resource data; * is the uppercase resource name where
                               dot are replaced by "_"; (see declare_resource_data)
            group (str): used to manager group data; default is "base"
            merge (str): merge data with public data (currently just "zerobug")

        Raises:
            TypeError: if invalid parameters issued
        """
        self.log_stack()
        if not isinstance(message, dict):  # pragma: no cover
            self.raise_error("Dictionary expected")
        if "TEST_SETUP_LIST" not in message:  # pragma: no cover
            self.raise_error("Key TEST_SETUP_LIST not found")
        group = group or "base"
        for resource in message["TEST_SETUP_LIST"]:
            item = "TEST_%s" % resource.upper().replace(".", "_")
            if item not in message:  # pragma: no cover
                self.raise_error("Key %s not found" % item)
        for resource in message["TEST_SETUP_LIST"]:
            self.log_lvl_1(" 🐜 declare_all_data(%s,group=%s)" % (resource, group))
            item = "TEST_%s" % resource.upper().replace(".", "_")
            self.declare_resource_data(
                resource, message[item], group=group, merge=merge
            )

    def get_resource_data(self, resource, xref, group=None, try_again=True):
        """Get declared resource data; may be used to test compare.

        Args:
            resource (str): Odoo model name or name assigned, i.e. "res.partner"
            xref (str): external reference
            group (str): if supplied select specific group data; default is "base"

        Returns:
            dictionary with data or empty dictionary
        """
        if try_again:
            xref = self._get_conveyed_value(resource, None, xref)
        group = group or "base"
        if (
            group in self.setup_data
            and resource and resource in self.setup_data[group]
            and xref in self.setup_data[group][resource]
        ):
            return self.setup_data[group][resource][xref]
        if try_again and xref in self.setup_xrefs:
            group, resource = self.setup_xrefs[xref]
            return self.get_resource_data(resource, xref, group=group, try_again=False)
        return {}  # pragma: no cover

    def get_resource_data_list(self, resource, group=None):
        """Get declared resource data list.

        Args:
            resource (str): Odoo model name or name assigned, i.e. "res.partner"
            group (str): if supplied select specific group data; default is "base"

        Returns:
            list of data
        """
        group = group or "base"
        if group in self.setup_data and resource in self.setup_data[group]:
            return list(self.setup_data[group][resource].keys())
        return []  # pragma: no cover

    def get_resource_list(self, group=None):
        """Get declared resource list.

        Args:
            group (str): if supplied select specific group data; default is "base"
        """
        group = group or "base"
        if group in self.setup_data_list:
            return self.setup_data_list[group]
        return []  # pragma: no cover

    def set_locale(self, locale_name, raise_if_not_found=True):
        modules_model = self.env["ir.module.module"]
        modules = modules_model.search([("name", "=", locale_name)])
        if modules and modules[0].state != "uninstalled":
            modules = []
        if modules:
            modules.button_immediate_install()
            self.env["account.chart.template"].try_loading_for_current_company(
                locale_name
            )
        else:
            if raise_if_not_found:
                self.raise_error("Module %s not found in the system" % locale_name)

    def install_language(self, iso, overwrite=None, force_translation=None):
        iso = iso or "en_US"
        overwrite = overwrite or False
        load = False
        lang_model = self.env["res.lang"]
        languages = lang_model.search([("code", "=", iso)])
        if not languages:  # pragma: no cover
            languages = lang_model.search([("code", "=", iso), ("active", "=", False)])
            if languages:
                languages.write({"active": True})
                load = True
        if not languages or load:
            vals = {
                "lang": iso,
                "overwrite": overwrite,
            }
            self.env["base.language.install"].create(vals).lang_install()
        if force_translation:
            vals = {"lang": iso}
            self.env["base.update.translations"].create(vals).act_update()

    def setup_company(
        self,
        company,
        xref=None,
        partner_xref=None,
        recv_xref=None,
        pay_xref=None,
        bnk1_xref=None,
        values={},
        group=None,
    ):
        """Setup company values for current user.
        This function assigns company to current user and / or can create xref aliases
        and /or can update company values.
        This function is useful in multi companies tests where different company values
        will be used in different tests. May be used in more simple test where company
        data will be updated in different tests.
        You can assign partner_xref to company base by group; then all tests executed
        after setup_env(), use the assigned partner data for company of the group.
        You can also create more companies and assign one of them to test by group.

        Args:
            company (obj): company to update; if not supplied a new company is created
            xref (str): external reference or alias for main company
            partner_xref (str): external reference or alias for main company partner
            bnk1_xref (str): external reference or alias for 1st liquidity bank
            values (dict): company data to update immediately
            group (str): if supplied select specific group data; default is "base"

        Returns:
            default company for user
        """
        def store_acc_alias(xref, acc_type, chart_name):
            if chart_name.endswith("_prefix"):
                acc_code = getattr(chart_template, chart_name)
            else:
                acc_code = getattr(chart_template, chart_name).code
            acc_ids = self.env["account.account"].search(
                [
                    (
                        "user_type_id",
                        "=",
                        self.env.ref(acc_type).id,
                    ),
                    ("code", "like", acc_code),
                ]
            )
            self._add_xref(xref, acc_ids[0].id, "account.account")

        self.log_stack()
        add_alias = True
        if not company:  # pragma: no cover
            company = self.env["res.company"].create(values)
            add_alias = True
        elif values:
            company.write(self.cast_types("res.company", values, fmt="cmd"))
        chart_template = self.env["account.chart.template"].search(
            [("id", "=", company.chart_template_id.id)]
        )
        if xref:
            if not add_alias:
                self.add_xref(xref, "res.company", company.id)  # pragma: no cover
            elif not self.env.ref(xref, raise_if_not_found=False):
                self.add_alias_xref(
                    xref, "base.main_company", resource="res.company", group=group
                )
        if partner_xref:
            if not add_alias:  # pragma: no cover
                self.add_xref(partner_xref, "res.partner", company.partner_id.id)
            elif not self.env.ref(partner_xref, raise_if_not_found=False):
                self.add_alias_xref(
                    partner_xref,
                    "base.main_partner",
                    resource="res.partner",
                    group=group,
                )
        if recv_xref:
            store_acc_alias(recv_xref,
                            "account.data_account_type_receivable",
                            "property_account_receivable_id")
        if pay_xref:
            store_acc_alias(pay_xref,
                            "account.data_account_type_payable",
                            "property_account_payable_id")
        if bnk1_xref:
            store_acc_alias(bnk1_xref,
                            "account.data_account_type_liquidity",
                            "bank_account_code_prefix")
        if self.env.user.company_id != company:
            self.env.user.company_id = company  # pragma: no cover
        return self.default_company()

    def setup_env(
        self,
        lang=None,
        locale=None,
        group=None,
    ):
        """Create all record from declared data.
        This function starts the test workflow creating the test environment.
        Test data must be declared before engage this function with declare_all_data()
        function (see above).
        setup_env may be called more times with different group value.
        If it is called with the same group, it recreates the test environment with
        declared values; however this feature might do not work for some reason: i.e.
        if test creates a paid invoice, the setup_env() cannot unlink invoice.
        If you want to recreate the same test environment, assure the conditions for
        unlink of all created and tested records.
        If you create more test environment with different group you can use all data,
        even record created by different group.
        In this way you can test a complex process the evolved scenario.

        Args:
            lang (str): install & load specific language
            locale (str): install locale module with CoA; i.e l10n_it
            group (str): if supplied select specific group data; default is "base"

        Returns:
            None
        """
        self._logger.info(
            "🎺🎺🎺 Starting test v2.0.12 (debug_level=%s)" % (self.debug_level)
        )
        self._logger.info(
            "🎺🎺 Testing module: %s (%s)"
            % (self.module.name, self.module.installed_version)
        )
        self.log_stack()
        if locale:  # pragma: no cover
            self.set_locale(locale)
        if lang:  # pragma: no cover
            self.install_language(lang)
        self._convert_test_data(group=group)
        for resource in self.get_resource_list(group=group):
            resource_parent = self.parent_resource.get(resource)
            for xref in sorted(self.get_resource_data_list(resource, group=group)):
                if resource_parent:
                    parent_xref, ln = self._unpack_xref(xref)
                    if self.get_resource_data(resource_parent, parent_xref,
                                              group=group):
                        # Childs record alread loaded with header record
                        continue
                self.resource_make(resource, xref, group=group)
        if self.odoo_major_version < 13:
            self.env["account.journal"].search([("update_posted", "!=", True)]).write(
                {"update_posted": True}
            )

    ############################################
    #                                          #
    #     WIZARD/FORM ENVIRONMENT TEST API     #
    #                                          #
    ############################################

    def resource_edit(self, resource, default={}, web_changes=[], actions=[], ctx={}):
        """Server-side web form editing.
        Ordinary Odoo test use the primitive create() and write() functions to manage
        test data. These methods create an update records, but they do not properly
        reflect the behaviour of user editing form with GUI interface.

        This function simulates the client-side form editing in the server-side.
        It works in the follow way:

        * It can simulate the form create record
        * It can simulate the form update record
        * It can simulate the user data input
        * It calls the onchange functions automatically
        * It may be used to call button on the form

        User action simulation:

        The parameter <web_changes> is a list of user actions to execute sequentially.
        Every element of the list is another list with 2 or 3 values:

        * Field name to assign value
        * Value to assign
        * Optional function to execute (i.e. specific onchange)

        If field is associate to an onchange function the relative onchange functions
        are execute after value assignment. If onchange set another field with another
        onchange the relative another onchange are executed until all onchange are
        exhausted. This behavior is the same of the form editing.

        Warning: because function are always executed at the server side the behavior
        may be slightly different from actual form editing. Please take note of
        following limitations:

        * update form cannot simulate discard button
        * some required data in create must be supplied by default parameter
        * form inconsistency cannot be detected by this function
        * nested function must be managed by test code (i.e. wizard from form)

        See test_testenv module for test examples
        https://github.com/zeroincombenze/zerobug-test/tree/12.0/test_testenv

        Args:
            resource (str or obj): if field is a string simulate create web behavior of
                                   Odoo model issued in resource;
                                   if field is an obj simulate write web behavior on the
                                   issued record
            default (dict): default value to assign
            web_changes (list): list of tuples (field, value); see <wiz_edit>

        Returns:
            windows action to execute or obj record
        """
        self.log_stack()
        actions = actions or (
            ["create"] if isinstance(resource, basestring) else ["save"]
        )
        actions = actions if isinstance(actions, (list, tuple)) else [actions]
        self.log_lvl_2("🐞%s.resource_edit(%s)" % (resource, actions), strict=True)
        self.log_lvl_3(
            "🐞%s.resource_edit(def=%s,chng=%s,act=%s,ctx=%s)"
            % (
                resource,
                self.dict_2_print(default),
                self.dict_2_print(web_changes),
                actions,
                self.dict_2_print(ctx),
            )
        )
        origin = self._set_origin(resource, ctx=ctx)
        for action in actions:
            result = self._exec_action(
                resource, action,
                default=default, web_changes=web_changes, origin=origin, ctx=ctx
            )
            # Web changes executed, clear them, same for default
            web_changes = []
            default = {}
            if hasattr(result, "_name"):
                # action returned recordset
                resource = result
        return result

    def field_download(self, record, field):
        """Execute the data download from a binary field.

        Args:
            record (obj): record object
            field (str): field name to download

        Returns:
            binary obj downloaded from field
        """
        self.log_stack()
        if field not in record:  # pragma: no cover
            raise ValueError("Field %s not found in %s" % (field, record._name))
        return base64.b64decode(getattr(record, field))

    def resource_download(
        self,
        module=None,
        action_name=None,
        act_windows=None,
        records=None,
        default=None,
        ctx={},
        button_name=None,
        web_changes=[],
        button_ctx={},
        field=None,
    ):
        """Execute the data download.
        Engage the specific download wizard and return the downloaded data.
        Both parameters <module> and <action_name> must be issued in order to
        call <wiz_by_action_name>; they are alternative to act_windows.

        User action simulation:

        The parameter <web_changes> is a list of user actions to execute sequentially.
        Every element of the list is another list with 2 or 3 values:

        * Field name to assign value
        * Value to assign
        * Optional function to execute (i.e. specific onchange)

        If field is associate to an onchange function the relative onchange functions
        are execute after value assignment. If onchange set another field with another
        onchange the relative another onchange are executed until all onchange are
        exhausted. This behavior is the same of the form editing.

        Args:
            module (str): module name for wizard to test; if "." use current module name
            action_name (str): action name
            act_windows (dict): Odoo windows action (do not issue module & action_name)
            records (obj): objects required by the download wizard
            default (dict): default value to assign
            ctx (dict): context to pass to wizard during execution
            button_name (str): function name to execute at the end of then wizard
            web_changes (list): list of tuples (field, value); see above
            button_ctx (dict): context to pass to button_name function
            field (str): field name to download

        Returns:
            binary obj downloaded from field
        """
        self.log_stack()
        act_windows = self.wizard(
            module=module,
            action_name=action_name,
            act_windows=act_windows,
            records=records,
            default=default,
            ctx=ctx,
            button_name=button_name,
            web_changes=web_changes,
            button_ctx=button_ctx,
        )
        res_model = self._get_model_from_act_windows(act_windows)
        if field not in self.env[res_model]:
            self.raise_error("Field %s not found in %s" % (field, res_model))
        return base64.b64decode(
            getattr(self.env[res_model].browse(act_windows["res_id"]), field)
        )

    def is_action(self, act_windows):
        return isinstance(act_windows, dict) and act_windows.get("type") in (
            "ir.actions.act_window",
            "ir.actions.client",
            "ir.actions.act_window_close"
        )

    def wizard(
        self,
        module=None,
        action_name=None,
        act_windows=None,
        records=None,
        default=None,
        ctx={},
        button_name=None,
        web_changes=[],
        button_ctx={},
    ):
        """Execute a full wizard.

        Engage the specific wizard, simulate user actions and return the wizard result,
        usually a windows action.

        It is useful to test:
            * view names
            * wizard structure
            * wizard code

        Both parameters <module> and <action_name> must be issued in order to
        call <wiz_by_action_name>; they are alternative to act_windows.

        *** Example of use ***

        XML view file:
            <record id="action_example" model="ir.actions.act_window">
                <field name="name">Example</field>
                <field name="res_model">wizard.example</field>
                [...]
            </record>

        Python code:
            act_windows = self.wizard(module="module_example",
                action_name="action_example", ...)
            if self.is_action(act_windows):
                act_windows = self.wizard(act_windows=act_windows, ...)

        User action simulation:
        The parameter <web_changes> is a list of user actions to execute sequentially.
        Every element of the list is another list with 2 or 3 values:
        * Field name to assign value
        * Value to assign
        * Optional function to execute (i.e. specific onchange)
        If field is associate to an onchange function the relative onchange functions
        are execute after value assignment. If onchange set another field with another
        onchange the relative another onchange are executed until all onchange are
        exhausted. This behavior is the same of the form editing.

        Args:
            module (str): module name for wizard to test; if "." use current module name
            action_name (str): action name
            act_windows (dict): Odoo windows action (do not issue module & action_name)
            records (obj): objects required by the download wizard
            default (dict): default value to assign
            ctx (dict): context to pass to wizard during execution
            button_name (str): function name to execute at the end of then wizard
            web_changes (list): list of tuples (field, value); see above
            button_ctx (dict): context to pass to button_name function

        Returns:
            result of the wizard

        Raises:
            ValueError: if invalid parameters issued
        """
        self.log_stack()
        if module and action_name:
            act_windows = self._wiz_launch_by_act_name(
                module, action_name, records=records, default=default, ctx=ctx
            )
        elif act_windows:
            act_windows = self._wiz_launch(
                act_windows, records=records, default=default, ctx=ctx
            )
        else:  # pragma: no cover
            self.raise_error("Invalid action!")
        return self._wiz_execution(
            act_windows,
            button_name=button_name,
            web_changes=web_changes,
            button_ctx=button_ctx,
        )

    def get_records_from_act_windows(self, act_windows):
        """Get records from a windows message.

        Args:
            act_windows (dict): Odoo windows action returned by a wizard

        Returns:
            records or False

        Raises:
            ValueError: if invalid parameters issued
        """
        if self.is_action(act_windows):
            if act_windows["type"] == "ir.actions.act_window":
                res_model = self._get_model_from_act_windows(act_windows)
                if self._is_transient(res_model):  # pragma: no cover
                    self.raise_error(
                        "Invalid transiente model %s for <%s>!"
                        % (res_model, act_windows.get("name", ""))
                    )
                if "res_id" in act_windows:
                    return self.env[res_model].browse(act_windows["res_id"])
                elif "domain" in act_windows:
                    return self.env[res_model].search(act_windows["domain"])
        return False  # pragma: no cover

    ###############################
    #                             #
    #     DATA VALIDATION API     #
    #                             #
    ###############################

    def tmpl_repr(self, tmpl=[], level=None, match=None):
        def get_item(template, match=None):
            if isinstance(template, (list, tuple)):
                item = ""
                for tmpl in template:
                    item += get_item(tmpl, match=match) + " "
                return item.strip()
            item = str(template.get("id", template.get("code", template.get(
                "name", "<...>"))))
            if match and "_MATCH" in template:
                item += "{"
                item += ", ".join(
                    ["%s=%d" % (k, v) for (k, v) in template["_MATCH"].items()])
                item += "}"
            return item

        level = level or 0
        indent = level * "  "
        return indent + "".join(
            [
                "template(",
                ", ".join(
                    [
                        get_item(x, match=match)
                        for x in tmpl
                    ]
                ),
                ")",
            ]
        )

    def tmpl_init(self, template, record, nr=0, repr="", rec_parent=None):
        def merge_match(match, submatch, is_child=False):
            for kk in submatch:
                key = (rec_parent, kk[0]) if is_child else kk
                if key not in match:
                    match[key] = 0
                match[key] += submatch[kk]

        if not is_iterable(record):  # pragma: no cover
            self.raise_error(
                "Function validate_records(): right param is not iterable!"
            )

        if isinstance(template, (list, tuple)):
            match = {}
            for ix, tmpl in enumerate(template):
                if (
                    isinstance(tmpl, (list, tuple))
                    and isinstance(tmpl[0], (int, long))
                    and isinstance(tmpl[1], (int, long))
                    and isinstance(tmpl[2], dict)
                ):
                    tmpl = tmpl[2]
                    template[ix] = tmpl
                if not isinstance(tmpl, dict):                      # pragma: no cover
                    self.raise_error(
                        ("Function validate_records(): "
                         "invalid structure: %s must be a dictionary!" % tmpl)
                    )
                if REC_KEY_NAME & set(tmpl.keys()):
                    if rec_parent:
                        repr = "line." + tmpl.get("code", tmpl.get("name", ""))[0:20]
                    else:
                        repr = tmpl.get("code", tmpl.get("name", ""))[0:20]
                else:
                    if rec_parent:
                        repr = "line."
                    nr += 1
                    tmpl["id"] = repr + str(nr)
                merge_match(
                    match,
                    self.tmpl_init(
                        tmpl, record, nr=nr, repr=repr, rec_parent=rec_parent))
            return match

        if len(record) > 1 or isinstance(record, (list, tuple)):
            for rec in record:
                match = self.tmpl_init(
                    template, rec, nr=nr, repr=repr, rec_parent=rec_parent)
            return match

        resource = self._get_model_from_records(record)
        if not resource:                                            # pragma: no cover
            self.raise_error("No valid record supplied for comparation!")
        self._load_field_struct(resource)
        childs_name = self.childs_name.get(resource)
        resource_child = self.childs_resource.get(resource)
        if resource_child:
            self._load_field_struct(resource_child)
        key = (rec_parent, record)
        template["_MATCH"] = template.get("_MATCH", {})
        template["_MATCH"][key] = 0
        for field in template.keys():
            if field in (childs_name, "id") or field.startswith("_"):
                continue
            if self._cast_field(
                resource, field, template[field], fmt="py"
            ) == self._convert_field_to_write(record, field):
                template["_MATCH"][key] += 1
        if childs_name:
            merge_match(template["_MATCH"],
                        self.tmpl_init(
                            template[childs_name],
                            record[childs_name],
                            nr=nr + 100,
                            repr=repr,
                            rec_parent=record),
                        is_child=True)
        return template["_MATCH"]

    def tmpl_purge_matrix(self, template, record, rec_parent=None):
        def get_score(template, record, ctr=-1, rec_parent=None):
            key = (rec_parent, record)
            match = None
            if key in template["_MATCH"] and template["_MATCH"][key] > ctr:
                match = key
                ctr = template["_MATCH"][key]
            return template, match, ctr

        def get_best_score(template, record, rec_parent=None, matched=[], childs=False):
            resource = self._get_model_from_records(record)
            childs_name = self.childs_name.get(resource)
            if childs and not childs_name:                          # pragma: no cover
                return None, None
            ctr = -1
            match_key = match_tmpl = None
            for rec in record:
                for tmpl in template:
                    if (tmpl, (rec_parent, rec)) in matched:
                        continue
                    tmpl, key, ctr = get_score(
                        tmpl, rec, ctr=ctr, rec_parent=rec_parent)
                    if key:
                        match_key = key
                        match_tmpl = tmpl
            return match_tmpl, match_key

        if (
            isinstance(template, (list, tuple))
            or len(record) > 1
            or isinstance(record, (list, tuple))
        ):
            template = template if isinstance(template, (list, tuple)) else [template]
            resource = self._get_model_from_records(record)
            childs_name = self.childs_name.get(resource)
            if childs_name:
                matched = []
                while True:
                    ctr = -1
                    match_tmpl = match_key = None
                    for rec in record:
                        for tmpl in template:
                            for child_rec in rec[childs_name]:
                                for child_tmpl in tmpl[childs_name]:
                                    if (child_tmpl, (rec, child_rec)) in matched:
                                        continue
                                    child_tmpl, child_key, ctr = get_score(
                                        child_tmpl, child_rec,
                                        ctr=ctr, rec_parent=rec)
                                    if child_key:
                                        match_tmpl = child_tmpl
                                        match_key = child_key
                    if not match_key:
                        break
                    matched.append((match_tmpl, match_key))
                    self.tmpl_purge_matrix(
                        match_tmpl, match_key[1], rec_parent=match_key[0])

            max_recs = len(template) * len(record)
            matched = []
            while len(matched) < max_recs:
                match_tmpl, match_key = get_best_score(
                    template, record, rec_parent=rec_parent, matched=matched)
                if not match_key:
                    break
                matched.append((match_tmpl, match_key))
                self.tmpl_purge_matrix(
                    match_tmpl, match_key[1], rec_parent=match_key[0])
                for tmpl in template:
                    if tmpl == match_tmpl:
                        continue
                    if match_key in tmpl["_MATCH"]:
                        del tmpl["_MATCH"][match_key]
            return matched

        for key in template["_MATCH"].copy().keys():
            if key[0] != rec_parent or key[1] != record:
                del template["_MATCH"][key]

    def tmpl_validate_record(self, template, record):
        resource = self._get_model_from_records(record)
        childs_name = self.childs_name.get(resource)
        ctr_assertion = 0

        if isinstance(template, (list, tuple)):
            for tmpl in template:
                ctr_assertion += self.tmpl_validate_record(tmpl, record)
            return ctr_assertion

        if len(record) > 1 or isinstance(record, (list, tuple)):
            for rec in record:
                ctr_assertion += self.tmpl_validate_record(template, rec)
            return ctr_assertion

        # if [key for key in template["_MATCH"]][0][1] == record:
        if template["_MATCH"] and template["_MATCH"].keys()[0][1] == record:
            for field in template.keys():
                if field in (childs_name, "id") or field.startswith("_"):
                    continue
                msg_id = ("🐞 ... assertEqual(%s.%s:'%s', %s:'%s')"
                          % (
                              self.tmpl_repr([template]),
                              field,
                              template[field],
                              "rec(%d)" % record.id,
                              record[field],
                          ))
                self.log_lvl_2(msg_id)
                self.assertEqual(
                    self._cast_field(resource, field, template[field], fmt="py"),
                    self._cast_field(resource, field, record[field], fmt="py"),
                    msg_id
                )
                ctr_assertion += 1
            if childs_name:
                ctr_assertion += self.tmpl_validate_record(
                    template[childs_name], record[childs_name])
        return ctr_assertion

    def validate_records(self, template, records, raise_if_not_match=True):
        """Validate records against template values.
        During the test will be necessary to check result record values.
        This function aim to validate all the important values with one step.
        You have to issue 2 params: template with expected values and record to check.
        You can declare just some field value in template which are important for you.
        Both template and record are lists, record may be a record set too.
        This function do following steps:

        * matches templates and record, based on template supplied data
        * check if all templates are matched with 1 record to validate
        * execute self.assertEqual() for every field in template
        * check for every template record has matched with assert
        * check if all templates matched 1 to 1 with a record

        Notice: all templates must be matched but not all record must be matched.
        You can supply the complete table, this function check for all records that
        match with templates, remaining records are ignored.
        In this way you do not have to select records to match, just issue all records
        which contain the test set.

        Args:
             template (list of dict): list of dictionaries with expected values
             records (list or set): records to validate values

        Returns:
            list of matched coupled (template, record) + # of assertions

        Raises:
            ValueError: if no enough assertions or one assertion is failed
        """
        self.log_stack()
        self.tmpl_init(template, records)
        self.log_lvl_2(
            "🐞validate_records(%s, %s)" % (self.tmpl_repr(template), records)
        )
        self.tmpl_purge_matrix(template, records)
        ctr_assertion = self.tmpl_validate_record(template, records)
        matches = []
        for tmpl in template:
            if not tmpl["_MATCH"]:
                self.raise_error("One template item matches twice!\n%s" % tmpl)
            elif tmpl["_MATCH"] not in matches:
                matches.append(tmpl["_MATCH"])
                ctr_assertion += 1
            else:
                self.raise_error("One template item matches twice!\n%s" % tmpl)
        self.log_lvl_1(
            "🐞%d assertion validated for validate_records(%s)"
            % (ctr_assertion, self.tmpl_repr(template, match=True)),
        )
