from netaddr import IPSet, IPNetwork
from sqlalchemy import desc, event
from sqlalchemy.orm import Session
from hippools.db.exception import NotFound
from hippools.db.sqlalchemy import models

from hippools.db.sqlalchemy.session import get_session


def model_query(context, *args):
    session = _session(context)
    query = session.query(*args)

    return query


def _session(context):
    return context or get_session()

# ---------------------------------------

# @event.listens_for(models.InitialPool, 'after_insert')
# def initial_pool_after_insert(mapper, connection, target):
#     target.
#     free_pool_add()

# ---------------------------------------


def pool_group_get_all(context):
    result = model_query(context, models.PoolGroup).all()

    if not result:
        raise NotFound('no raw templates were found')

    return result


def pool_group_add(context, values):
    pool_group = models.PoolGroup()
    pool_group.update(values)
    pool_group.save(_session(context))
    return pool_group


def initial_pool_add(context, values):
    initial_pool = models.InitialPool()
    initial_pool.update(values)
    initial_pool.group_id = values['group_id'].group_id
    cidr = values['cidr']
    cidr = IPNetwork(cidr)
    initial_pool.ip = cidr.first
    initial_pool.netmask = cidr.netmask.value
    initial_pool.count = len(cidr)
    initial_pool.save(_session(context))
    return initial_pool


def initial_pool_get(context, pool_id):
    result = model_query(context, models.InitialPool).get(pool_id)
    return result


def initial_pool_delete(context, pool_id):
    pool = initial_pool_get(context=context, pool_id=pool_id)
    if not pool:
        raise NotFound('Pool %s not found' % pool_id)

    session = Session.object_session(pool)
    session.delete(pool)
    session.flush()


# ------used_pool--------


def used_pool_add(context, values):
    used_pool = models.Pool()
    used_pool.update(values)
    cidr = values['cidr']
    cidr = IPNetwork(cidr)
    used_pool.ip = cidr.first
    used_pool.is_free = False
    used_pool.netmask = cidr.netmask.value
    used_pool.count = len(cidr)
    used_pool.save(_session(context))
    return used_pool


def pool_get(context, pool_id):
    result = model_query(context, models.Pool).get(pool_id)
    return result


def pool_delete(context, pool_id):
    pool = pool_get(context=context, pool_id=pool_id)
    if not pool:
        raise NotFound('Pool %s not found' % pool_id)

    session = Session.object_session(pool)
    session.delete(pool)
    session.flush()


def pool_neighbors_get(context, pool_id):
    pool = pool_get(context=context, pool_id=pool_id)
    pool_ip = pool.ip
    up_neighbor = model_query(context, models.Pool).filter(models.Pool.ip > pool_ip).order_by(models.Pool.ip).first()
    down_neighbor = model_query(context, models.Pool).filter(models.Pool.ip < pool_ip).order_by(desc(models.Pool.ip)).first()
    return [up_neighbor, down_neighbor]


# --------free_pool-----------

def free_pool_add(context, values):
    free_pool = models.Pool()
    free_pool.update(values)
    cidr = values['cidr']
    cidr = IPNetwork(cidr)
    free_pool.ip = cidr.first
    free_pool.netmask = cidr.netmask.value
    free_pool.is_free = True
    free_pool.count = len(cidr)
    free_pool.save(_session(context))
    return free_pool


def free_pool_get(context, pool_id):
    result = model_query(context, models.Pool).get(pool_id)
    return result


def free_pool_find_by_netnask(context, netmask):
    query = model_query(context, models.Pool).filter(models.Pool.netmask >= netmask,
                                                     models.Pool.is_free == True).order_by(desc(models.Pool.netmask))
    return query.first()


