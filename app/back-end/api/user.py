from typing import Union
from crud.user_crud import create_user, update_user
from .utils import get_postgre_conn, convert_datetime_to_str
from services.external_api import get_eflow_data
from pydantic_schemas.user import UserCreate, UserUpdate
from fastapi.encoders import jsonable_encoder


def _get_eflow_user_data(username: str = "") -> dict:
    """
    Retrieves user data from eFlow API based on the provided username.

    Args:
        username (str): The username of the user to retrieve data for.

    Returns:
        dict: A dictionary containing the user data retrieved from the eFlow API.

    Raises:
        Exception: If an error occurs while retrieving the user data.
    """
    try:
        params = {
            "CaseID": "99999",  # Note: CaseID needs to be hardcoded as 99999
            "LogonID": username,
        }
        data = get_eflow_data("/Staff/getUserByLogonID", params)
        return data
    except Exception as e:
        raise e


def update_or_create_user(user: Union[UserUpdate, UserCreate]):
    """
    Updates or creates a user in the database based on the provided user object.

    Args:
        user: A user object containing the user's information.

    Returns:
        The result of the update or create operation.

    Raises:
        Exception: If an error occurs during the operation.
    """
    try:
        # 1. get eflow data
        eflow_data = _get_eflow_user_data()
        user.bu = eflow_data["SBU"]
        user.bg = eflow_data["SBG"]
        user.job_grade = eflow_data["Job"]
        # 2. update db
        db_session = get_postgre_conn()
        # if id in user - update
        # else - create
        if "id" in user.dict():
            ret = update_user(db_session, user)
        else:
            ret = create_user(db_session, user)

        db_session.commit()
        db_session.refresh(ret)
        db_session.close()
        return convert_datetime_to_str(jsonable_encoder(ret))
    except Exception as e:
        db_session.rollback()
        raise e
