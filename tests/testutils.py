from flask import Flask
from flask.ext.restful import Api
from flask.ext.testing import TestCase

from hippools.app import app
from hippools.db.sqlalchemy import models
from hippools.db.sqlalchemy import session
from hippools.ip_pool import IPPoolGroup, IPInitialPool, IPPoolV2

from exam.decorators import fixture
from exam.cases import Exam
from hippools.resources import MyPool, PoolUsed, PoolFree, IPPoolUtilization, SQLPool, InitialPool, PoolGroup


class PoolTestCase(Exam, TestCase):
    session.SQL_CONNECTION = 'mysql://root@localhost/test_hippools'
    TESTING = True

    def create_app(self):
        app = Flask(__name__)
        app.debug = True
        api = Api(app)

        # API v1
        api.add_resource(MyPool, '/api/v1/pools/<string:pool_name>')
        api.add_resource(PoolUsed, '/api/v1/pools/<string:pool_name>/used')
        api.add_resource(PoolFree, '/api/v1/pools/<string:pool_name>/free')
        api.add_resource(IPPoolUtilization, '/api/v1/pools/<string:pool_name>/utilization')

        # API v2
        api.add_resource(SQLPool, '/api/v2/pools/<string:pool_name>')
        api.add_resource(PoolGroup, '/api/v2/pools/poolgroup')
        api.add_resource(InitialPool, '/api/v2/pools/<string:pool_name>')

        return app

    def setUp(self):
        models.create_all()

    def tearDown(self):
        models.drop_all()

    @fixture
    def pool_group(self):
        return self.create_pool_group(pool_group_name='test_group_name')

    def create_pool_group(self, pool_group_name):
        pool_group = IPPoolGroup()
        return pool_group.create_new_pool_group(pool_group_name)

    @fixture
    def initial_pool(self):
        return self.create_initial_pool(ip='192.168.1.1', mask='255.255.0.0')

    def create_initial_pool(self, ip, mask):
        initial_pool = IPInitialPool()
        return initial_pool.create_new_initial_pool(self.pool_group.group_id, ip, mask)

    @fixture
    def allocated_pool(self):
        netmask = 30
        net_group_name = self.pool_group.group_name
        initial_pool = self.initial_pool
        stack_id = 'FFFFFFFF-bf15-4c80-8910-a5119b2e558d'
        stack_name = 'test name'
        return self.create_allocated_pool(netmask, net_group_name, stack_id, stack_name)

    def create_allocated_pool(self, netmask, net_group_name, stack_id, stack_name):
        ip_pool_v2 = IPPoolV2()
        return ip_pool_v2.allocate(netmask, net_group_name, stack_id, stack_name)


