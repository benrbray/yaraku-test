import flask;
from flask import Flask, escape, abort, jsonify, request;

from . import models;
from .models import redis;
import json;

from werkzeug.exceptions import HTTPException;
import os;

# application factory
def create_app(test_config=None):
	# create and configure app
	app = Flask(__name__);
	#TODO: secret key should be random (set in config.py)
	app.config.from_mapping(
		SECRET_KEY="dev",
		DATABASE=os.path.join(app.instance_path, 'yaraku_ml.sqlite')
	)

	# load instance config, if it exists, when not testing,
	# otherwise use test_config
	if test_config is None:
		app.config.from_pyfile("config.py", silent=True);
	else:
		app.config.from_mapping(test_config);
	
	# app context
	app.app_context().push();

	# initialize database
	#dbdb.init_app(app);
	#db.create_all();
	models.init_redis();

	@app.route("/", methods=["GET"])
	def index():
		return "Hello, ML!";

	#### ERRORS #########################################################

	@app.errorhandler(Exception)
	def json_error(error):
		# preserve status code on HTTP errors
		code = 500;
		if isinstance(error, HTTPException) :
			code = error.code;
		# return error as JSON
		return jsonify(error=str(error)), code;

	return app;