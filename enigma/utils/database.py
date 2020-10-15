# -*- coding: utf-8 -*-
from datetime import date
from typing import List

from sqlalchemy import create_engine, Column, Integer, Date, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from enigma.settings import database_settings

_engine = create_engine(database_settings['url'])
_Session = sessionmaker()
_Session.configure(bind=_engine)

Base = declarative_base()


class User(Base):
    """Single user, map object."""
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    user_xp = Column(Integer)
    user_cash = Column(Integer)
    last_daily = Column(Date)

    def __repr__(self):
        return f"<User(" \
               f"user_id='{self.user_id}', " \
               f"user_xp='{self.user_xp}', " \
               f"user_cash='{self.user_cash}', " \
               f"last_daily='{self.last_daily}')>"


def get_all_users() -> List[User]:
    """Queries all users from database.

    :return: List of users from database.
    """
    session = _Session()
    try:
        return [row for row in session.query(User).all()]
    finally:
        session.close()


def get_single_user(user_id: int) -> User:
    """Queries single user from database.

    :param user_id: User ID which profile should be queried.
    :return: Existing or new user object.
    """
    session = _Session()
    try:
        q = session.query(User).filter_by(user_id=user_id).one_or_none()
        if q is None:
            new_user = create_profile(user_id=user_id)
            return new_user
        else:
            return q
    finally:
        session.close()


def create_profile(user_id: int) -> User:
    """Creates user profile in database.

    :param user_id: User ID to put in.
    :return: New user object.
    """
    session = _Session()
    try:
        new_user = User(
            user_id=user_id,
            user_xp=0,
            user_cash=0,
            last_daily=date(day=1, month=1, year=1970)
        )
        session.add(new_user)
        session.commit()
        return new_user
    finally:
        session.close()


def update_profile(user_id: int, xp: int = None, cash: int = None) -> User:
    """Updates user profile in database - sets XP or cash.

    :param user_id: User ID which profile should be updated.
    :param xp: XP amount.
    :param cash: Cash amount
    """
    if xp and cash:
        stmt = {'user_xp': xp, 'user_cash': cash}
    elif xp:
        stmt = {'user_xp': xp}
    elif cash:
        stmt = {'user_cash': cash}
    else:
        stmt = {}
    session = _Session()
    try:
        session.query(User).filter_by(user_id=user_id).update(stmt)
        session.commit()
        managed_user = session.query(User).filter_by(user_id=user_id).one()
        return managed_user
    finally:
        session.close()
