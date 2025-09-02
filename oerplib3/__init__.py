# -*- coding: utf-8 -*-
##############################################################################
#
#    OERPLib
#    Copyright (C) 2011-2013 Sébastien Alix.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""The `oerplib` module defines the :class:`OERP` class.

The :class:`OERP` class is the entry point to manage `OpenERP/Odoo` servers.
You can use this one to write `Python` programs that
performs a variety of automated jobs that communicate with a
`OpenERP/Odoo` server.

You can load a pre-configured :class:`OERP` session with the :func:`load`
function.
"""

__author__ = 'Antonio Maria Vigliotti'
__email__ = 'antoniomaria.vigliotti@gmail.com'
__licence__ = 'LGPL v3'
__version__ = '1.0.0'

#__all__ = ['OERP', 'error']

from oerplib3.oerp import OERP
from oerplib3 import error


