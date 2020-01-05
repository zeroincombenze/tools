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

    def __init__(self):
        self.EXPIRATION_TIME = 60
        self.STRUCT = {}
        self.MANAGED_MODELS = {}

    def lifetime(self, dbname, lifetime):
        # TODO: set life time per DB
        if lifetime >= 5 and lifetime <= 3600:
            self.EXPIRATION_TIME = lifetime
        return self.EXPIRATION_TIME

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

    def is_struct(self, model):
        return model >= 'a'

    def get_channel_list(self, dbname):
        return self.MANAGED_MODELS.get(dbname, {})

    def get_attr_list(self, dbname, channel_id):
        return self.MANAGED_MODELS.get(dbname, {}).get(channel_id, {})

    def get_attr(self, dbname, channel_id, attrib, default=None):
        return self.MANAGED_MODELS.get(dbname, {}).get(
            channel_id, {}).get(attrib, default)

    def get_model_attr(self, dbname, channel_id, model, attrib, default=None):
        return self.MANAGED_MODELS.get(dbname, {}).get(
            channel_id, {}).get(model, {}).get(attrib, default)

    def get_model_field_attr(self, dbname, channel_id, model, field, attrib,
                             default=None):
        return self.MANAGED_MODELS.get(dbname, {}).get(
            channel_id, {}).get(model, {}).get(attrib, {}).get(
                field, default)

    def init_struct(self, dbname):
        self.MANAGED_MODELS[dbname] = {}

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

    def set_attr(self, dbname, channel_id, attrib, value):
        self.MANAGED_MODELS[dbname][channel_id][attrib] = value

    def set_model_attr(self, dbname, channel_id, model, attrib, value):
        self.MANAGED_MODELS[dbname][channel_id][model][attrib] = value

    def del_model_attr(self, dbname, channel_id, model, attrib):
        if attrib in self.MANAGED_MODELS[dbname][channel_id][model]:
            del self.MANAGED_MODELS[dbname][channel_id][model][attrib]

    def set_model_field_attr(self, dbname, channel_id, model, field, attrib, value):
        self.MANAGED_MODELS[dbname][channel_id][model][attrib][
            field] = value

    def model_list(self, dbname):
        return self.STRUCT.get(dbname, {})

    def get_struct_attr(self, dbname, attrib, default=None):
        default = default or {}
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

    def setup_models_in_channels(self, dbname, model):
        if not model:
            return
        where = [('name', '=', model)]
        for rec in self.env['synchro.channel.model'].search(where):
            if rec.synchro_channel_id.id not in self.get_channel_list(dbname):
                continue
            model = rec.name
            channel_id = rec.synchro_channel_id.id
            if self.get_model_attr(channel_id, model, 'EXPIRE',
                                   default=datetime.now()) > datetime.now():
                continue
            self.set_model(channel_id, model)
            self.set_model_attr(channel_id, model, 'EXPIRE',
                                datetime.now() + timedelta(
                                    seconds=(self.EXPIRATION_TIME) * 2))
            if rec.field_2complete:
                self.set_model_attr(channel_id, model, '2PULL', True)
            self.set_model_attr(
                channel_id, model, 'MODEL_KEY', rec.field_uname)
            self.set_model_attr(
                channel_id, model, 'SKEYS', eval(rec.search_keys))
            self.set_model_attr(
                channel_id, model, 'BIND', rec.counterpart_name)
            if rec.model_spec:
                self.set_model_attr(channel_id, model, 'SPEC', rec.model_spec)
            self.setup_channel_model_fields(rec)
        for channel_id in self.get_channel_list(dbname):
            if self.get_attr(channel_id, 'IDENTITY') == 'odoo':
                self.set_odoo_model(channel_id, model)

    def setup_channel_model_fields(self, model_rec):
        model = model_rec.name
        channel_id = model_rec.synchro_channel_id.id
        self.set_model(channel_id, model)
        self.set_odoo_model(channel_id, model, force=True)
        for field in self.env[
            'synchro.channel.model.fields'].search(
                [('model_id', '=', model_rec.id)]):
            if field.name:
                loc_name = field.name
            else:
                loc_name = '.%s' % field.counterpart_name
            if field.counterpart_name:
                ext_name = field.counterpart_name
            else:
                ext_name = '.%s' % field.name
            self.set_model_field_attr(
                channel_id, model, loc_name, 'LOC_FIELDS', ext_name)
            self.set_model_field_attr(
                channel_id, model, ext_name, 'EXT_FIELDS', loc_name)
            if field.apply:
                self.set_model_field_attr(
                    channel_id, model, loc_name, 'APPLY', field.apply)
            if field.protect and field.protect != '0':
                self.set_model_field_attr(
                    channel_id, model, loc_name, 'PROTECT', field.protect)
            if field.spec:
                self.set_model_field_attr(
                    channel_id, model, loc_name, 'SPEC', field.spec)

        # special names
        ext_ref = '%s_id' % self.get_attr(channel_id, 'PREFIX')
        self.set_model_field_attr(
            channel_id, model, 'id', 'LOC_FIELDS', '')
        self.set_model_field_attr(
            channel_id, model, ext_ref, 'LOC_FIELDS', 'id')
        self.set_model_field_attr(
            channel_id, model, 'id', 'EXT_FIELDS', ext_ref)

    def set_odoo_model(self, channel_id, model, force=None):
        if not force and self.get_attr(channel_id, model):
            return
        identity = self.get_attr(channel_id, 'IDENTITY')
        self.set_model(channel_id, model)
        skeys = ['name']
        for field in self.get_struct_attr(model):
            if not self.is_struct(field):
                continue
            if identity == 'odoo':
                self.set_model_field_attr(
                    channel_id, model, field, 'LOC_FIELDS', field)
                self.set_model_field_attr(
                    channel_id, model, field, 'EXT_FIELDS', field)
            else:
                self.set_model_field_attr(
                    channel_id, model, field, 'LOC_FIELDS', '.%s' % field)
                self.set_model_field_attr(
                    channel_id, model, '.%s' % field, 'EXT_FIELDS', field)
            self.set_model_field_attr(
                channel_id, model, field, 'PROTECT',
                self.get_struct_model_field_attr(model, field, 'protect'))
            if ((field == 'description' and model == 'account.tax') or
                    field == 'code'):
                skeys = [field]
        if model in self.SKEYS:
            self.set_model_attr(channel_id, model, 'SKEYS', self.SKEYS[model])
        else:
            self.set_model_attr(channel_id, model, 'SKEYS', [skeys])
