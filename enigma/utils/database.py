# -*- coding: utf-8 -*-
from datetime import date, datetime as d
from typing import List, Optional, Union, Tuple

from sqlalchemy import create_engine, Column, Integer, Date, BigInteger, Text, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from enigma.settings import database_url

_engine = create_engine(database_url())
_Session = sessionmaker()
_Session.configure(bind=_engine)

Base = declarative_base()


def check_connection() -> bool:
    session = _Session()
    try:
        return session.is_active
    finally:
        session.close()


class User(Base):
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    user_xp = Column(Integer)
    user_cash = Column(Integer)
    last_daily = Column(Date)


def get_all_users() -> List[User]:
    session = _Session()
    try:
        return [row for row in session.query(User).all()]
    finally:
        session.close()


def get_single_user(user_id: int) -> User:
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


def create_profile(user_id: int) -> Optional[User]:
    session = _Session()
    new_user = User(
        user_id=user_id,
        user_xp=0,
        user_cash=0,
        last_daily=date(day=1, month=1, year=1970)
    )
    try:
        session.add(new_user)
        session.commit()
        return new_user
    except IntegrityError:
        session.rollback()
        return None
    finally:
        session.close()


def update_profile(user_id: int, xp: int = None, cash: int = None) -> User:
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
    session = _Session()
    try:
        user = get_single_user(user_id)
        updated_user = update_profile(user_id=user_id, cash=user.user_cash + cash)
        now = d.now()
        session.query(User).update({'last_daily': f'{now.year}-{now.month}-{now.day}'})
        session.commit()
        return updated_user
    finally:
        session.close()


class Giveaway(Base):
    __tablename__ = 'giveaways'
    giveaway_id = Column(Integer, primary_key=True)
    message_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    data = Column(Text)


def get_giveaway_from_message(message_id: int) -> Optional[Giveaway]:
    session = _Session()
    try:
        return session.query(Giveaway).filter_by(message_id=message_id).one_or_none()
    finally:
        session.close()


def create_giveaway(message_id: int, guild_id: int, data: str) -> Optional[Giveaway]:
    create_guild(guild_id)
    session = _Session()
    new_giveaway = Giveaway(
        message_id=message_id,
        guild_id=guild_id,
        data=data
    )
    try:
        session.add(new_giveaway)
        session.commit()
        return new_giveaway
    except IntegrityError:
        session.rollback()
        return None
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


class Guild(Base):
    __tablename__ = 'guilds'
    guild_id = Column(BigInteger, primary_key=True)


def create_guild(guild_id: int) -> Optional[Guild]:
    session = _Session()
    new_guild = Guild(
        guild_id=guild_id
    )
    try:
        session.add(new_guild)
        session.commit()
        return new_guild
    except IntegrityError:
        session.rollback()
        return None
    finally:
        session.close()
