#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from db.models.feedback import Feedback as DBFeedback
from pydantic_schemas.feedback import FeedbackCreate as PydanticFeedbackCreate
from sqlalchemy.orm import Session


def create_feedback(db: Session, feedback: PydanticFeedbackCreate):
    """
    Creates a new feedback record in the database.

    Args:
    - db (Session): The database session.
    - feedback (PydanticFeedbackCreate): The feedback data to be created.

    Returns:
    - DBFeedback: The newly created feedback record.
    """
    db_feedback = DBFeedback(
        query=feedback.query,
        irrelevant_source=feedback.irrelevant_source,
        user_id=feedback.user_id,
    )
    try:
        db.add(db_feedback)
        return db_feedback
    except Exception as e:
        raise ("Insert feedback failed.", e)
