#!/env/python
# from pycharm_debug import pydevd
import os
from flask import Flask, send_from_directory
from flask.ext.restful import Api
from resources import IPPoolUtilization, PoolUsed, MyPool, PoolFree
from charts import chart_index, chart_utilisation, chart_fragmentation


app = Flask(__name__)
api = Api(app)

# API v1
api.add_resource(MyPool, '/api/v1/pools/<string:pool_name>')
api.add_resource(PoolUsed, '/api/v1/pools/<string:pool_name>/used')
api.add_resource(PoolFree, '/api/v1/pools/<string:pool_name>/free')
api.add_resource(IPPoolUtilization, '/api/v1/pools/<string:pool_name>/utilization')


@app.route("/")
def index():
    return chart_index()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'favicon.png', mimetype='image/png')


@app.route("/<string:pool_name>")
def utilization(pool_name):
    return chart_utilisation(pool_name)


@app.route("/fragmentation/<string:pool_name>")
def fragmentation(pool_name):
    return chart_fragmentation(pool_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
