from crud.feedback_crud import create_feedback
from fastapi.encoders import jsonable_encoder
from pydantic_schemas.feedback import Feedback, FeedbackCreate

from .utils import convert_datetime_to_str, get_postgre_conn


def create_a_feedback(feedback: FeedbackCreate) -> Feedback:
    """insert_feedback: Insert feedback into database

    Args:
        feedback (Feedback): Feedback object

    Returns:
        Feedback: Feedback object

    Raises:
        Exception: If an error occurs during the operation.
    """
    try:
        db_session = get_postgre_conn()
        ret = create_feedback(db_session, feedback)
        db_session.commit()
        db_session.refresh(ret)
        db_session.close()
        return convert_datetime_to_str(jsonable_encoder(ret))
    except Exception as e:
        db_session.rollback()
        raise e
