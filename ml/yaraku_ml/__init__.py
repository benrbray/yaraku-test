import flask;
from flask import Flask, escape, abort, jsonify, request;

from . import models;
from .models import redis;
import json;

from werkzeug.exceptions import HTTPException;
import os, sys, traceback;

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
		return "Hello, ML!", 200;
	
	@app.route("/addbook", methods=["POST"])
	def add_book():
		print("ml :: addbook");
		# parse request json
		data = request.get_json();
		if not data:
			abort(400, "no json data provided");
		
		print(data);

		book_id = data.get("id");
		book_title = data.get("title");

		print(book_id, book_title);

		# validate request data
		if book_id is None:
			abort(400, "failed to add book (missing required 'id')");
		if book_title is None:
			abort(400, "failed to add book (missing required 'title')");

		# build word index
		models.rec_add_title(book_title, book_id);

		print("ml :: done");
		return "added book", 200;

	@app.route("/recommend", methods=["POST"])
	def recommend():
		# parse and validate request json
		data = request.get_json();
		if not data:
			abort(400, "no json data provided");
		
		# validate: book title
		book_title = data.get("title");
		if not book_title:
			abort(400, "cannot make recommendation (missing required 'title')");
		
		# validate: count (default=5)
		count = data.get("count") or 5;

		# get recommendation
		book = {
			"title" : book_title
		}
		similar_books = models.rec_recommend(book, count);

		return json.dumps(similar_books, ensure_ascii=False).encode("utf-8"), 200;


	#### ERRORS #########################################################

	@app.errorhandler(Exception)
	def json_error(error):
		# preserve status code on HTTP errors
		code = 500;
		if isinstance(error, HTTPException) :
			code = error.code;

		print(error);
		traceback.print_last();
		print(sys.exc_info());

		# return error as JSON
		return jsonify(error=str(error)), code;

	return app;