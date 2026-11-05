# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from .db import Base
from .document import fmt_datetime


class Call(Base):
    """Log of REST calls received, shown in the web page"""

    __tablename__ = "calls"

    id = Column(Integer, primary_key=True)
    called_at = Column(DateTime, default=datetime.now)
    action = Column(String(32))
    client_id = Column(String(64))
    archive = Column(Integer)
    esito = Column(Integer)
    message = Column(Text)

    def to_dict(self):
        return {
            "id": self.id,
            "called_at": fmt_datetime(self.called_at),
            "action": self.action,
            "client_id": self.client_id,
            "archive": self.archive,
            "esito": self.esito,
            "message": self.message,
        }
