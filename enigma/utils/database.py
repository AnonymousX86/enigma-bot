# -*- coding: utf-8 -*-
from datetime import date, datetime as d
from typing import List, Union

from sqlalchemy import create_engine, Column, Integer, Date, BigInteger, Text
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


def user_get_cash(user_id: int, cash: int) -> User:
    try:
        return update_profile(user_id=user_id, cash=get_single_user(user_id).user_cash + cash)
    finally:
        session = _Session()
        try:
            now = d.now()
            session.query(User).update({'last_daily': f'{now.year}-{now.month}-{now.day}'})
            session.commit()
        finally:
            session.close()


class Giveaway(Base):
    """Single giveaway, map object."""
    __tablename__ = 'giveaways'
    giveaway_id = Column(Integer, primary_key=True)
    message_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    data = Column(Text)


def get_giveaway_from_message(message_id: int) -> Union[Giveaway, None]:
    session = _Session()
    try:
        return session.query(Giveaway).filter_by(message_id=message_id).one_or_none()
    finally:
        session.close()


def create_giveaway(message_id: int, guild_id: int, data: str) -> Giveaway:
    """Creates giveaway in database.

    :param message_id: Giveaway's message ID.
    :param guild_id: Giveaway's guild ID.
    :param data: String representation of data.
    :return: New Giveaway object.
    """
    session = _Session()
    try:
        new_giveaway = Giveaway(
            message_id=message_id,
            guild_id=guild_id,
            data=data
        )
        session.add(new_giveaway)
        session.commit()
        return new_giveaway
    finally:
        session.close()


def delete_giveaway(message_id: int) -> bool:
    session = _Session()
    try:
        result = bool(session.query(Giveaway).filter_by(message_id=message_id).delete())
        session.commit()
        return result
    finally:
        session.close()
