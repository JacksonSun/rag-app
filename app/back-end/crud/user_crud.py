#!/usr/bin/env python

# -*- encoding: utf-8 -*-


from sqlalchemy.orm import Session


from pydantic_schemas.user import UserCreate as PydanticUserCreate

from pydantic_schemas.user import User as PydancticUser

from db.models.user import User as DBUser


def create_user(db: Session, user: PydanticUserCreate):
    db_user = DBUser(
        username=user.username,
        email=user.email,
        token_id=user.token_id,
        bg=user.bg,
        bu=user.bu,
        job_grade=user.job_grade,
    )

    try:
        db.add(db_user)
        return db_user

    except Exception as e:
        raise ("Insert user failed.", e)


def update_user(db: Session, user: PydancticUser):
    db_user = db.query(DBUser).filter(DBUser.id == user.id).first()

    try:
        if db_user:
            db_user.username = user.username

            db_user.email = user.email

            db_user.token_id = user.token_id

            db_user.bg = user.bg
            db_user.bu = user.bu

            db_user.job_grade = user.job_grade
            return db_user

        else:
            raise ("User not found.")

    except Exception as e:
        raise ("Update user failed.", e)


def get_user(db: Session, user_id: int):
    try:
        return db.query(DBUser).filter(DBUser.id == user_id).first()

    except Exception as e:
        raise ("Update user failed.", e)
