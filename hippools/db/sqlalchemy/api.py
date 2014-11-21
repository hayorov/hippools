import logging
from netaddr import IPSet, IPNetwork
from sqlalchemy import desc
from sqlalchemy.orm import Session
from hippools.db.exception import NotFound
from hippools.db.sqlalchemy import models

from hippools.db.sqlalchemy.session import get_session
from hippools.db.utils import pool_to_network


logger = logging.getLogger(__name__)


def model_query(context, *args):
    session = _session(context)
    query = session.query(*args)

    return query


def _session(context):
    return context or get_session()

# ---------------------------------------


def concat_pool(context, pool):
    logger.debug('concat_pool pool id %s' % pool.pool_id)
    if pool.is_free:
        [up_neighbor, down_neighbor] = pool_neighbors_get(context, pool.pool_id)
        if up_neighbor:
            logger.debug('up_neighbor pool is free %s' % up_neighbor.is_free)
            concat_networks(context, pool, up_neighbor)

        if down_neighbor:
            logger.debug('down_neighbor pool is free %s' % down_neighbor.is_free)
            concat_networks(context, pool, down_neighbor)


def concat_networks(context, pool_1, pool_2):
    if pool_1.is_free and pool_2.is_free:
        network_1 = pool_to_network(pool_1)
        network_2 = pool_to_network(pool_2)
        if network_1.size == network_2.size:
            ipset = IPSet([network_1, network_2])
            cidr = ipset.iter_cidrs()[0]
            pool_1.ip = cidr.first
            pool_1.netmask = cidr.netmask.value
            count = len(pool_to_network(pool_1))
            pool_1.count = count
            pool_delete(context, pool_2.pool_id)
            concat_pool(context, pool_1)




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


def pool_group_get_by_name(context, netgroup_name):
    pool_group = model_query(context, models.PoolGroup).filter(models.PoolGroup.group_name == netgroup_name).first()
    return pool_group


# ----------------------------------

def initial_pool_add(context, values):
    initial_pool = models.InitialPool()
    initial_pool.update(values)
    cidr = IPNetwork(values['cidr'])
    initial_pool.ip = cidr.first
    initial_pool.netmask = cidr.netmask.value
    initial_pool.count = len(cidr)
    initial_pool.save(_session(context))
    free_pool_add(context, {'initial_pool': initial_pool, 'cidr': cidr})
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


def __initial_pool_get_by_pool_group(context, pool_group):
    result = model_query(context, models.InitialPool).filter(models.InitialPool.group == pool_group).all()
    return result

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


def free_pool_find_by_netmask_and_netgroup(context, netmask, netgroup_name):
    pool_group = pool_group_get_by_name(context, netgroup_name)
    query = model_query(context, models.Pool).filter(models.Pool.netmask <= netmask,
                                                     models.Pool.is_free == True,
                                                     ).join(models.InitialPool).filter(models.InitialPool.group == pool_group).order_by(desc(models.Pool.netmask), models.Pool.updated_at, models.Pool.created_at)
    return query.first()

