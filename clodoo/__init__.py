from . import clodoo as clodoo
from . import transodoo
from clodoocore import (extract_vals_from_rec,
                        get_val_from_field,
                        cvt_from_ver_2_ver,
                        get_model_structure,
                        cvt_value_from_ver_to_ver)
from clodoolib import (build_odoo_param,crypt)
from transodoo import read_stored_dict