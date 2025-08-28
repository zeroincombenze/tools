# -*- coding: utf-8 -*-
# Copyright (C) 2018-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import print_function, unicode_literals

# from past.builtins import basestring

# import os
# import sys
from datetime import datetime, timedelta
from threading import Lock

try:
    import odoo.release as release
    __db_protocol__ = 'psycopg2'
except ImportError:
    try:
        import openerp.release as release
        __db_protocol__ = 'psycopg2'
    except ImportError:
        release = ''
if release:
    majver = int(release.major_version.split('.')[0])
    if majver == 19:
        from . import odoo_score_19  # noqa: F401
    elif majver == 18:
        from . import odoo_score_18  # noqa: F401
    elif majver == 17:
        from . import odoo_score_17  # noqa: F401
    elif majver == 16:
        from . import odoo_score_16  # noqa: F401
    elif majver == 15:
        from . import odoo_score_15  # noqa: F401
    elif majver == 14:
        from . import odoo_score_14  # noqa: F401
    elif majver == 13:
        from . import odoo_score_13  # noqa: F401
    elif majver == 12:
        from . import odoo_score_12  # noqa: F401
    elif majver == 11:
        from . import odoo_score_11  # noqa: F401
    elif majver == 10:
        from . import odoo_score_10  # noqa: F401
    elif majver == 9:
        from . import odoo_score_9  # noqa: F401
    elif majver == 8:
        from . import odoo_score_8  # noqa: F401
    elif majver == 7:
        from . import odoo_score_7  # noqa: F401
    elif majver == 6:
        from . import odoo_score_6  # noqa: F401
else:
    try:
        import odoorpc  # noqa: F401
        __db_protocol__ = 'json'
    except ImportError:
        __db_protocol__ = ''
    try:
        import oerplib  # noqa: F401
        __db_protocol__ = 'xml' if not __db_protocol__ else 'json+xml'
    except ImportError:
        pass


__version__ = '2.0.11'

MODULE_ID = 'odoo_score'
TEST_FAILED = 1
TEST_SUCCESS = 0


class SingletonCache(object):
    # Internal cache uses 2 structures:
    # - MANAGED_MODELS
    #      \__ dbname
    #           \__ channel_id
    #                 |__ model
    #                 |     |__ field
    #                 |     |      \__ attrib / value
    #                 |     \__ attrib
    #                  \__ attrib
    # - STRUCT
    #      \__ dbname
    #             \__ model
    #                    \__ attrib

    #
    # General functions
    #
    def __init__(self):
        self.EXPIRATION_TIME = 86400
        self.INCR_EXPIRATION_TIME = 30
        self.INCR_QUEUE_TIME = 10
        self.STRUCT = {}
        self.MANAGED_MODELS = {}
        self.LIVE = {}
        self.mutex = Lock()

    def lifetime(self, dbname, lifetime):
        # TODO: set life time per DB: keep dbname for compatibily
        if lifetime >= 5 and lifetime <= 99990:
            self.EXPIRATION_TIME = lifetime
        return self.EXPIRATION_TIME

    def is_struct(self, model):
        return model >= 'a'

    def clean_cache(self, dbname, channel_id=None, model=None, lifetime=None):
        if channel_id:
            self.init_channel(dbname, channel_id)
        else:
            self.init_struct_model(dbname, model) if model else self.init_struct(dbname)
        if lifetime:
            self.lifetime(None, lifetime)
        return self.lifetime(None, 0)

    #
    # General functions (STRUCT specific)
    #
    def init_struct(self, dbname):
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        for model in self.STRUCT[dbname]:
            if self.is_struct(model):
                self.reset_struct_cache(dbname, model)

    def set_struct_attr(self, dbname, attr, value):
        self.mutex.acquire()
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        self.STRUCT[dbname][attr] = value
        self.mutex.release()

    def get_struct_attr(self, dbname, attrib, default=None):
        if self.is_struct(attrib):
            default = default if default is not None else {}
        else:
            default = default if default is not None else ''
        return self.STRUCT.get(dbname, {}).get(attrib, default)

    def del_struct_attr(self, dbname, attr):
        self.mutex.acquire()
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        if attr in self.STRUCT[dbname]:
            del self.STRUCT[dbname][attr]
        self.mutex.release()

    #
    # Channel functions (MANAGED specific)
    #
    def init_channel(self, dbname, channel_id):
        self.init_struct(dbname)
        self.reset_channel_cache(dbname, channel_id)
        for model in self.MANAGED_MODELS[dbname][channel_id]:
            if self.is_struct(model):
                self.reset_model_cache(dbname, channel_id, model)

    def reset_channel_cache(self, dbname, channel_id):
        self.mutex.acquire()
        self.set_channel_base(dbname, channel_id, no_mutex=True)
        self.MANAGED_MODELS[dbname][channel_id]["XPIRE"] = False
        self.mutex.release()

    def set_channel_cache(self, dbname, channel_id, no_mutex=False):
        if not no_mutex:
            self.mutex.acquire()
        self.set_channel_base(dbname, channel_id, no_mutex=True)
        self.MANAGED_MODELS[dbname][channel_id]["XPIRE"] = datetime.now() + timedelta(
            seconds=self.EXPIRATION_TIME
        )
        if not no_mutex:
            self.mutex.release()

    def age_channel(self, dbname, channel_id):
        self.set_channel_base(dbname, channel_id)
        self.mutex.acquire()
        if self.get_attr(dbname, channel_id, "XPIRE"):
            self.MANAGED_MODELS[dbname][channel_id]["XPIRE"] = self.MANAGED_MODELS[
                dbname
            ][channel_id]["XPIRE"] + timedelta(seconds=self.INCR_EXPIRATION_TIME)
        else:
            self.set_channel_cache(dbname, channel_id, no_mutex=True)
        self.mutex.release()

    def get_channel_list(self, dbname):
        return self.MANAGED_MODELS.get(dbname, {})

    def set_channel_base(self, dbname, channel_id, no_mutex=False):
        if not no_mutex:
            self.mutex.acquire()
        self.MANAGED_MODELS[dbname] = self.MANAGED_MODELS.get(dbname, {})
        self.MANAGED_MODELS[dbname][channel_id] = self.MANAGED_MODELS.get(
            dbname, {}).get(channel_id, {})
        if not no_mutex:
            self.mutex.release()

    #
    # Model functions (STRUCT specific)
    #
    def model_list(self, dbname):
        return self.STRUCT.get(dbname, {})

    def init_struct_model(self, dbname, model):
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        if model:
            self.reset_struct_cache(dbname, model)

    def reset_struct_cache(self, dbname, model):
        self.mutex.acquire()
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        if self.is_struct(model):
            self.STRUCT[dbname][model] = {}
            self.STRUCT[dbname][model]["XPIRE"] = False
        self.mutex.release()

    def set_struct_cache(self, dbname, model):
        self.mutex.acquire()
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        if self.is_struct(model):
            self.STRUCT[dbname][model] = self.STRUCT[dbname].get(model, {})
            self.STRUCT[dbname][model]["XPIRE"] = datetime.now() + timedelta(
                seconds=self.EXPIRATION_TIME)
        self.mutex.release()

    def age_struct_cache(self, dbname, model):
        self.mutex.acquire()
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        self.STRUCT[dbname][model] = self.STRUCT[dbname].get(model, {})
        if self.is_struct(model):
            if self.get_struct_attr(dbname, "XPIRE"):
                self.STRUCT[dbname][model]["XPIRE"] = (
                    self.STRUCT[dbname][model]["XPIRE"] + timedelta(
                        seconds=self.INCR_EXPIRATION_TIME))
            else:
                self.STRUCT[dbname][model]["XPIRE"] = datetime.now() + timedelta(
                    seconds=self.EXPIRATION_TIME)
        self.mutex.release()

    def reset_struct_model(self, dbname, model):
        # Deprecated: use reset_struct_cache()
        if model:
            self.reset_struct_cache(dbname, model)

    def set_struct_model(self, dbname, model):
        # Deprecated: use set_struct_cache()
        if model:
            self.age_struct_cache(dbname, model)

    def del_struct_model(self, dbname, model):
        self.STRUCT[dbname] = self.STRUCT.get(dbname, {})
        if model:
            self.STRUCT[dbname][model] = {}

    #
    # Model of channel functions (MANAGED specific)
    #
    def get_channel_models(self, dbname, channel_id, default=None):
        default = default if default is not None else {}
        return self.MANAGED_MODELS.get(dbname, {}).get(channel_id, default)

    def reset_model_cache(self, dbname, channel_id, model):
        self.mutex.acquire()
        self.set_channel_base(dbname, channel_id, no_mutex=True)
        if self.is_struct(model):
            self.MANAGED_MODELS[dbname][channel_id][model] = {}
            self.MANAGED_MODELS[dbname][channel_id][model]["XPIRE"] = False
        self.mutex.release()

    def set_model_cache(self, dbname, channel_id, model):
        self.mutex.acquire()
        self.set_channel_base(dbname, channel_id, no_mutex=True)
        if self.is_struct(model):
            self.MANAGED_MODELS[dbname][channel_id][model] = (
                self.MANAGED_MODELS[dbname].get(channel_id, {}).get(model, {}))
            self.MANAGED_MODELS[dbname][channel_id][model]["XPIRE"] = (
                datetime.now() + timedelta(seconds=self.EXPIRATION_TIME))
        self.mutex.release()

    def age_model(self, dbname, channel_id, model):
        self.mutex.acquire()
        self.set_channel_base(dbname, channel_id, no_mutex=True)
        if self.is_struct(model):
            self.MANAGED_MODELS[dbname][channel_id][model] = (
                self.MANAGED_MODELS[dbname].get(channel_id, {}).get(model, {}))
            if self.get_model_attr(dbname, channel_id, model, "XPIRE"):
                self.MANAGED_MODELS[dbname][channel_id][model][
                    "XPIRE"
                ] = self.MANAGED_MODELS[dbname][channel_id][model]["XPIRE"] + timedelta(
                    seconds=self.INCR_EXPIRATION_TIME
                )
            else:
                self.MANAGED_MODELS[dbname][channel_id][model]["XPIRE"] = datetime.now(
                    ) + timedelta(seconds=self.EXPIRATION_TIME)
        self.mutex.release()

    #
    # Model attribute functions (STRUCT specific)
    #
    def get_struct_model_attr(self, dbname, model, attrib, default=None):
        if attrib == "XPIRE":
            expire = self.STRUCT.get(dbname, {}).get(model, {}).get(attrib, False)
            if expire and expire > datetime.now():
                return expire
            return False
        elif not self.is_struct(attrib):
            default = default if default is not None else ''
            self.set_struct_cache(dbname, model)
            return self.STRUCT.get(dbname, {}).get(model, {}).get(attrib, default)
        default = default if default is not None else {}
        self.set_struct_cache(dbname, model)
        if self.get_struct_model_attr(dbname, model, "XPIRE"):
            return self.STRUCT.get(dbname, {}).get(model, {}).get(attrib, default)
        return default

    def set_struct_model_attr(self, dbname, model, attrib, value):
        self.set_struct_cache(dbname, model)
        self.STRUCT[dbname][model][attrib] = value

    #
    # Model attribute functions (MANAGED specific)
    #
    def set_attr(self, dbname, channel_id, attrib, value):
        self.set_model_cache(dbname, channel_id, attrib)
        self.MANAGED_MODELS[dbname][channel_id][attrib] = value

    def get_attr(self, dbname, channel_id, attrib, default=None):
        if attrib == "XPIRE":
            expire = (
                self.MANAGED_MODELS.get(dbname, {})
                .get(channel_id, {})
                .get(attrib, False)
            )
            if expire and expire > datetime.now():
                return expire
            return False
        elif not self.is_struct(attrib):
            default = default if default is not None else ''
            return (
                self.MANAGED_MODELS.get(dbname, {}).get(channel_id, {}).get(attrib,
                                                                            default)
            )
        default = default if default is not None else {}
        if self.get_attr(dbname, channel_id, "XPIRE"):
            return (
                self.MANAGED_MODELS.get(dbname, {}).get(channel_id, {}).get(attrib,
                                                                            default)
            )
        return default

    def del_attr(self, dbname, channel_id, attrib):
        self.age_channel(dbname, channel_id)
        self.MANAGED_MODELS[dbname][channel_id][attrib] = {}

    #
    # Model attribute in channel functions (MANAGED specific)
    #
    def get_model_attr(self, dbname, channel_id, model, attrib, default=None):
        if attrib == "XPIRE":
            expire = (
                self.MANAGED_MODELS.get(dbname, {})
                .get(channel_id, {})
                .get(model, {})
                .get(attrib, False)
            )
            if expire and expire > datetime.now():
                return expire
            return False
        if not self.is_struct(attrib):
            default = default if default is not None else ''
            return (
                self.MANAGED_MODELS.get(dbname, {})
                .get(channel_id, {})
                .get(model, {})
                .get(attrib, default)
            )
        default = default if default is not None else {}
        if self.get_model_attr(dbname, channel_id, model, "XPIRE"):
            return (
                self.MANAGED_MODELS.get(dbname, {})
                .get(channel_id, {})
                .get(model, {})
                .get(attrib, default)
            )
        return default

    def set_model_attr(self, dbname, channel_id, model, attrib, value):
        self.set_model_cache(dbname, channel_id, model)
        self.MANAGED_MODELS[dbname][channel_id][model][attrib] = value

    def del_model_attr(self, dbname, channel_id, model, attrib):
        if attrib in self.MANAGED_MODELS[dbname][channel_id][model]:
            del self.MANAGED_MODELS[dbname][channel_id][model][attrib]

    #
    # Model field functions (STRUCT specific)
    #

    def get_struct_model_field_attr(self, dbname, model, field, attrib, default=None):
        if self.get_struct_model_attr(dbname, model, "XPIRE"):
            return (
                self.STRUCT.get(dbname, {})
                .get(model, {})
                .get(field, {})
                .get(attrib, default)
            )
        return default

    #
    # Model field functions (MANAGED specific)
    #
    def get_model_field_attr(
        self, dbname, channel_id, model, field, attrib, default=None
    ):
        if not self.is_struct(attrib):
            default = default if default is not None else ''
            return (
                self.MANAGED_MODELS.get(dbname, {})
                .get(channel_id, {})
                .get(model, {})
                .get(attrib, {})
                .get(field, default)
            )
        default = default if default is not None else {}
        if self.get_attr(dbname, channel_id, "XPIRE"):
            return (
                self.MANAGED_MODELS.get(dbname, {})
                .get(channel_id, {})
                .get(model, {})
                .get(attrib, {})
                .get(field, default)
            )
        return default

    def set_model_field_attr(self, dbname, channel_id, model, field, attrib, value):
        # deprecated
        self.age_channel(dbname, channel_id)
        self.MANAGED_MODELS[dbname][channel_id][model][attrib] = (
            self.MANAGED_MODELS[dbname][channel_id][model].get(attrib, {}))
        self.MANAGED_MODELS[dbname][channel_id][model][attrib][field] = (
            self.MANAGED_MODELS[dbname][channel_id][model][attrib].get(field, {}))
        self.MANAGED_MODELS[dbname][channel_id][model][attrib][field] = value
