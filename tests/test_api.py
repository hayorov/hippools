from hippools.api_client import ApiClient
from testutils import PoolTestCase


class APIV2Test(PoolTestCase):
    api_client = ApiClient()

    def test_allocate_pool(self):
        initial_pool = self.initial_pool
        pool = initial_pool.group.group_name
        netmask = 30
        stack_id = 'FFFFFFFFFFFFFFFFFFFFFF'
        stack_name = 'la_la_la'
        # self.api_client.allocate(pool, netmask, stack_id, stack_name)
        uri = '/api/v2/pools/%s?netmask=%s&stack_id=%s&stack_name=%s' % (pool, netmask, stack_id, stack_name)
        allocated = self.client.get(uri)

    def test_deallocate_pool(self):
        initial_pool = self.initial_pool
        pool = initial_pool.group.group_name
        netmask = 30
        stack_id = 'FFFFFFFFFFFFFFFFFFFFFF'
        stack_name = 'la_la_la'
        # self.api_client.allocate(pool, netmask, stack_id, stack_name)
        uri = '/api/v2/pools/%s?netmask=%s&stack_id=%s&stack_name=%s' % (pool, netmask, stack_id, stack_name)
        allocated = self.client.get(uri)

        pool_id = allocated.json['pool_id']
        delete_uri = '/api/v2/pools/%s?pool_id=%s' % (pool, pool_id)
        self.client.delete(delete_uri)
        print pool_id

