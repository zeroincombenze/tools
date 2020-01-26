# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import print_function,unicode_literals
from past.builtins import basestring

import os
import sys
from datetime import datetime, timedelta

__version__ = "0.1.0.9"

MODULE_ID = 'odoo_score'
TEST_FAILED = 1
TEST_SUCCESS = 0


class Orm10(object):

    def __init__(self):
        pass


class SingletonCache(object):

    #
    # General functions
    #
    def __init__(self):
        self.EXPIRATION_TIME = 3600
        self.STRUCT = {}
        self.MANAGED_MODELS = {}

    def lifetime(self, dbname, lifetime):
        # TODO: set life time per DB
        if lifetime >= 5 and lifetime <= 36000:
            self.EXPIRATION_TIME = lifetime
        return self.EXPIRATION_TIME

    def is_struct(self, model):
        return model >= 'a'

    def clean_cache(self, dbname, channel_id=None, model=None, lifetime=None):
        self.setup_channels(dbname)
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        self.MANAGED_MODELS[dbname] = self.MANAGED_MODELS.get(dbname, {})
        if model:
            self.STRUCT[dbname][model] = {}
        else:
            self.STRUCT[dbname] = {}
        if channel_id:
            if model:
                self.MANAGED_MODELS[dbname][channel_id] = self.MANAGED_MODELS[
                    dbname].get(channel_id, {})
                self.MANAGED_MODELS[dbname][channel_id][model] = {}
            else:
                self.MANAGED_MODELS[dbname][channel_id] = {}
        else:
            self.MANAGED_MODELS[dbname] = {}
        if lifetime:
            self.lifetime(lifetime)
        return self.lifetime(0)
    #
    # Model functions
    #
    def age_struct_cache(self, dbname, model):
        if self.get_struct_attr(dbname, 'XPIRE'):
            self.STRUCT[dbname][model][
                'XPIRE'] = self.STRUCT[dbname][model][
                                'XPIRE'] + timedelta(seconds=3)
        else:
            self.STRUCT[dbname][model][
                'XPIRE'] = datetime.now() + timedelta(
                seconds=self.EXPIRATION_TIME)

    def init_struct(self, dbname):
        # self.MANAGED_MODELS[dbname] = {}
        self.STRUCT[dbname] = {}

    def set_struct_model(self, dbname, model):
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        if model:
            self.STRUCT[dbname][model] = self.STRUCT.get(
                dbname, {}).get(model, {})
            self.age_struct_cache(dbname, model)

    def get_struct_attr(self, dbname, attrib, default=None):
        if self.is_struct(attrib):
            default = default if default is not None else {}
        else:
            default = default if default is not None else ''
        return self.STRUCT.get(dbname, {}).get(attrib, default)

    def get_struct_model_attr(self, dbname, model, attrib, default=None):
        if attrib == 'XPIRE':
            expire = self.STRUCT.get(dbname, {}).get(attrib, False)
            if expire and expire > datetime.now():
                return expire
            return False
        elif self.is_struct(attrib):
            default = default if default is not None else {}
            self.set_struct_model(self, dbname, model)
        else:
            default = default if default is not None else ''
        return self.STRUCT.get(dbname, {}).get(model, {}).get(
            attrib, default)

    #
    # Channel functions
    #
    def age_cache(self, dbname, channel_id, model):
        if self.get_attr(channel_id, dbname, 'XPIRE'):
            self.MANAGED_MODELS[dbname][channel_id][model][
                'XPIRE'] = self.MANAGED_MODELS[dbname][channel_id][model][
                                'XPIRE'] + timedelta(seconds=2)
        else:
            self.MANAGED_MODELS[dbname][channel_id][model][
                'XPIRE'] = datetime.now() + timedelta(
                seconds=self.EXPIRATION_TIME)

    def get_channel_list(self, dbname):
        return self.MANAGED_MODELS.get(dbname, {})

    def get_attr_list(self, dbname, channel_id, default=None):
        default = default if default is not None else {}
        return self.MANAGED_MODELS.get(dbname, {}).get(channel_id, default)

    def get_attr(self, dbname, channel_id, attrib, default=None):
        if attrib == 'XPIRE':
            expire = self.MANAGED_MODELS.get(dbname, {}).get(
                channel_id, {}).get(attrib, False)
            if expire and expire > datetime.now():
                return expire
            return False
        elif self.is_struct(attrib):
            default = default if default is not None else {}
            # set_struct_model(self, dbname, model)
        else:
            default = default if default is not None else ''
        return self.MANAGED_MODELS.get(dbname, {}).get(
            channel_id, {}).get(attrib, default)

    def get_model_attr(self, dbname, channel_id, model, attrib, default=None):
        self.age_cache(dbname, channel_id, model)
        return self.MANAGED_MODELS.get(dbname, {}).get(
            channel_id, {}).get(model, {}).get(attrib, default)

    def get_model_field_attr(self, dbname, channel_id, model, field, attrib,
                             default=None):
        return self.MANAGED_MODELS.get(dbname, {}).get(
            channel_id, {}).get(model, {}).get(attrib, {}).get(
                field, default)

    def init_channel(self, dbname, channel_id):
        self.MANAGED_MODELS[dbname] = {}
        self.MANAGED_MODELS[dbname][channel_id] = {}

    def init_struct_model(self, dbname, model):
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        if model:
            self.STRUCT[dbname][model] = {}

    def set_channel(self, dbname, channel_id):
        self.MANAGED_MODELS[dbname] = self.MANAGED_MODELS.get(dbname, {})
        self.MANAGED_MODELS[dbname][
            channel_id] = self.MANAGED_MODELS.get(dbname, {}).get(
                channel_id, {})

    def set_model(self, dbname, channel_id, model):
        self.set_channel(dbname, channel_id)
        self.MANAGED_MODELS[dbname][channel_id][
            model] = self.MANAGED_MODELS.get(dbname, {})[
                channel_id].get(model, {})
        self.set_model_attr(dbname, channel_id, model, 'LOC_FIELDS', {})
        self.set_model_attr(dbname, channel_id, model, 'EXT_FIELDS', {})
        self.set_model_attr(dbname, channel_id, model, 'APPLY', {})
        self.set_model_attr(dbname, channel_id, model, 'PROTECT', {})
        self.set_model_attr(dbname, channel_id, model, 'SPEC', {})
        self.set_model_attr(dbname, channel_id, model, 'REQUIRED', {})

    def set_attr(self, dbname, channel_id, attrib, value):
        self.MANAGED_MODELS[dbname][channel_id][attrib] = value

    def set_model_attr(self, dbname, channel_id, model, attrib, value):
        self.MANAGED_MODELS[dbname][channel_id][model][attrib] = value

    def del_model_attr(self, dbname, channel_id, model, attrib):
        if attrib in self.MANAGED_MODELS[dbname][channel_id][model]:
            del self.MANAGED_MODELS[dbname][channel_id][model][attrib]

    def set_model_field_attr(
            self, dbname, channel_id, model, field, attrib, value):
        self.MANAGED_MODELS[dbname][channel_id][model][attrib][
            field] = value

    def model_list(self, dbname):
        return self.STRUCT.get(dbname, {})

    def get_struct_attr(self, dbname, attrib, default=None):
        default = default if default is not None else {}
        return self.STRUCT.get(dbname, {}).get(attrib, default)

    def get_struct_model_attr(self, dbname, model, attrib, default=None):
        return self.STRUCT.get(dbname, {}).get(model, {}).get(
            attrib, default)

    def get_struct_model_field_attr(self, dbname, model, field, attrib,
                                    default=None):
        return self.STRUCT.get(dbname, {}).get(model, {}).get(
            field, {}).get(attrib, default)

    def set_struct_model(self, dbname, model):
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        if model:
            self.STRUCT[dbname][model] = self.STRUCT.get(
                dbname, {}).get(model, {})

    def set_struct_model_attr(self, dbname, model, attrib, value):
        self.STRUCT[dbname][model][attrib] = value
