# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
from sqlalchemy import Column, Integer, String

from .db import Base


class Client(Base):
    """Evolve customer: Odoo SdI channel credentials"""

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    client_id = Column(String(64), unique=True, nullable=False)
    client_key = Column(String(64), nullable=False)
    company_id = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "client_key": self.client_key,
            "company_id": self.company_id,
        }
