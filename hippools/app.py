#!/env/python
from flask import Flask
from flask.ext.restful import Api
from resources import IPPoolUtilization, PoolUsed, MyPool, PoolFree


app = Flask(__name__)
api = Api(app)

# API v1
api.add_resource(MyPool, '/api/v1/pools/<string:pool_name>')
api.add_resource(PoolUsed, '/api/v1/pools/<string:pool_name>/used')
api.add_resource(PoolFree, '/api/v1/pools/<string:pool_name>/free')
api.add_resource(IPPoolUtilization, '/api/v1/pools/<string:pool_name>/utilization')
