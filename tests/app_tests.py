from flask.ext.testing import TestCase
from fixture import SQLAlchemyFixture
from netaddr import IPNetwork
from hippools.app import app
from hippools.db.api import get_session
from hippools.db.sqlalchemy import models
from hippools.db.sqlalchemy import session
from hippools import db


class MyTest(TestCase):

    session.SQL_CONNECTION = 'mysql://root:1q2w3e@localhost/test_hippools'
    TESTING = True

    def create_app(self):
        # pass in test configuration
        return app

    def setUp(self):
        models.create_all()

    def tearDown(self):
        models.drop_all()

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


