import logging as lg

from contextlib import contextmanager
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Integer, String)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

RegisterBase = declarative_base()
log = lg.getLogger(__name__)


@contextmanager
def session_scope(engine):
    """Provide a transactional scope around a series of operations."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        log.error(f'Session exception : {e}')
        session.rollback()
    finally:
        session.close()


class User(RegisterBase):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    snowflake = Column(BigInteger)
    reddit_name = Column(String)
    utc_added = Column(DateTime)
    locked = Column(Boolean)
    verified = Column(Boolean)
    last_status = Column(String)
    since = Column(DateTime)
    last_online = Column(DateTime)
    deleted = Column(Boolean)
    up_votes = Column(Integer)
    down_votes = Column(Integer)

    def __repr__(self):
        return "<User(id='%s', sf='%s', rd='%s')>" % \
            (self.id, self.snowflake, self.reddit_name)
