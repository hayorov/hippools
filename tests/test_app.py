from netaddr import IPAddress

from hippools.ip_pool import IPPoolGroup, IPInitialPool, IPPoolV2
from testutils import PoolTestCase


class IPPoolGroupTest(PoolTestCase):

    def test_create_new_pool_group(self):
        pool_group_name = 'test_group'

        pool_group = IPPoolGroup()
        new_group = pool_group.create_new_pool_group(pool_group_name)

        assert  new_group.group_name == pool_group_name

    def test_get_new_pool_group(self):
        pool_group_name = 'test_group_name'
        pool_group = IPPoolGroup()
        new_group = pool_group.create_new_pool_group(pool_group_name)

        get_pool = pool_group.get_pool_group(pool_group_name)

        assert  get_pool.group_name == new_group.group_name
        assert  get_pool.group_id == new_group.group_id


class IPInitialPoolTest(PoolTestCase):

    def test_create_new_initial_pool(self):
        pool_group_name = 'test_group_name'
        pool_group = IPPoolGroup()
        new_group = pool_group.create_new_pool_group(pool_group_name)
        ip = '192.168.1.1'
        mask = '255.255.0.0'
        initial_pool = IPInitialPool()
        pool = initial_pool.create_new_initial_pool(new_group.group_id, ip, mask)
        assert IPAddress(pool.cidr).value == IPAddress(ip).value


class IPPoolV2Test(PoolTestCase):

    def test_allocate(self):
        ip_pool_v2 = IPPoolV2()
        netmask = 30
        net_group_name = self.pool_group.group_name
        initial_pool = self.initial_pool
        stack_id = 'FFFFFFFF-bf15-4c80-8910-a5119b2e558d'
        stack_name = 'test name'
        new_allocated_pool = ip_pool_v2.allocate(netmask, net_group_name, stack_id, stack_name)

    def test_allocate_same_size(self):
        ip_pool_v2 = IPPoolV2()
        netmask = 30
        net_group_name = self.pool_group.group_name
        ip = '192.168.1.1'
        initial_pool = self.create_initial_pool(ip, netmask)
        stack_id = 'FFFFFFFF-bf15-4c80-8910-a5119b2e558d'
        stack_name = 'test name'
        new_allocated_pool = ip_pool_v2.allocate(netmask, net_group_name, stack_id, stack_name)

    def test_deallocate(self):
        ip_pool_v2 = IPPoolV2()
        allocated_pool = self.allocated_pool
        pool_id = allocated_pool.pool_id
        ip_pool_v2.deallocate(pool_id)
        print allocated_pool
