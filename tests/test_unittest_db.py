from netaddr import IPNetwork

from hippools.db.api import get_session
from hippools import db
from testutils import PoolTestCase


class DBTest(PoolTestCase):

    def test_create_group(self):
        context = get_session()
        group1 = db.api.pool_group_add(context, {'group_name': '10.31_pool'})
        group2 = db.api.pool_group_add(context, {'group_name': '10.31_instances'})
        assert group1 is not group2

    def test_create_initial_pool(self):
        context = get_session()
        group1 = db.api.pool_group_add(context, {'group_name': '10.31_pool'})
        network = IPNetwork('10.31.214.0/22')
        initial_pool1 = db.api.initial_pool_add(context, {'group_id': group1.group_id, 'cidr': network})

    def test_add_used_pool(self):
        context = get_session()
        group1 = db.api.pool_group_add(context, {'group_name': '10.31_pool'})
        network = IPNetwork('10.31.214.0/22')
        stack_name = 'stack_name FFF'
        stack_id = 'FFF-FFF-FFF-FFF'
        initial_pool1 = db.api.initial_pool_add(context, {'group_id': group1.group_id, 'cidr': network})
        allocated_pool = db.api.used_pool_add(context, {'initial_pool': initial_pool1, 'cidr': network,
                                                        'stack_id': stack_id, 'stack_name': stack_name})
        assert allocated_pool.stack_id == stack_id
        assert allocated_pool.stack_name == stack_name
        assert allocated_pool.initial_pool.initial_pool_id == initial_pool1.initial_pool_id

    def test_allocate_pool(self):
        context = get_session()
        group1 = db.api.pool_group_add(context, {'group_name': '10.31_pool'})
        network = IPNetwork('10.31.214.0/22')
        initial_pool1 = db.api.initial_pool_add(context, {'group_id': group1.group_id, 'cidr': network})
        network_new_pool = IPNetwork('0.0.0.0/30')
        pool = db.api.free_pool_find_by_netmask_and_netgroup(context, network_new_pool.netmask.value, group1.group_name)
        assert pool.count == initial_pool1.count




