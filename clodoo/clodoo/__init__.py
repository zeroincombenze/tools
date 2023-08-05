# -*- coding: utf-8 -*-
from . import scripts

from . import clodoo_main as clodoo
from . import transodoo

try:
    from clodoocore import (
        extract_vals_from_rec,
        get_val_from_field,
        cvt_from_ver_2_ver,
        get_model_structure,
        is_valid_field,
        is_required_field,
        model_has_company,
        create_model_object,
    )
except:
    from clodoo.clodoocore import (
        extract_vals_from_rec,
        get_val_from_field,
        cvt_from_ver_2_ver,
        get_model_structure,
        is_valid_field,
        is_required_field,
        model_has_company,
        create_model_object,
    )
try:
    from clodoolib import build_odoo_param, crypt
except:
    from clodoo.clodoolib import build_odoo_param, crypt
