from netaddr import IPSet, IPNetwork, IPAddress
from hippools import db
from hippools.db.api import get_session


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


def allocate(netmask):
    context = get_session()
    pool = db.api.free_pool_find_by_netnask(context, netmask)
    ip_set = pool_to_network(pool)
    ip_count = IPNetwork('0.0.0.0/%s' % netmask).size
    if ip_set.size == ip_count:
        pool.is_free = False
        pool.save()
        return pool
    a = list(ip_set.subnet(netmask))
    new_network = a[0]
    a = IPSet(a[1::])
    print new_network
    db.api.used_pool_add(context, {'initial_pool': pool.initial_pool, 'cidr': new_network})
    for free_pool in a.iter_cidrs():
        db.api.free_pool_add(context, {'initial_pool':  pool.initial_pool, 'cidr': free_pool})
    db.api.pool_delete(context, pool.pool_id)


    print a
    print ip_count
    print('allocate %s '% pool)


def pool_to_network(pool):
    bb = IPNetwork('%s/%s' % (IPAddress(pool.ip), IPAddress(pool.netmask)))
    print bb
    return bb


#init_db()
allocate(30)
#print db.api.pool_group_get_all(None)[0].group_name
