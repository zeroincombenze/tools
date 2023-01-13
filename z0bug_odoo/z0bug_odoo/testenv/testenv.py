# -*- coding: utf-8 -*-
"""Test Environment v2.0.3

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

* Ordinary Odoo external reference (a), format "module.name"
* Test reference, format "z0bug.name" (b)
* Key value, format "external.key" (c)
* 2 keys reference, for header/detail relationship (d)
* Magic reference for 'product.template' / 'product.product' (e)

Ordinary Odoo external reference (a) is a record of 'ir.model.data';
you can see them from Odoo GUI interface.

Test reference (b) are visible just in the test environment.
They are identified by "z0bug." prefix module name.

External key reference (c) is identified by "external." prefix followed by
the key value used to retrieve the record.
The field "code" or "name" are used to search record;
for account.tax the "description" field is used.
Please set self.debug_level = 2 (or more) to log these field keys.

The 2 keys reference (d) needs to address child record inside header record
at 2 level model (header/detail) relationship.
The key MUST BE the same key of the parent record,
plus "_", plus line identifier (usually 'sequence' field).
i.e. "z0bug.move_1_3" means: line with sequence 3 of 'account.move.line'
which is child of record "z0bug.move_1" of 'account.move'.
Please set self.debug_level = 2 (or more) to log these relationships.

For 'product.template' (product) you must use '_template' text in reference (e).
TestEnv inherit 'product.product' (variant) external reference.

For furthermore information, please:

* Read file testenv.rst in this directory (if supplied)
* Visit https://zeroincombenze-tools.readthedocs.io
* Visit https://github.com/zeroincombenze/tools
* Visit https://github.com/zeroincombenze/zerobug-test
"""
from __future__ import unicode_literals

import os

from future.utils import PY2, PY3
from past.builtins import basestring, long

from datetime import datetime
import json
import logging
import base64

from odoo.tools.safe_eval import safe_eval
from odoo.modules.module import get_module_resource

import python_plus
from z0bug_odoo.test_common import SingleTransactionCase
from z0bug_odoo import z0bug_odoo_lib
# from clodoo import transodoo

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
RESOURCE_WO_COMPANY = ("res.users",)
# Please, do not change fields order
KEY_CANDIDATE = (
    "acc_number",
    "code_prefix",
    "default_code",
    "sequence",
    "login",
    "description",
    "depreciation_type_id",
    "number",
    "partner_id",
    "product_id",
    "product_tmpl_id",
    "tax_src_id",
    "tax_dest_id",
    "code",
    "name",
)
if PY3:                                                              # pragma: no cover
    text_type = unicode = str
    bytestr_type = bytes
elif PY2:                                                            # pragma: no cover
    # unicode exist only for python2
    text_type = unicode
    bytestr_type = str


def is_iterable(obj):
    return hasattr(obj, "__iter__")


class MainTest(SingleTransactionCase):

    def setUp(self):
        super(MainTest, self).setUp()
        self.debug_level = 0
        self.PYCODESET = 'utf-8'
        self._logger = _logger
        self.setup_data_list = {}
        self.setup_data = {}
        self.struct = {}
        self.skeys = {}
        self.parent_name = {}
        self.parent_resource = {}
        self.childs_name = {}
        self.childs_resource = {}
        self.uninstallable_modules = []
        self.convey_record = {}
        for item in self.__module__.split("."):
            if item not in ("odoo", "openerp", "addons"):
                self.module = item
                break
        # self.tnldict = {}
        # transodoo.read_stored_dict({})
        # self.decl_version = "librerp12"
        # if os.environ.get("VERSION"):
        #     self.odoo_version = int(os.environ["VERSION"].split("."))
        # else:
        #     try:
        #         import odoo.release as release
        #         self.odoo_version = "%s" % release.version_info[0]
        #     except ImportError:
        #         try:
        #             import openerp.release as release
        #             self.odoo_version = "%" % release.version_info[0]
        #         except ImportError:
        #             self.odoo_version = "16"

    # ---------------------------------------
    # --  Unicode encode/decode functions  --
    # ---------------------------------------
    def u(self, s):                                                  # pragma: no cover
        if isinstance(s, bytestr_type):
            if PY3:
                return s.decode(self.PYCODESET)
            return unicode(s, self.PYCODESET)
        return s

    def unicodes(self, src):                                         # pragma: no cover
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
    def dict_2_print(self, values):                                  # pragma: no cover
        def to_str(obj):
            x = str(obj)
            return x if (hasattr(obj, "len") and len(x) < 120) else "[...]"

        if isinstance(values, dict):
            return json.dumps(values, default=to_str, indent=4)
        return values

    def log_lvl_3(self, mesg, strict=None):                          # pragma: no cover
        if (self.debug_level >= 3 and not strict) or self.debug_level == 3:
            self._logger.info(mesg)

    def log_lvl_2(self, mesg, strict=None):                          # pragma: no cover
        if (self.debug_level >= 2 and not strict) or self.debug_level == 2:
            self._logger.info(mesg)

    def log_lvl_1(self, mesg, strict=None):                          # pragma: no cover
        if (self.debug_level >= 1 and not strict) or self.debug_level == 1:
            self._logger.info(mesg)

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
                self.setup_data[group][resource][conveyed_xref] = (
                    self.setup_data[group][resource][xref]
                )
                del self.setup_data[group][resource][xref]

    def _add_conveyance(self, resource, field, convey):
        self._logger.info(
            "⚠ %s[%s]: '%s' -> '%s'" % (resource, field, convey[0], convey[1])
        )
        if resource not in self.convey_record:
            self.convey_record[resource] = {}
        self.convey_record[resource][field] = convey

    def add_alias_xref(self, xref, conveyed_xref, resource=None, group=None):
        self._logger.info(
            "⚠ xref '%s' -> '%s'" % (xref, conveyed_xref)
        )
        ir_resource = "ir.model.data"
        if ir_resource not in self.convey_record:
            self.convey_record[ir_resource] = {}
        self.convey_record[ir_resource][xref] = conveyed_xref
        self._move_conveyed_xref(resource, xref, conveyed_xref, group=group)

    def _get_conveyed_value(self, resource, field, value, fmt=None):
        if (
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
            [("name", "=", "account_payment_term_extension"),
             ("state", "=", "installed")]
        ):
            resource = "account.payment.term.line"
            for xref in self.get_resource_data_list(resource, group=group):
                values = self.get_resource_data(resource, xref, group=group)
                if values.get("months"):
                    values["days"] = values["months"] * 30 - 2
                    values["months"] = ""
                self.store_resource_data(resource, xref, values, group=group)

    # ------------------------------
    # --  Hierarchical functions  --
    # ------------------------------

    def _search4parent(self, resource, parent_resource=None):
        if resource == "product.product":
            parent_resource = "product.template"
        else:
            parent_resource = parent_resource or ".".join(resource.split(".")[:-1])
        if parent_resource not in self.env:
            parent_resource = None
        if parent_resource and resource not in self.parent_resource:
            for field in self.struct[resource].keys():
                if self.struct[resource][field].get("relation", "/") == parent_resource:
                    self.parent_name[resource] = field
                    self.parent_resource[resource] = parent_resource
                    self.log_lvl_2(
                        "🐞  parent_resource[%s] = %s" % (
                            resource, self.parent_resource[resource])
                    )
                    self.log_lvl_2(
                        "🐞  parent_name[%s] = %s" % (resource, field)
                    )
                    break

    def _search4childs(self, resource, childs_resource=None):
        childs_resource = childs_resource or []
        if not childs_resource:
            if resource == "product.template":
                childs_resource = ["product.product"]
            else:
                for suffix in (".line", ".rate", ".state"):
                    childs_resource.append(resource + suffix)
        if not isinstance(childs_resource, (list, tuple)):
            childs_resource = [childs_resource]                      # pragma: no cover
        if resource not in self.childs_resource:
            for field in self.struct[resource].keys():
                if self.struct[resource][field].get("relation",
                                                    "/") in childs_resource:
                    if (
                        resource not in self.childs_name
                        or len(field) < len(self.childs_name[resource])
                    ):
                        self.childs_name[resource] = field
                        self.childs_resource[resource] = self.struct[resource][field][
                            "relation"
                        ]
                        self.log_lvl_2(
                            "🐞childs_resource[%s] = %s" % (
                                resource, self.childs_resource[resource])
                        )
                        self.log_lvl_2(
                            "🐞childs_name[%s] = %s" % (resource, field)
                        )

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
                record = self.resource_bind(
                    child_xref, raise_if_not_found=False, resource=childs_resource,
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
        return (isinstance(xref, basestring)
                and "." in xref
                and " " not in xref
                and len(xref.split(".")) == 2)

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
        xrefs[0].write(values)
        return xrefs[0]

    def _get_xref_id(self, resource, xref, fmt=None):
        res = xref
        if xref.isdigit() or (xref.startswith("-") and xref[1:].isdigit()):
            res = int(xref)
        elif self._is_xref(xref):
            if fmt:
                res = self.resource_bind(
                    xref, raise_if_not_found=False, resource=resource
                )
                if not res and not self.get_resource_data(resource, xref):
                    self._logger.info("⚠ External reference %s not found" % xref)
            else:
                res = self.env.ref(
                    self._get_conveyed_value(resource, None, xref),
                    raise_if_not_found=False)
            res = res.id if res else False if fmt else xref
        return res

    def _get_depending_xref(self, resource, xref):
        resource_child = xref_child = field_child = field_parent = False
        if resource == "product.template":
            xref_child = xref.replace("_template", "_product")
            if xref_child == xref:
                xref_child = xref.replace("template_", "product_")   # pragma: no cover
            if xref_child == xref:
                xref_child = xref.replace("template", "product")     # pragma: no cover
            if xref_child == xref:                                   # pragma: no cover
                self._logger.info(
                    (
                        "⚠ wrong xref pattern '%s':"
                        " please use something like 'z0bug.product_template_1"
                    ) % xref
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
                raise ValueError(                                    # pragma: no cover
                    "Model %s not found in the system" % resource)   # pragma: no cover
            self.struct[resource] = self.env[resource].fields_get()
            self._search4parent(resource)
            if resource in self.parent_resource:
                self._load_field_struct(self.parent_resource[resource])
                self._search4childs(self.parent_resource[resource])
            self._search4childs(resource)
            if resource in self.childs_resource:
                self._load_field_struct(self.childs_resource[resource])
                self._search4parent(self.childs_resource[resource])
            multi_key = True if self.parent_name.get(resource) else False
            for field in KEY_CANDIDATE:
                if (
                    field == self.parent_name.get(resource)
                    or (field == "code" and resource == "product.product")
                    or (field == "description" and resource != "account.tax")
                    or (field == "login" and resource != "res.users")
                    or (field == "sequence" and not multi_key)
                ):
                    continue                                         # pragma: no cover
                if field in self.struct[resource]:
                    self.skeys[resource] = [field]
                    self.log_lvl_2(
                        "🐞  skeys[%s] = %s" % (resource, self.skeys[resource])
                    )
                    break

    # ---------------------------------------------
    # --  Type <char> / <text> / base functions  --
    # ---------------------------------------------

    def _cast_field(self, resource, field, value, fmt=None, group=None):
        ftype = self.struct[resource][field]["type"]
        if ftype != "binary":
            value = self._get_conveyed_value(resource, field, value, fmt=fmt)
        if value is None or value in ("None", r"\N") or field == "id":
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
            value = getattr(
                self, method)(resource, field, value, fmt=fmt, group=group)
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

    def _cast_field_selection(self, resource, field, value, fmt=None, group=None):
        if fmt and resource == "res.partner" and field == "lang":
            if not self.env["res.lang"].search([("code", "=", value)]):
                self._logger.info("⚠ Invalid value %s" % value)
                value = None
        return value

    # --------------------------------
    # --  Type <boolean> functions  --
    # --------------------------------

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

    def _upgrade_field_boolean(self, record, field, value):
        return self._cast_field_boolean(record, field, value)

    # --------------------------------
    # --  Type <integer> functions  --
    # --------------------------------

    def _cast_field_integer(self, resource, field, value, fmt=None, group=None):
        if value and isinstance(value, basestring):
            value = int(value)
        return value

    def _upgrade_field_integer(self, record, field, value):
        return self._cast_field_integer(record, field, value)

    # ------------------------------
    # --  Type <float> functions  --
    # ------------------------------

    def _cast_field_float(self, resource, field, value, fmt=None, group=None):
        if value and isinstance(value, basestring):
            value = eval(value)
        return value

    def _upgrade_field_float(self, record, field, value):
        return self._cast_field_float(record, field, value)

    # ---------------------------------
    # --  Type <monetary> functions  --
    # ---------------------------------

    def _cast_field_monetary(self, resource, field, value, fmt=None, group=None):
        return self._cast_field_float(resource, field, value, fmt=fmt, group=group)

    def _upgrade_field_monetary(self, record, field, value):
        return self._cast_field_monetary(record, field, value)

    # ---------------------------------
    # --  Type <datetime> functions  --
    # ---------------------------------

    def _cast_field_datetime(self, resource, field, value, fmt=None, group=None):
        return self._cast_field_date(resource, field, value, fmt=fmt, group=group)

    def _upgrade_field_datetime(self, record, field, value):
        if isinstance(value, basestring):
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return value

    def _convert_datetime_to_write(self, record, field, value):
        return str(value)

    # -----------------------------
    # --  Type <date> functions  --
    # -----------------------------

    def _cast_field_date(self, resource, field, value, fmt=None, group=None):
        if isinstance(value, (list, tuple)) and fmt:
            value = self.compute_date(value[0], refdate=value[1])
        else:
            value = self.compute_date(value)
        return value

    def _upgrade_field_date(self, record, field, value):
        if isinstance(value, basestring):
            return datetime.strptime(value, "%Y-%m-%d")
        return value

    def _convert_date_to_write(self, record, field, value):
        return str(value)

    # -------------------------------
    # --  Type <binary> functions  --
    # -------------------------------

    def _get_binary_filename(self, xref, bin_types=None):
        binary_root = get_module_resource(self.module, "tests", "data")
        if not bin_types:
            binary_file = os.path.join(binary_root, xref)
            if os.path.isfile(binary_file):
                return binary_file
        bin_types = bin_types or ["png", "jpg", "xml"]
        if not is_iterable(bin_types):
            bin_types = [bin_types]
        for btype in bin_types:
            binary_file = os.path.join(binary_root, "%s.%s" % (xref, btype))
            if os.path.isfile(binary_file):
                return binary_file
        return False

    def _get_binary_contents(self, value):
        if (
            not isinstance(value, basestring)
            or (PY3 and isinstance(value, bytes))
            or len(value) > 64
        ):
            return value
        bin_file = self._get_binary_filename(value)
        if bin_file:
            with open(bin_file, 'rb') as fd:
                bin_contents = python_plus._b(fd.read())
            return base64.b64encode(bin_contents)
        return False

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

    def _cast_field_many2one(self, resource, field, value, fmt=None, group=None):
        if isinstance(value, basestring):
            value = self._get_xref_id(
                self.struct[resource][field].get("relation", resource),
                value,
                fmt=fmt,
            )
        if not value:
            value = None
        return value

    def _upgrade_field_many2one(self, record, field, value):
        return self._cast_field_many2one(record, field, value)

    def _convert_many2one_to_write(self, record, field, value):
        return value.id

    # -----------------------------------------------
    # --  Type <one2many> / <many2many> functions  --
    # -----------------------------------------------

    def _cast_2many(self, resource, value, fmt=None, group=None):
        """"One2many and many2many may have more representations:
        * External reference (str) -> 1 value or None
        * list() or list (str)
        * - [0, 0, values (dict)]
        * - [1, ID (int), values (dict)]
        * - [2, ID (int)]
        * - [3, ID (int)]
        * - [4, ID (int)]
        * - [5, x]
        * - [6, x, IDs (list)]
        * - External reference (str) -> 1 value or None
        """

        def value2list(value):
            if isinstance(value, basestring):
                value = [x for x in value.split(",")]
            elif not is_iterable(value):
                value = [value]
            return value

        res = []
        is_cmd = True if isinstance(value, (list, tuple)) else False
        items = value2list(value)
        for item in items:
            if isinstance(item, basestring):
                xid = self._get_xref_id(resource, item, fmt=fmt)
                if xid:
                    res.append(xid)
                is_cmd = False
            elif (
                fmt
                and is_cmd
                and isinstance(item, (list, tuple))
                and len(item) == 3
                and item[0] in (0, 1)
                and isinstance(item[2], basestring)
            ):
                res.append(
                    (
                        item[0],
                        item[1],
                        self.cast_types(
                            resource,
                            self.get_resource_data(
                                resource, item[2], group=group),
                            fmt=fmt,
                            group=group
                        ),
                    )
                )
            elif (
                fmt
                and is_cmd
                and isinstance(item, (list, tuple))
                and len(item) in (2, 3)
                and (
                    (len(item) == 3 and item[0] == 0 and isinstance(item[2], dict))
                    or (
                        len(item) == 3
                        and item[0] == 1
                        and isinstance(item[1], (int, long))
                        and isinstance(item[2], dict)
                    )
                    or (
                        len(item) == 2
                        and item[0] in (2, 3, 4)
                        and isinstance(item[1], (int, long))
                    )
                    or item[0] == 5
                    or (
                        len(item) == 3
                        and item[0] == 6
                        and isinstance(item[1], (int, long))
                        and isinstance(item[2], (list, tuple))
                    )
                )
            ):
                res.append(item)
            elif isinstance(item, (list, tuple)):
                res.append(self._cast_2many(resource, item, group=group))
                is_cmd = False
            else:
                res.append(item)
                is_cmd = False
        if len(res):
            if fmt == "cmd" and not is_cmd:
                res = [(6, 0, res)]
        else:
            res = False
            if fmt:
                self._logger.info("⚠ No *2many value for %s.%s" % (resource, value))
        return res

    def _cast_field_one2many(self, resource, field, value, fmt=None, group=None):
        value = self._cast_2many(
            self.struct[resource][field]["relation"],
            value,
            fmt=fmt,
            group=group,
        )
        if not value:
            value = None
        return value

    def _cast_field_many2many(self, resource, field, value, fmt=None, group=None):
        return self._cast_field_one2many(resource, field, value, fmt=fmt, group=group)

    def _upgrade_field_one2many(self, record, field, value):
        return self._cast_2many(record, value)

    def _upgrade_field_many2many(self, record, field, value):
        return self._cast_2many(record, value)

    def _convert_one2many_to_write(self, record, field, value):
        if value:
            return [(6, 0, [x.id for x in value])]
        return False

    def _convert_many2many_to_write(self, record, field, value):
        return self._convert_one2many_to_write(record, field, value)

    # -------------------------------------
    # --  ir.model / resource functions  --
    # -------------------------------------

    def cast_types(self, resource, values, fmt=None, group=None):
        if values:
            self._load_field_struct(resource)
            for field in [x for x in list(values.keys())]:
                if field not in self.struct[resource]:
                    if fmt:
                        del values[field]
                        self.log_lvl_2(
                            "🐞field %s does not exist in %s" % (field, resource)
                        )
                    continue

                value = self._cast_field(
                    resource, field, values[field], fmt=fmt, group=group)
                if value is None:
                    del values[field]
                    if field != "id":
                        self.log_lvl_3(
                            "🐞del %s.vals[%s]" % (resource, field)
                        )
                    continue
                values[field] = value
            if not values:                                           # pragma: no cover
                self.log_lvl_2("🐞%s.cast_type() = {}" % resource)

        return values

    def _convert_to_write(self, record, new=None):
        values = {}
        for field in list(record._fields.keys()):
            if (
                field in BLACKLIST_COLUMNS
                or record._fields[field].readonly
                or record._fields[field].type == "binary"
            ):
                continue
            value = self._convert_field_to_write(record, field)
            if value is None:
                continue
            elif value is False:
                if new:
                    continue
                values[field] = value
            else:
                values[field] = value
        return values

    def _upgrade_record(self, record, values, default={}):
        for field in list(values.keys()):
            if field in SUPERMAGIC_COLUMNS:
                continue
            method = "_upgrade_field_%s" % record._fields[field].type
            method = method if hasattr(self, method) else "_upgrade_field_base"
            value = getattr(self, method)(record, field, values[field])
            if not value and default.get(field):
                value = getattr(self, method)(record, field, default[field])
            if value is not None:
                setattr(record, field, value)
        return record

    def _purge_values(self, values, timed=None):
        for field in BITTER_COLUMNS:
            if field in values:
                del values[field]
        if timed:
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
            if isinstance(records, (int, long)) != act_windows["multi"]:
                self._logger.info("⚠ act_windows['multi'] does not match # of records!")

    def _create_object(self, resource, default={}, ctx={}):
        if ctx:
            record = self.env[resource].with_context(ctx).new(values=default)
        else:
            record = self.env[resource].new(values=default)
        if hasattr(record, "default_get"):
            self._upgrade_record(record,
                                 record.default_get(record.fields_get_keys()),
                                 default)
        for field in record._onchange_methods.values():
            for method in field:
                method(record)
        return record

    def _exec_action(self, record, action, web_changes=[]):
        resource_model = record[0]._name if isinstance(
            record, (list, tuple)) else record._name
        self._load_field_struct(resource_model)
        for args in web_changes:
            self._wiz_edit(
                record,
                resource_model,
                args[0], args[1], args[2] if len(args) > 2 else None,
            )
        if action == "save":
            return record.write({})
        elif action == "create":
            return record.create(
                self._convert_to_write(record, new=True))            # pragma: no cover
        elif action == "discard":
            return False                                             # pragma: no cover
        elif action and hasattr(record, action):
            self.log_lvl_2("🐞  %s.%s()" % (resource_model, action))
            act_windows = getattr(record, action)()
            # Weird bug: this is a workaround!!!
            if action == "action_invoice_draft" and record.state != "draft":
                record.state = "draft"
            elif action == "action_invoice_open" and record.state != "open":
                record.state = "open"
        elif self._is_xref(action):
            module, name = action.split(".", 1)
            act_windows = self.env["ir.actions.act_window"].for_xml_id(module, name)
            self.log_lvl_2("🐞  act_windows(%s)" % action)
            self._finalize_ctx_act_windows(record, act_windows)
        else:                                                        # pragma: no cover
            raise (ValueError, "Invalid button/action %s for %s!" % (
                action, resource_model))
        return act_windows

    def _get_model_from_act_windows(self, act_windows):
        return act_windows.get("res_model", act_windows.get("model"))

    def _wiz_launch(
        self, act_windows, records=None, default=None, ctx={}
    ):
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
        self.log_lvl_2("🐞wizard starting(%s)" % act_windows.get("name"), strict=True)
        self.log_lvl_3(
            "🐞wizard starting(%s,%s,def=%s,ctx=%s)" % (
                act_windows.get("name"),
                self.dict_2_print(act_windows),
                self.dict_2_print(default),
                self.dict_2_print(ctx)),
            strict=True
        )
        if not isinstance(act_windows, dict):                        # pragma: no cover
            raise (ValueError, "Invalid act_windows")
        self._finalize_ctx_act_windows(records, act_windows, ctx)
        if ctx and ctx.get("res_id"):
            act_windows["res_id"] = ctx.pop("res_id")
        if records:
            # The record type have to be the same of the action windows model
            # Warning: action windows may not contain any model declaration
            # Please, do not remove test, because if model is declared in action windows
            # must match with record model type
            if records._name != act_windows.get(                     # pragma: no cover
                "model_name", act_windows.get(
                    "src_model", act_windows.get("res_model", records._name))):
                raise (ValueError, "Records model different from declared model")
            if "active_ids" not in act_windows["context"]:
                act_windows["context"].update(
                    self._ctx_active_ids(records, ctx=act_windows["context"]))
            if not is_iterable(records):
                records = [records]
        if act_windows["type"] == "ir.actions.server":               # pragma: no cover
            if not records:
                raise (ValueError, "No records supplied")
        else:
            res_model = self._get_model_from_act_windows(act_windows)
            vals = self.cast_types(res_model, default or {}, fmt="cmd")
            res_id = act_windows.get("res_id")
            if res_id and isinstance(res_id, (int, long)):
                wizard = self.env[res_model].with_context(
                    act_windows["context"]).browse(res_id)
            else:
                wizard = self.env[res_model].with_context(
                    act_windows["context"]).create(
                    self._purge_values(
                        self._convert_to_write(
                            self._create_object(res_model,
                                                default=vals,
                                                ctx=act_windows["context"]),
                            new=True)))
                act_windows["res_id"] = wizard.id
        act_windows["res_id"] = wizard.id
        # Save wizard for furthermore use
        act_windows["_wizard_"] = wizard
        if act_windows.get("view_id"):
            # This code is just executed to test valid view structure
            self.env["ir.ui.view"].browse(act_windows["view_id"])    # pragma: no cover
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
        act_model = "ir.actions.act_window"
        module = self.module if module == "." else module
        act_windows = self.env[act_model].for_xml_id(module, action_name)
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
        self.log_lvl_3(
            "🐞  %s.onchange(%s=%s)" % (wizard, field, value)
        )
        cur_vals = {}
        for name in wizard._fields.keys():
            if name not in SUPERMAGIC_COLUMNS:
                cur_vals[name] = getattr(wizard, name)
        value = self._cast_field(resource, field, value, fmt="cmd")
        if value is not None:
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
        if onchange:
            getattr(wizard, onchange)()

    def _wiz_execution(
        self,
        act_windows,
        button_name=None,
        web_changes=[],
        button_ctx={},
    ):
        """Simulate wizard execution issued by an action.

        Wizard is created by <wizard_start> with default values.
        First, execute onchange methods without values.
        Simulate user actions by web_changes that is a list of tuple (field, value);
            * fields are updated sequentially from web_changes parameters
            * a field can be updated more times
            * any updated engages the onchange funcion if defined for field
        Finally, the <button_name> function is executed.
        It returns the wizard result or False.

        Python example:
            act_window = self.wizard_execution(
                act_window,
                button_name="do_something",
                web_changes=[
                    ("field_a_ids", [(6, 0, [value_a.id])], "onchange_field_a"),
                    ("field_b_id", self.b.id, "onchange_field_b"),
                    ("field_c", "C"),
                ],
            )

        Args:
            act_windows (dict): Odoo windows action returned by <wizard_start>
            records (obj): objects supplied for action server
            button_name (str): function name to execute at the end of then wizard
            web_changes (list): list of tuples (field, value); see above <wizard_edit>
            button_ctx (dict): context to pass to button_name function

        Returns:
            Odoo wizard result; may be a windows action to engage another wizard
            If windows break return wizard image too

        Raises:
          TypeError: if invalid wizard image
        """
        self.log_lvl_3("🐞wizard running(%s, %s)"
                       % (act_windows.get("name"), self.dict_2_print(act_windows)))
        # if act_windows["type"] == "ir.actions.server":
        #     if not records and "_wizard_" in act_windows:
        #         records = act_windows.pop("_wizard_")
        #     if not records:
        #         raise (ValueError, "No records supplied")
        #     if records._name != act_windows["model_name"]:
        #         raise (ValueError, "Records model different from declared model")
        #     ctx = {
        #         "active_model": act_windows["model_name"],
        #         "active_ids": [x.id for x in records],
        #     }
        #     eval_context = {
        #         "env": self.env,
        #         "model": records.with_context(ctx),
        #         "Warning": Warning,
        #         "record": records[0] if len(records) == 1 else None,
        #         "records": records,
        #         "log": self._logger,
        #     }
        #     eval_context.update(ctx)
        #     act_windows = safe_eval(
        #         act_windows["code"].strip(), eval_context, mode="exec", nocopy=True
        #     )
        #     return act_windows

        wizard = act_windows.pop("_wizard_")
        if button_name:
            result = self._exec_action(wizard, button_name, web_changes=web_changes)
            if isinstance(result, dict) and result.get("type") != "":
                result.setdefault("type", "ir.actions.act_window_close")
                if isinstance(button_ctx, dict):
                    result.setdefault("context", button_ctx)
                if (
                    self.is_action(result)
                    and result["type"] == "ir.actions.client"
                    and result.get("context", {}).get("active_model")
                    and result.get("context", {}).get("active_id")
                ):
                    result = self.env[result["context"]["active_model"]].browse(
                        result["context"]["active_id"]
                    )
            return result
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
        if group not in self.setup_data_list:
            self.setup_data_list[group] = []
            self.setup_data[group] = {}
        if name not in self.setup_data[group]:
            self.setup_data[group][name] = {}
        self.setup_data[group][name][xref] = self.cast_types(
            resource, values, group=group)
        self.log_lvl_2("🐞%s.store_resource_data(%s,name=%s,group=%s)" % (
            resource, xref, name, group))
        if name not in self.setup_data_list[group]:
            self.setup_data_list[group].append(name)

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

    def resource_bind(self, xref, raise_if_not_found=True, resource=None):
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

        Returns:
            obj: the Odoo model record

        Raises:
            ValueError: if invalid parameters issued
        """
        self.log_lvl_3(
            "🐞%s.resource_bind(%s)" % (resource, xref)
        )
        # Search for Odoo standard external reference
        if isinstance(xref, (int, long)):
            if not resource:                                         # pragma: no cover
                raise ValueError(
                    "No model issued for binding"
                )
                return False
            record = self.env[resource].browse(xref)
        else:
            record = self.env.ref(
                self._get_conveyed_value(None, None, xref), raise_if_not_found=False)
        if record:
            return record
        # Simulate external reference
        if not resource:
            if raise_if_not_found:                                   # pragma: no cover
                raise ValueError(
                    "No model issued for binding"
                )
            return False
        if resource not in self.env:                                 # pragma: no cover
            if raise_if_not_found:
                raise ValueError(
                    "Model %s not found in the system" % resource
                )
            return False
        self._load_field_struct(resource)
        if resource not in self.skeys:                               # pragma: no cover
            if raise_if_not_found:
                raise ValueError(
                    "Model %s without search key" % resource
                )
            self._logger.info("⚠ Model %s without search key" % resource)
            return False

        module, name = xref.split(".", 1)
        parent_name = self.parent_name.get(resource)
        if parent_name and self.parent_resource[resource] in self.childs_resource:
            # This is a 3 level external reference for header/detail relationship
            x = name.split("_")
            # Actual external reference for parent record
            name = "_".join(x[:-1])
            # Key to search for child record
            x = x[-1]
            if x.isdigit():
                x = int(x)
                if not x:
                    return False                                     # pragma: no cover
            # if self.struct[resource][self.skeys[resource][0]]["type"] == "many2one":
            #     pass
            domain = [(self.skeys[resource][0], "=", x)]
            x = self.resource_bind(
                "%s.%s" % (module, name),
                resource=self.parent_resource[resource],
                raise_if_not_found=False,
            )
            if not x:                                                # pragma: no cover
                return False
            domain.append((parent_name, "=", x.id))
        else:
            domain = [(self.skeys[resource][0], "=", name)]
        if (
            resource not in RESOURCE_WO_COMPANY
            and "company_id" in self.struct[resource]
        ):
            domain.append("|")
            domain.append(("company_id", "=", self.default_company().id))
            domain.append(("company_id", "=", False))
        record = self.env[resource].search(domain)
        if len(record) == 1:
            # return record[0]
            return self.env[resource].browse(record[0].id)
        if raise_if_not_found:
            raise ValueError("External ID %s not found" % xref)      # pragma: no cover
        return False

    def resource_create(self, resource, values=None, xref=None, group=None):
        """Create a test record and set external ID to next tests.
        This function works as standard Odoo create() with follow improvements:

        * It can create external reference too
        * It can use stored data if no values supplied

        Args:
            resource (str): Odoo model name, i.e. "res.partner"
            values (dict): record data (default stored data)
            xref (str): external reference to create
            group (str): used to manager group data; default is "base"

        Returns:
            obj: the Odoo model record, if created
        """
        self._load_field_struct(resource)
        xref = self._get_conveyed_value(resource, None, xref)
        values = self.unicodes(values)
        if not values and xref:
            values = self.get_resource_data(resource, xref, group=group)
            values = self._add_child_records(resource, xref, values, group=group)
        if not values:                                       # pragma: no cover
            raise ValueError(
                "No value supplied for %s create" % resource
            )
        self.log_lvl_3(
            "🐞%s.resource_create(%s,xref=%s)"
            % (resource, self.dict_2_print(values), xref)
        )
        values = self.cast_types(resource, values, fmt="cmd", group=group)
        if resource.startswith("account.move"):
            res = (
                self.env[resource]
                .with_context(check_move_validity=False)
                .create(values)
            )
        else:
            res = self.env[resource].create(values)
        if self._is_xref(xref):
            self._add_xref(xref, res.id, resource)
            self.store_resource_data(resource, xref, values, group=group)
            (
                resource_child, xref_child, field_child, field_parent
            ) = self._get_depending_xref(resource, xref)
            if resource_child and xref_child:
                self._add_xref(
                    xref_child, getattr(res, field_child)[0].id, resource_child)
                values_child = {k: v for (k, v) in values.items()}
                values_child[field_parent] = res.id
                self.store_resource_data(
                    resource_child, xref_child, values_child, group=group)
        return res

    def resource_write(
        self, resource, xref=None, values=None, raise_if_not_found=True, group=None
    ):
        """Update a test record.
        This function works as standard Odoo write() with follow improvements:

        * If resource is a record, xref is ignored (it should be None)
        * It resource is a string, xref must be a valid xref or an integer
        * If values is not supplied, record is restored to stored data values

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
        if isinstance(resource, basestring):
            record = self.resource_bind(
                xref, resource=resource, raise_if_not_found=raise_if_not_found
            )
        else:
            record = resource
            resource = resource._name
        if record:
            if values:
                values = self.unicodes(values)
            else:
                values = self.get_resource_data(resource, xref, group=group)
                values = self._purge_values(values)
            values = self._add_child_records(resource, xref, values, group=group)
            values = self.cast_types(resource, values, fmt="cmd", group=group)
            self.log_lvl_3(
                "🐞%s.resource_write(%s,%s,xref=%s)"
                % (resource, record.id, self.dict_2_print(values), xref)
            )
            if resource.startswith("account.move"):
                record.with_context(check_move_validity=False).write(values)
            else:
                record.write(values)
            # record.clear_caches()
        return record

    def resource_make(self, resource, xref, values=None, group=None):
        """Create or write a test record.
        This function is a hook to resource_write() or resource_create().
        """
        self.log_lvl_3(
            "🐞%s.resource_make(%s,xref=%s)"
            % (resource, self.dict_2_print(values), xref)
        )
        record = self.resource_write(
            resource, xref, values=values, raise_if_not_found=False, group=group
        )
        if not record:
            record = self.resource_create(
                resource, values=values, xref=xref, group=group)
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
        if not isinstance(data, dict):                               # pragma: no cover
            raise ValueError("Dictionary expected")
        if merge and merge != "zerobug":                             # pragma: no cover
            raise ValueError("Invalid merge value: use 'zerobug'")
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
                        # tnxl_field = self.translate(resource, field)
                        # data[xref][tnxl_field] = self.translate(
                        #     resource,
                        #     zerobug[field],
                        #     ttype="value",
                        #     fld_name=field,
                        # )
                        data[xref][field] = zerobug[field]
            tnxl_xref = self._get_conveyed_value(None, None, xref)
            if tnxl_xref != xref:
                data[tnxl_xref] = self.unicodes(data[xref])
                del data[xref]
            else:
                data[xref] = self.unicodes(data[xref])
            self.store_resource_data(
                resource, xref, data[tnxl_xref], group=group, name=name)

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
        if not isinstance(message, dict):                            # pragma: no cover
            raise ValueError("Dictionary expected")
        if "TEST_SETUP_LIST" not in message:                         # pragma: no cover
            raise ValueError("Key TEST_SETUP_LIST not found")
        group = group or "base"
        for resource in message["TEST_SETUP_LIST"]:
            item = "TEST_%s" % resource.upper().replace(".", "_")
            if item not in message:                                  # pragma: no cover
                raise ValueError("Key %s not found" % item)
        for resource in message["TEST_SETUP_LIST"]:
            self.log_lvl_1("🐞declare_all_data(%s,group=%s)" % (resource, group))
            item = "TEST_%s" % resource.upper().replace(".", "_")
            self.declare_resource_data(
                resource, message[item], group=group, merge=merge
            )

    def get_resource_data(self, resource, xref, group=None):
        """Get declared resource data; may be used to test compare.

        Args:
            resource (str): Odoo model name or name assigned, i.e. "res.partner"
            xref (str): external reference
            group (str): if supplied select specific group data; default is "base"

        Returns:
            dictionary with data or empty dictionary
        """
        group = group or "base"
        xref = self._get_conveyed_value(resource, None, xref)
        if (
            group in self.setup_data
            and resource in self.setup_data[group]
            and xref in self.setup_data[group][resource]
        ):
            return self.setup_data[group][resource][xref]
        return {}                                                    # pragma: no cover

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
        return []                                                    # pragma: no cover

    def get_resource_list(self, group=None):
        """Get declared resource list.

        Args:
            group (str): if supplied select specific group data; default is "base"
        """
        group = group or "base"
        if group in self.setup_data_list:
            return self.setup_data_list[group]
        return []                                                    # pragma: no cover

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
                raise ValueError("Module %s not found in the system" % locale_name)

    def install_language(self, iso, overwrite=None, force_translation=None):
        iso = iso or "en_US"
        overwrite = overwrite or False
        load = False
        lang_model = self.env["res.lang"]
        languages = lang_model.search([("code", "=", iso)])
        if not languages:                                            # pragma: no cover
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
        self, company, xref=None, partner_xref=None, values={}, group=None
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
            values (dict): company data to update immediately
            group (str): if supplied select specific group data; default is "base"

        Returns:
            default company for user
        """
        add_alias = True
        if not company:                                              # pragma: no cover
            company = self.env["res.company"].create(values)
            add_alias = True
        elif values:
            company.write(values)
        if xref:
            if not add_alias:
                self.add_xref(xref, "res.company", company.id)       # pragma: no cover
            elif not self.env.ref(xref, raise_if_not_found=False):
                self.add_alias_xref(
                    xref, "base.main_company", resource="res.company", group=group)
        if partner_xref:
            if not add_alias:                                        # pragma: no cover
                self.add_xref(partner_xref, "res.partner", company.partner_id.id)
            elif not self.env.ref(partner_xref, raise_if_not_found=False):
                self.add_alias_xref(
                    partner_xref, "base.main_partner",
                    resource="res.partner", group=group)
        if self.env.user.company_id != company:
            self.env.user.company_id = company                       # pragma: no cover
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
            "🎺 Starting test v2.0.3 (debug_level=%s)" % (self.debug_level))
        if locale:
            self.set_locale(locale)
        if lang:
            self.install_language(lang)
        self._convert_test_data(group=group)
        for resource in self.get_resource_list(group=group):
            for xref in self.get_resource_data_list(resource, group=group):
                self.resource_make(resource, xref, group=group)
        self.env["account.journal"].search([("update_posted", "!=", True)]).write(
            {"update_posted": True}
        )

    ############################################
    #                                          #
    #     WIZARD/FORM ENVIRONMENT TEST API     #
    #                                          #
    ############################################

    def resource_edit(
        self, resource, default={}, web_changes=[], actions=[], ctx={}
    ):
        """Server-side web form editing.
        Ordinary Odoo test use the primitive create() and write() function to manage
        test data. These methods create an update records, but they do not properly
        reflect the behaviour of user editing form with GUI interface.

        This function simulates the client-side form editing in the server-side.
        It works in the follow way:

        * It can simulate the form create record
        * It can simulate the form update record
        * It can simulate the user data input
        * It calls the onchange functions automatically
        * It may be used to call button in the form

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
        * required data in create must be supplied by default
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
        actions = actions or (
            ["create"] if isinstance(resource, basestring) else ["save"])
        actions = actions if isinstance(actions, (list, tuple)) else [actions]
        self.log_lvl_2("🐞%s.resource_edit(%s)" % (resource, actions), strict=True)
        self.log_lvl_3(
            "🐞%s.resource_edit(def=%s,chng=%s,act=%s,ctx=%s)" % (
                resource,
                self.dict_2_print(default),
                self.dict_2_print(web_changes),
                actions,
                self.dict_2_print(ctx))
        )
        if isinstance(resource, basestring):
            resource_model = resource
            vals = self.cast_types(resource_model, default or {}, fmt="cmd")
            record = self.env[resource_model].with_context(ctx).create(
                self._purge_values(
                    self._convert_to_write(
                        self._create_object(resource_model,
                                            default=vals,
                                            ctx=ctx),
                        new=True)))
        elif is_iterable(resource):
            record = resource
        else:
            if ctx:
                record = resource.with_context(ctx)
            else:
                record = resource
        for action in actions:
            result = self._exec_action(record, action, web_changes=web_changes)
            # Web changes execute, clear them
            web_changes = []
        return result

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
        """Execute the data downlod.
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
            binary obj downloaded form field
        """
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
            raise ValueError(
                "Filed %s not found in %s" % (field, res_model))
        return base64.decodestring(
            getattr(self.env[res_model].browse(act_windows["res_id"]),
                    field))

    def is_action(self, act_windows):
        return isinstance(act_windows, dict) and act_windows.get("type") in (
            "ir.actions.act_window",
            "ir.actions.client",
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
        if module and action_name:
            act_windows = self._wiz_launch_by_act_name(
                module, action_name, records=records, default=default, ctx=ctx
            )
        elif act_windows:
            act_windows = self._wiz_launch(
                act_windows, records=records, default=default, ctx=ctx
            )
        else:                                                        # pragma: no cover
            raise (ValueError, "Invalid action!")
        return self._wiz_execution(
            act_windows,
            button_name=button_name,
            web_changes=web_changes,
            button_ctx=button_ctx,
        )
