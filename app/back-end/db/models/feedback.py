#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..init_db import Base
from .mixins import TimestampMixin


class Feedback(TimestampMixin, Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False, index=True)
    irrelevant_source = Column(
        String,
        ForeignKey(
            "file_meta.uuid", ondelete="CASCADE", name="feedback_filemeta_uuid_fk"
        ),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="NO ACTION", name="feedback_user_id_fk"),
        nullable=False,
        index=True,
    )

    user = relationship("User", back_populates="feedback")
    file = relationship("File", back_populates="feedback")
