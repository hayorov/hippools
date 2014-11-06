import logging
from requests import get, delete

# temp
HOST = 'http://127.0.0.1:5001'
API_VERSION = '/api/v1'
allocate_url = '/pools/%s?ip_count=%s'
deallocate_url = '/pools/%s?ipset_id=%s'

logger = logging.getLogger(__name__)


def allocate(pool, ip_count):
    r = get(HOST + API_VERSION + allocate_url % (pool, ip_count))
    return r.json()


def deallocate(pool, ipset_id):
    r = delete(HOST + API_VERSION + deallocate_url % (pool, ipset_id))
    try:
        err = r.json()
    except:
        return True
    raise Exception(err['mesage'])


class ApiClient():
    allocate_url = '/pools/%s?netmask=%s&stack_id=%s&stack_name=%s'
    deallocate_url = '/pools/%s?pool_id=%s'

    def __init__(self, api_version=2, host='127.0.0.1', port=5001):
        if api_version != 2:
            raise NotImplementedError('api version %s not implemented' % api_version)
        self.uri = 'http://%s:%s/api/v%s' % (host, port, api_version)

    def allocate(self, pool, netmask, stack_id, stack_name):
        logger.info('allocate  pool %s, netmask %s, stack_id %s, stack_name %s' % (pool, netmask, stack_id, stack_name))
        r = get(self.uri + self.allocate_url % (pool, netmask, stack_id, stack_name))
        logger.info('response = %s' % r)
        return r.json()

    def deallocate(self, pool, pool_id):
        logger.debug('deallocate   pool %s, pool_id %s' % ( pool, pool_id))
        r = delete(self.uri + self.deallocate_url % (pool, pool_id))
        try:
            logger.debug('response = %s' % r)
            err = r.json()
        except:
            return True
        raise Exception(err['mesage'])



