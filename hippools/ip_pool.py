import os
from netaddr import IPSet, IPRange, IPNetwork
import logging
from hashlib import md5
from cPickle import load, dump
from lockfile import FileLock
from config_parser import DB_PATH, LOGFILE, LOGLEVEL

from hippools.db.api import get_session
from hippools import db

from hippools.db.utils import pool_to_network

if LOGLEVEL == 'DEBUG':
    LOGLEVEL = logging.DEBUG
else:
    LOGLEVEL = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)

# create console handler with a higher log level
ch = logging.FileHandler(LOGFILE)
formatter = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class IPPool:
    _pool = None
    _db = None
    _lock = None

    @property
    def size(self):
        return self._size(self._db['pool'])

    @property
    def used_size(self):
        ipset = IPSet([])
        for ip_set_hash, pool in self._db['allocated'].items():
            ipset |= pool
        return self._size(ipset)

    @property
    def utilization(self):
        with self._lock:
            self._load_pool_db()
        if self.used_size == 0:
            return 0
        return round(float(self.used_size) / (float(self.size) + float(self.used_size)), 2)

    def _size(self, pool):
        size = 0
        for ip_element in pool.iter_cidrs():
            size += ip_element.size
        return size

    def _load_pool_db(self):
        logger.debug("Try to load pool state from db")
        logger.debug("Pool hash=%s" % self._pool_hash)
        try:
            self._db = load(file(os.path.join(DB_PATH, self._pool_hash), 'r'))
        except IOError:
            self._dump_pool_db()

    def _dump_pool_db(self):
        logger.debug("Try to dump pool state to db")
        logger.debug("Pool hash=%s" % self._pool_hash)
        dump(self._db, file(os.path.join(DB_PATH, self._pool_hash), 'w'))

    def __init__(self, pools_list):
        self._db = {'pool': IPSet(pools_list), 'allocated': {}}
        logger.debug("Inited pool with size=%s ips" % self.size)
        self._pool_hash = md5(str(pools_list)).hexdigest()
        self._lock = FileLock(os.path.join(DB_PATH, self._pool_hash))
        self._load_pool_db()

    def allocate(self, ip_count):
        with self._lock:
            self._load_pool_db()
            logger.info("Allocation started, require=%s" % ip_count)
            for ip_element in reversed(self._db['pool'].iter_cidrs()):
                if ip_count <= ip_element.size:
                    logger.debug("Good ip_element found %s, size: %s, require=%s" % (ip_element, ip_element.size,
                                                                                     ip_count))
                    logger.debug("Allocate ip range size=%s from ip_element %s" % (ip_count, ip_element))
                    allocated_ip_sets = IPSet([ip for ip in ip_element[:ip_count]])
                    allocated_ip_sets_hash = md5(str(allocated_ip_sets)).hexdigest()
                    self._db['pool'] ^= allocated_ip_sets
                    self._db['allocated'][allocated_ip_sets_hash] = allocated_ip_sets
                    self._dump_pool_db()
                    logger.info("[-] Allocated %s" % allocated_ip_sets)
                    return allocated_ip_sets_hash
            raise Exception("Cannot get IpSet size=%s" % ip_count)

    def deallocate(self, ip_sets_hash):
        with self._lock:
            self._load_pool_db()
            ipset = self._get_allocated_ip_pools(ip_sets_hash)
            logger.info("De-allocation started, free=%s" % ipset.size)
            del self._db['allocated'][ip_sets_hash]
            self._db['pool'] |= ipset
            self._dump_pool_db()
            logger.info("[+] De-allocated %s" % ipset)
            return True

    @staticmethod
    def ip_sets_to_ip_range(ip_sets):
        return {'StartIp': unicode(list(ip_sets)[0]), 'EndIp': unicode(list(ip_sets)[-1])}

    @staticmethod
    def ip_range_to_ip_sets(startip, endip):
        return IPSet(IPRange(startip, endip))

    def _get_allocated_ip_pools(self, ip_sets_hash):
        self._load_pool_db()
        if ip_sets_hash in self._db['allocated']:
            return self._db['allocated'][ip_sets_hash]
        else:
            raise Exception("Allocated ip_sets with hash=%s not exist" % ip_sets_hash)

    def get_allocated_ip_pools(self, ip_sets_hash):
        with self._lock:
            return self._get_allocated_ip_pools(ip_sets_hash)


class IPPoolV2():

    def allocate(self, netmask, net_group_name, stack_id=None, stack_name=None):
        context = get_session()
        network = IPNetwork('0.0.0.0/%s' % netmask)
        pool = db.api.free_pool_find_by_netmask_and_netgroup(context, network.netmask.value, net_group_name)
        ip_network = pool_to_network(pool)
        if ip_network.size == network.size:
            pool.is_free = False
            pool.stack_id = stack_id
            pool.stack_name = stack_name
            pool.save()
            allocated_pool = pool
        else:
            pool_list = list(ip_network.subnet(netmask))
            allocated_network = pool_list[0]
            pool_list = IPSet(pool_list[1::])
            print allocated_network
            allocated_pool = db.api.used_pool_add(context, {'initial_pool': pool.initial_pool, 'cidr': allocated_network,
                                                            'stack_id': stack_id, 'stack_name': stack_name})
            for free_pool in pool_list.iter_cidrs():
                db.api.free_pool_add(context, {'initial_pool':  pool.initial_pool, 'cidr': free_pool})
            db.api.pool_delete(context, pool.pool_id)
            logger.info('allocate pool id %s ' % allocated_pool.pool_id)
        return allocated_pool

    def deallocate(self, pool_id):
        context = get_session()
        pool = db.api.used_pool_get(context, pool_id)
        logger.info('deallocate pool %s' % pool.pool_id)
        pool.is_free = True
        pool.save(context)
        db.api.concat_pool(context, pool)


class IPPoolGroup():
    def create_new_pool_group(self, group_name):
        context = get_session()
        group = db.api.pool_group_add(context, {'group_name': group_name})
        return  group

    def get_pool_group(self, group_name):
        context = get_session()
        group = db.api.pool_group_get_by_name(context,  group_name)
        return  group


class IPInitialPool():

    def create_new_initial_pool(self, group_id, ip, mask):
        network = IPNetwork('%s/%s' % (ip, mask))
        context = get_session()
        initial_pool = db.api.initial_pool_add(context, {'group_id': group_id, 'cidr': network})
        return initial_pool


