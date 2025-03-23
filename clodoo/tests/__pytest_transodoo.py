# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://www.zeroincombenze.org>)
#
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""
    Clodoo Regression Test Suite based on pytest
"""
# import pytest
from clodoo import transodoo

__version__ = "2.0.9"


class TestClass:
    def test_version_zerobug(self):
        ctx = {}
        ctx["mindroot"] = transodoo.read_stored_dict(ctx)
        model = "account.account.type"
        item = "report_type"
        src_ver = "6.1"
        tgt_ver = "10.0"
        ttype = "field"
        tnl_item = transodoo.translate_from_to(
            ctx, model, item, src_ver, tgt_ver, ttype=ttype
        )
        assert tnl_item == "type"
