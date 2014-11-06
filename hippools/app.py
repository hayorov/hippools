#!/env/python
import logging
from flask import Flask
from flask.ext.restful import Api
import config_parser
from resources import IPPoolUtilization, PoolUsed, MyPool, PoolFree, SQLPool, PoolGroup, InitialPool


app = Flask(__name__)
# app.debug = True
api = Api(app)


if config_parser.LOGLEVEL == 'DEBUG':
    LOGLEVEL = logging.DEBUG
else:
    LOGLEVEL = logging.INFO

logger = logging.getLogger('hippools')
logger.setLevel(LOGLEVEL)

# create console handler with a higher log level
ch = logging.FileHandler(config_parser.LOGFILE)
formatter = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
app.logger.addHandler(ch)
logger.info('load complete')

# API v1
api.add_resource(MyPool, '/api/v1/pools/<string:pool_name>')
api.add_resource(PoolUsed, '/api/v1/pools/<string:pool_name>/used')
api.add_resource(PoolFree, '/api/v1/pools/<string:pool_name>/free')
api.add_resource(IPPoolUtilization, '/api/v1/pools/<string:pool_name>/utilization')

# API v2
api.add_resource(SQLPool, '/api/v2/pools/<string:pool_name>')
api.add_resource(PoolGroup, '/api/v2/pools/poolgroup')
api.add_resource(InitialPool, '/api/v2/pools/<string:pool_name>')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
