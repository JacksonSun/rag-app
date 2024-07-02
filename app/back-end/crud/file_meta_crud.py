#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from sqlalchemy.orm import Session

from pydantic_schemas.file_meta import FileCreate as PydancticFileCreate
from db.models.file_meta import File as DBFile


def create_new_file(db: Session, file: PydancticFileCreate):
    """
    Create a new file in the database.

    Args:
        db (Session): The database session.
        file (PydancticFileCreate): The file to be created.

    Returns:
        DBFile: The created file.

    Raises:
        Exception: If the file meta insertion fails.
        IntegrityError: If the file already exists in the database.
    """
    db_file = DBFile(
        filename=file.filename,
        blob_name=file.blob_name,
        url=file.url,
        summary=file.summary,
        user_id=file.user_id,
        uuid=file.uuid,
    )
    try:
        db.add(db_file)
        return db_file
    except IntegrityError as ie:
        raise ("Duplicated file.", ie)
    except Exception as e:
        raise ("Insert file meta failed.", e)


def get_files(db: Session, user_id: int):
    """
    Retrieve files from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user whose files to retrieve. If 0 or negative, retrieve all files.

    Returns:
        List[DBFile]: A list of DBFile objects representing the retrieved files.
    """
    if user_id > 0:
        return db.query(DBFile).filter(DBFile.user_id == user_id).all()
    else:
        return db.query(DBFile).all()
