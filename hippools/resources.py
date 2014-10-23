from flask.ext.restful import reqparse, abort, Resource
from hippools.db.utils import pool_to_network
from ip_pool import IPPool, IPPoolV2, IPPoolGroup, IPInitialPool
from config_parser import ALL_IP_POOLS

for ip_pool_name, ip_pool_size in ALL_IP_POOLS.iteritems():
    ALL_IP_POOLS[ip_pool_name] = IPPool(ip_pool_size)


def abort_if_ippol_not_doesnt_exist(pool_name):
    if pool_name not in ALL_IP_POOLS:
        abort(404, message='Pool %s not exist' % pool_name)


parser = reqparse.RequestParser()


class GetOnlyResource(Resource):
    def delete(self, *args, **kwargs):
        abort(405, message='Operation not allowed')

    def post(self, *args, **kwargs):
        abort(405, message='Operation not allowed')

    def put(self, *args, **kwargs):
        abort(405, message='Operation not allowed')


class IPPoolUtilization(GetOnlyResource):
    def get(self, pool_name):
        abort_if_ippol_not_doesnt_exist(pool_name)
        return {'pool_name': pool_name, 'utilization': getattr(ALL_IP_POOLS[pool_name], 'utilization')}


class PoolUsed(GetOnlyResource):
    def get(self, pool_name):
        abort_if_ippol_not_doesnt_exist(pool_name)
        return {'pool_name': pool_name, 'used': getattr(ALL_IP_POOLS[pool_name], 'used_size')}


class PoolFree(GetOnlyResource):
    def get(self, pool_name):
        abort_if_ippol_not_doesnt_exist(pool_name)
        return {'pool_name': pool_name, 'free': getattr(ALL_IP_POOLS[pool_name], 'size')}


class MyPool(GetOnlyResource):
    def get(self, pool_name):
        abort_if_ippol_not_doesnt_exist(pool_name)
        parser.add_argument('ip_count', type=int, help='set ip_count parameter')
        args = parser.parse_args()
        ip_count = int(args['ip_count'])
        if ip_count < 1:
            abort(400, message="Bad ip_count: %s" % ip_count)
        try:
            ip_set_hash = getattr(ALL_IP_POOLS[pool_name], 'allocate')(ip_count)
            ip_set = getattr(ALL_IP_POOLS[pool_name], 'get_allocated_ip_pools')(ip_set_hash)
            return {'ipset_id': ip_set_hash, 'pool_name': pool_name,
                    'allocated_ipset': [unicode(cidr) for cidr in ip_set.iter_cidrs()],
                    'allocated_range': getattr(ALL_IP_POOLS[pool_name], 'ip_sets_to_ip_range')(ip_set)}
        except IOError as e:
            abort(406, mesage="Not Acceptable %s" % e)

    def delete(self, pool_name):
        abort_if_ippol_not_doesnt_exist(pool_name)
        parser.add_argument('ipset_id', type=str, help='set ipset_id parameter')
        args = parser.parse_args()
        try:
            getattr(ALL_IP_POOLS[pool_name], 'deallocate')(args['ipset_id'])
            return '', 204
        except Exception as e:
            abort(406, mesage="Not Acceptable. (%s)" % e)


class SQLPool(GetOnlyResource):
    def get(self, pool_name):
        parser.add_argument('netmask', type=int, help='set netmask parameter')
        parser.add_argument('stack_id', type=str, help='set netmask parameter')
        parser.add_argument('stack_name', type=str, help='set netmask parameter')
        args = parser.parse_args()
        net_mask = int(args['netmask'])
        stack_id = args['stack_id']
        stack_name = args['stack_name']
        if 0 > net_mask > 32:
            abort(400, message="Bad mask: %s" % net_mask)
        try:
            ip_pool = IPPoolV2()
            allocated_pool = ip_pool.allocate(net_mask, stack_id, stack_name)
            return {'pool_id': allocated_pool.pool_id, 'pool_group': pool_name,
                    'allocated_network': pool_to_network(allocated_pool)}
        except IOError as e:
            abort(406, mesage="Not Acceptable %s" % e)

    def delete(self, pool_name):
        parser.add_argument('pool_id', type=str, help='set ipset_id parameter')
        args = parser.parse_args()
        pool_id = int(args['pool_id'])
        try:
            ip_pool = IPPoolV2()
            ip_pool.deallocate(pool_id)
            return '', 204
        except Exception as e:
            abort(406, mesage="Not Acceptable. (%s)" % e)


class PoolGroup(GetOnlyResource):
    def get(self):
        parser.add_argument('group_name', type=int, help='get group by group_id parameter')
        args = parser.parse_args()
        group_name = args['group_name']
        try:
            pool_group = IPPoolGroup()
            group = pool_group.get_pool_group(group_name)
            return {'group_id': group.group_id, 'group_name': group.group_name}
        except Exception as e:
            abort(406, mesage="Not Acceptable. (%s)" % e)

    def post(self):
        parser.add_argument('group_name', type=int, help='get group by group_name parameter')
        args = parser.parse_args()
        group_name = args['group_name']
        try:
            pool_group = IPPoolGroup()
            group = pool_group.create_new_pool_group(group_name)
            return {'group_id': group.group_id, 'group_name': group.group_name}
        except Exception as e:
            abort(406, mesage="Not Acceptable. (%s)" % e)


class InitialPool(GetOnlyResource):
    def post(self):
        parser.add_argument('group_id', type=int, help='get group by group_id parameter')
        parser.add_argument('ip', type=int, help='ip')
        parser.add_argument('mask', type=int, help='mask')
        args = parser.parse_args()
        group_id = args['group_id']
        ip = args['ip']
        mask = args['mask']
        try:
            initial_pool = IPInitialPool()
            pool = initial_pool.create_new_initial_pool(group_id, ip, mask)
            return {'inital_pool_id': pool.initial_pool_id, 'count': pool.count}
        except Exception as e:
            abort(406, mesage="Not Acceptable. (%s)" % e)

