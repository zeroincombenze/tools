# -*- coding: utf-8 -*-
# Copyright (C) 2018-2053 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
from __future__ import print_function, unicode_literals
import os
import sys

sys.path.insert(
    0, os.path.join(os.environ.get("HOME"), "build", "local", "odoo_score"))
import odoo_score           # noqa: E402
from zerobug import z0test  # noqa: E402

__version__ = '2.0.10'

MODULE_ID = 'odoo_score'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:

    def setup(self):
        self.cache = odoo_score.SingletonCache()
        self.db = "test"
        self.model = "test.model"
        self.channel = 1
        self.values = {"a": "A"}

    def test_01(self):
        lifetime = self.cache.clean_cache(self.db)
        self.assertGreaterEqual(lifetime, 5, msg_info="Cache init")
        self.assertLessEqual(lifetime, 99990)

        self.cache.set_struct_attr(self.db, "MALE", "XY")
        self.assertEqual(
            "XY",
            self.cache.get_struct_attr(self.db, "MALE"))
        self.cache.del_struct_attr(self.db, "MALE")
        self.assertEqual(
            "",
            self.cache.get_struct_attr(self.db, "MALE", default=""))

    def test_02(self):
        self.cache.init_struct_model(self.db, self.model)
        self.assertTrue(self.cache.model_list(self. db), msg_info="Cache model")
        self.assertEqual(1, len(self.cache.model_list(self. db)))

        self.cache.set_struct_model_attr(self.db, self.model, "MALE", "XY")
        self.assertEqual(
            "XY",
            self.cache.get_struct_model_attr(self.db, self.model, "MALE"))
        self.assertEqual(
            "XX",
            self.cache.get_struct_model_attr(
                self.db, self.model, "FEMALE", default="XX"))

        self.cache.reset_struct_cache(self.db, self.model)
        self.assertEqual(
            "",
            self.cache.get_struct_model_attr(self.db, self.model, "MALE"))
        self.assertEqual(
            "XX",
            self.cache.get_struct_model_attr(
                self.db, self.model, "FEMALE", default="XX")
        )

    def test_03(self):
        self.cache.init_channel(self.db, self.channel)
        self.assertTrue(self.cache.get_channel_list(self. db))
        self.assertEqual(1, len(self.cache.get_channel_list(self. db)))

        self.cache.set_model_attr(self.db, self.channel, self.model, "MALE", "XY")
        self.assertEqual(
            "XY",
            self.cache.get_model_attr(self.db, self.channel, self.model, "MALE"))
        self.assertEqual(
            "XX",
            self.cache.get_model_attr(
                self.db, self.channel, self.model, "FEMALE", default="XX"))

        self.cache.reset_model_cache(self.db, self.channel, self.model)
        self.assertEqual(
            "",
            self.cache.get_model_attr(self.db, self.channel, self.model, "MALE"))
        self.assertEqual(
            "XX",
            self.cache.get_model_attr(
                self.db, self.channel, self.model, "FEMALE", default="XX"))

    def test_04(self):
        self.cache.set_model_field_attr(
            self.db, self.channel, self.model, "name", "val", "Name")
        self.assertEqual(
            "Name",
            self.cache.get_model_field_attr(
                self.db, self.channel, self.model, "name", "val"),
            msg_info="Cache model field")

        self.cache.set_attr(self.db, self.channel, "LOGLEVEL", 1)
        self.assertEqual(
            1,
            self.cache.get_attr(self.db, self.channel, "LOGLEVEL"))

        self.cache.set_struct_model_attr(self.db, self.model, "field", self.values)
        self.assertEqual(
            self.values,
            self.cache.get_struct_model_attr(self.db, self.model, "field"))

        self.cache.set_model_field_attr(
            self.db, self.channel, self.model, "field", "val", self.values)
        self.assertEqual(
            self.values,
            self.cache.get_model_field_attr(
                self.db, self.channel, self.model, "field", "val"))


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
