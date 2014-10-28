import logging
import sqlalchemy.interfaces
import sqlalchemy.orm
import sqlalchemy.engine
from sqlalchemy.exc import DisconnectionError
from hippools import config_parser


logger = logging.getLogger(__name__)

_ENGINE = None
_MAKER = None
SQL_CONNECTION = config_parser.SQL_CONNECTION
SQL_IDLE_TIMEOUT = 3600


def get_session(autocommit=True, expire_on_commit=False):
    """Return a SQLAlchemy session."""
    global _MAKER

    if _MAKER is None:
        _MAKER = get_maker(get_engine(), autocommit, expire_on_commit)
    return _MAKER()


class SynchronousSwitchListener(sqlalchemy.interfaces.PoolListener):

    """Switch sqlite connections to non-synchronous mode"""

    def connect(self, dbapi_con, con_record):
        dbapi_con.execute("PRAGMA synchronous = OFF")


class MySQLPingListener(object):

    """
    Ensures that MySQL connections checked out of the
    pool are alive.

    Borrowed from:
    http://groups.google.com/group/sqlalchemy/msg/a4ce563d802c929f
    """

    def checkout(self, dbapi_con, con_record, con_proxy):
        try:
            dbapi_con.cursor().execute('select 1')
        except dbapi_con.OperationalError as ex:
            if ex.args[0] in (2006, 2013, 2014, 2045, 2055):
                logger.warn('Got mysql server has gone away: %s', ex)
                raise DisconnectionError("Database server went away")
            else:
                raise


def get_engine():
    """Return a SQLAlchemy engine."""
    global _ENGINE
    if _ENGINE is None:
        connection_dict = sqlalchemy.engine.url.make_url(_get_sql_connection())
        engine_args = {
            "pool_recycle": _get_sql_idle_timeout(),
            "echo": False,
            'convert_unicode': True
        }

        if 'mysql' in connection_dict.drivername:
            engine_args['listeners'] = [MySQLPingListener()]

        _ENGINE = sqlalchemy.create_engine(_get_sql_connection(),
                                           **engine_args)
    return _ENGINE


def get_maker(engine, autocommit=True, expire_on_commit=False):
    """Return a SQLAlchemy sessionmaker using the given engine."""
    ses = sqlalchemy.orm.sessionmaker(
        bind=engine,
        autocommit=autocommit,
        expire_on_commit=expire_on_commit)
    return sqlalchemy.orm.scoped_session(ses)


def _get_sql_connection():
    return SQL_CONNECTION


def _get_sql_idle_timeout():
    return SQL_IDLE_TIMEOUT

