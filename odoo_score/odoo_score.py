# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import print_function,unicode_literals
from past.builtins import basestring

import os
import sys
from datetime import datetime, timedelta
from threading import Lock


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
        self.INCR_EXPIRATION_TIME = 5
        self.INCR_QUEUE_TIME = 5
        self.STRUCT = {}
        self.MANAGED_MODELS = {}
        self.LIVE = {}
        self.mutex = Lock()

    def lifetime(self, dbname, lifetime):
        # TODO: set life time per DB
        if lifetime >= 5 and lifetime <= 36000:
            self.EXPIRATION_TIME = lifetime
        return self.EXPIRATION_TIME

    def is_struct(self, model):
        return model >= 'a'

    def clean_cache(self, dbname, channel_id=None, model=None, lifetime=None):
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
    def model_list(self, dbname):
        return self.STRUCT.get(dbname, {})

    def init_struct_model(self, dbname, model):
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        if model:
            self.set_struct_model(dbname, model)
            self.reset_struct_cache(dbname, model)
            # self.STRUCT[dbname][model] = {}

    def set_struct_cache(self, dbname, model):
        self.mutex.acquire()
        if model.startswith('_'):
            self.STRUCT[dbname][model]['XPIRE'] = datetime.now() + timedelta(
                seconds=self.INCR_QUEUE_TIME)
        else:
            self.STRUCT[dbname][model]['XPIRE'] = datetime.now() + timedelta(
                    seconds=self.EXPIRATION_TIME)
        self.mutex.release()

    def reset_struct_cache(self, dbname, model):
        self.mutex.acquire()
        self.STRUCT[dbname][model]['XPIRE'] = False
        self.mutex.release()

    def age_struct_cache(self, dbname, model):
        self.mutex.acquire()
        if self.get_struct_attr(dbname, 'XPIRE'):
            self.STRUCT[dbname][model]['XPIRE'] = self.STRUCT[
                dbname][model]['XPIRE'] + timedelta(
                seconds=self.INCR_EXPIRATION_TIME)
        self.mutex.release()

    def init_struct(self, dbname):
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        for model in self.STRUCT[dbname]:
            if self.is_struct(model):
                self.reset_struct_cache(dbname, model)

    def set_struct_model(self, dbname, model):
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        if model:
            self.STRUCT[dbname][model] = self.STRUCT.get(
                dbname, {}).get(model, {})
            self.age_struct_cache(dbname, model)

    def get_struct_attr(self, dbname, attrib, default=None):
        if self.is_struct(attrib):
            default = default if default is not None else {}
            self.age_struct_cache(dbname, attrib)
        else:
            default = default if default is not None else ''
        return self.STRUCT.get(dbname, {}).get(attrib, default)

    def del_struct_model(self, dbname, model):
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        if model:
            self.STRUCT[dbname][model] = {}

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
    def init_channel(self, dbname, channel_id):
        self.set_channel_base(dbname, channel_id)
        self.reset_channel_cache(dbname, channel_id)
        for model in self.MANAGED_MODELS[dbname][channel_id]:
            if self.is_struct(model):
                self.reset_model_cache(dbname, channel_id, model)

    def set_channel_cache(self, dbname, channel_id):
        self.mutex.acquire()
        self.MANAGED_MODELS[dbname][channel_id]['XPIRE'] = datetime.now(
            ) + timedelta(seconds=self.EXPIRATION_TIME)
        self.mutex.release()

    def reset_channel_cache(self, dbname, channel_id):
        self.mutex.acquire()
        self.MANAGED_MODELS[dbname][channel_id]['XPIRE'] = False
        self.mutex.release()

    def age_channel(self, dbname, channel_id):
        self.mutex.acquire()
        if self.get_attr(dbname, channel_id, 'XPIRE'):
            self.MANAGED_MODELS[dbname][channel_id][
                'XPIRE'] = self.MANAGED_MODELS[dbname][channel_id][
                    'XPIRE'] + timedelta(seconds=self.INCR_EXPIRATION_TIME)
        self.mutex.release()

    def set_model_cache(self, dbname, channel_id, model):
        self.mutex.acquire()
        if model.startswith('_'):
            self.MANAGED_MODELS[dbname][channel_id][model][
                'XPIRE'] = datetime.now() + timedelta(
                seconds=self.INCR_QUEUE_TIME)
        else:
            self.MANAGED_MODELS[dbname][channel_id][model][
                'XPIRE'] = datetime.now() + timedelta(
                seconds=self.EXPIRATION_TIME)
        self.mutex.release()

    def reset_model_cache(self, dbname, channel_id, model):
        self.mutex.acquire()
        self.MANAGED_MODELS[dbname][channel_id][model]['XPIRE'] = False
        self.mutex.release()

    def age_model(self, dbname, channel_id, model):
        self.mutex.acquire()
        if self.get_model_attr(dbname, channel_id, model, 'XPIRE'):
            self.MANAGED_MODELS[dbname][channel_id][model][
                'XPIRE'] = self.MANAGED_MODELS[dbname][channel_id][model][
                    'XPIRE'] + timedelta(seconds=self.INCR_EXPIRATION_TIME)
        self.mutex.release()

    def get_channel_list(self, dbname):
        return self.MANAGED_MODELS.get(dbname, {})

    def set_channel_base(self, dbname, channel_id):
        self.MANAGED_MODELS[dbname] = self.MANAGED_MODELS.get(dbname, {})
        self.MANAGED_MODELS[dbname][
            channel_id] = self.MANAGED_MODELS.get(dbname, {}).get(
                channel_id, {})
        self.age_channel(dbname, channel_id)

    def get_channel_models(self, dbname, channel_id, default=None):
        default = default if default is not None else {}
        return self.MANAGED_MODELS.get(dbname, {}).get(channel_id, default)

    def set_attr(self, dbname, channel_id, attrib, value):
        self.MANAGED_MODELS[dbname][channel_id][attrib] = value

    def get_attr(self, dbname, channel_id, attrib, default=None):
        if attrib == 'XPIRE':
            expire = self.MANAGED_MODELS.get(dbname, {}).get(
                channel_id, {}).get(attrib, False)
            if expire and expire > datetime.now():
                return expire
            return False
        elif self.is_struct(attrib):
            default = default if default is not None else {}
        else:
            default = default if default is not None else ''
        return self.MANAGED_MODELS.get(dbname, {}).get(
            channel_id, {}).get(attrib, default)

    def del_attr(self, dbname, channel_id, attrib):
        self.MANAGED_MODELS[dbname][channel_id][attrib] = {}

    def get_model_attr(self, dbname, channel_id, model, attrib, default=None):
        if attrib == 'XPIRE':
            expire = self.MANAGED_MODELS.get(dbname, {}).get(
                channel_id, {}).get(model, {}).get(attrib, False)
            if expire and expire > datetime.now():
                return expire
            return False
        self.age_model(dbname, channel_id, model)
        return self.MANAGED_MODELS.get(dbname, {}).get(
            channel_id, {}).get(model, {}).get(attrib, default)

    def set_model_attr(self, dbname, channel_id, model, attrib, value):
        self.age_model(dbname, channel_id, model)
        self.MANAGED_MODELS[dbname][channel_id][model][attrib] = value

    def del_model_attr(self, dbname, channel_id, model, attrib):
        if attrib in self.MANAGED_MODELS[dbname][channel_id][model]:
            del self.MANAGED_MODELS[dbname][channel_id][model][attrib]

    def get_model_field_attr(self, dbname, channel_id, model, field, attrib,
                             default=None):
        return self.MANAGED_MODELS.get(dbname, {}).get(
            channel_id, {}).get(model, {}).get(attrib, {}).get(
                field, default)

    def set_model_field_attr(
            self, dbname, channel_id, model, field, attrib, value):
        self.MANAGED_MODELS[dbname][channel_id][model][attrib][
            field] = value

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
