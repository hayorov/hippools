from flask.ext.restful import reqparse, abort, Resource
from ip_pool import IPPool
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
        abort_if_ippol_not_doesnt_exist(pool_name)
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
            ip_set_hash = getattr(ALL_IP_POOLS[pool_name], 'allocate')(net_mask)
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

