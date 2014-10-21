import os
from flask import send_from_directory, render_template, jsonify
from app import app
from charts import chart_index, chart_utilisation, chart_fragmentation, collect_chart_fragmentation_data
from config_parser import ALL_IP_POOLS

@app.route("/chart_index.png")
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


@app.route("/fragmentation_data/<string:pool_name>")
def fragmentation_data(pool_name):
    return  jsonify(collect_chart_fragmentation_data(pool_name))


@app.route("/")
@app.route("/index.html")
def main_view():
    return render_template('index.html', ALL_IP_POOLS=ALL_IP_POOLS)

