#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from sqlalchemy.orm import Session

from ..pydantic_schemas.qa_history import HistoryCreate as PydanticHistoryCreate
from ..db.models.qa_history import History as DBHistory


def create_new_qa_history(db: Session, qa_hist: PydanticHistoryCreate):
    db_hist = DBHistory(
        question=qa_hist.question,
        answer=qa_hist.answer,
        source=qa_hist.source,
        user_id=qa_hist.user_id,
    )
    db.add(db_hist)
    db.commit()
    db.refresh(db_hist)
    return db_hist


def get_all_qa_history(db: Session, user_id: int):
    return db.query(DBHistory).filter(DBHistory.user_id == user_id)
