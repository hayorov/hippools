import datetime
import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, backref
from hippools.db.exception import DuplicateException
from hippools.db.sqlalchemy.session import get_session, get_engine

logger = logging.getLogger(__name__)

BASE = declarative_base()


class HippoolsBase(object):
    """Base class for Methane Models."""
    __table_args__ = {'mysql_engine': 'InnoDB'}
    __table_initialized__ = False
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    def save(self, session=None):
        """Save this object."""
        if not session:
            session = Session.object_session(self)
            if not session:
                session = get_session()
        session.add(self)
        try:
            session.flush()
        except IntegrityError as e:
            if str(e).endswith('is not unique'):
                raise DuplicateException(str(e))
            else:
                raise

    def expire(self, session=None, attrs=None):
        """Expire this object ()."""
        if not session:
            session = Session.object_session(self)
            if not session:
                session = get_session()
        session.expire(self, attrs)

    def refresh(self, session=None, attrs=None):
        """Refresh this object."""
        if not session:
            session = Session.object_session(self)
            if not session:
                session = get_session()
        session.refresh(self, attrs)

    def delete(self, session=None):
        """Delete this object."""
        self.deleted = True
        self.deleted_at = datetime.datetime.utcnow()
        if not session:
            session = Session.object_session(self)
            if not session:
                session = get_session()
        session.delete(self)
        session.flush()

    def update(self, values):
        """Make the model object behave like a dict"""
        for k, v in values.iteritems():
            setattr(self, k, v)


class PoolGroup(BASE, HippoolsBase):
    __tablename__ = 'pool_group'
    group_id = Column('id', Integer, primary_key=True)
    group_name = Column(String(50), nullable=False)


class InitialPool(BASE, HippoolsBase):
    __tablename__ = 'initial_pool'

    initial_pool_id = Column('id', Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey(PoolGroup.group_id), nullable=False)
    group = relationship(PoolGroup, backref=backref('pool'))
    ip = Column(BigInteger, nullable=False)
    netmask = Column(BigInteger, nullable=False)
    count = Column(Integer)


class Pool(BASE, HippoolsBase):
    __tablename__ = 'pool'
    pool_id = Column('id', Integer, primary_key=True)
    initial_pool_id = Column(Integer, ForeignKey(InitialPool.initial_pool_id), nullable=False)
    initial_pool = relationship(InitialPool, backref=backref('initial_pool'))
    ip = Column(BigInteger, nullable=False)
    netmask = Column(BigInteger, nullable=False)
    is_free = Column(Boolean, nullable=False)
    count = Column(Integer)
    stack_id = Column(String(64))
    stack_name = Column(String(128))


def create_all():
    BASE.metadata.create_all(get_engine())


def drop_all():
    BASE.metadata.drop_all(get_engine())