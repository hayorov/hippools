from netaddr import IPSet, IPNetwork
from hippools import db
from hippools.db.api import get_session
from hippools.db.utils import pool_to_network


def init_db():
    context = get_session()
    group1 = db.api.pool_group_add(context, {'group_name': '10.31_pool'})
    group2 = db.api.pool_group_add(context, {'group_name': '10.31_instances'})

    network = IPNetwork('10.31.214.0/22')
    initial_pool1 = db.api.initial_pool_add(context, {'group_id': group1, 'cidr': network})
    db.api.initial_pool_add(context, {'group_id': group2, 'cidr': IPNetwork('10.31.206.0/24')})
    db.api.free_pool_add(context, {'initial_pool': initial_pool1, 'cidr': IPNetwork('10.31.206.0/24')})

    # pool = db.api.used_pool_add(context, {'initial_pool': initial_pool1, 'cidr': IPNetwork('10.31.214.0/31')})

    # db.api.initial_pool_delete(None, initial_pool1.initial_pool_id)

    # db.api.used_pool_delete(context, pool.pool_id)

    # print pool


def allocate(netmask, net_group_name, stack_id=None, stack_name=None):
    context = get_session()
    network = IPNetwork('0.0.0.0/%s' % netmask)
    pool = db.api.free_pool_find_by_netmask_and_netgroup(context, network.netmask.value, net_group_name)
    ip_network = pool_to_network(pool)
    if ip_network.size == network.size:
        pool.is_free = False
        pool.stack_id = stack_id
        pool.stack_name = stack_name
        pool.save()
        return pool

    pool_list = list(ip_network.subnet(netmask))
    allocated_network = pool_list[0]
    pool_list = IPSet(pool_list[1::])
    print allocated_network
    allocated_pool = db.api.used_pool_add(context, {'initial_pool': pool.initial_pool, 'cidr': allocated_network,
                                                    'stack_id': stack_id, 'stack_name': stack_name})
    for free_pool in pool_list.iter_cidrs():
        db.api.free_pool_add(context, {'initial_pool':  pool.initial_pool, 'cidr': free_pool})
    db.api.pool_delete(context, pool.pool_id)
    print pool_list
    # print ip_count
    print('allocate %s ' % allocated_pool.pool_id)
    return allocated_pool


def deallocate(pool_id):
    context = get_session()
    pool = db.api.used_pool_get(context, pool_id)
    print('deallocate pool %s' % pool)
    [pool_1, pool_2] = db.api.pool_neighbors_get(context, pool_id)
    print('deallocate pool %s' % pool_1.is_free)
    print('deallocate pool %s' % pool_2.is_free)
    pool.is_free = True
    pool.save(context)



# init_db()
pool_a = allocate(28, '10.31_pool')
deallocate(pool_a.pool_id)

#print db.api.pool_group_get_all(None)[0].group_name
