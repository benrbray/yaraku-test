import flask;
from flask import Flask, escape, abort, jsonify, request;

from . import models;
from . import database;
from .database import redis;
import json;

from werkzeug.exceptions import HTTPException;
import os, sys, traceback;

#### HELPER FUNCTIONS ##########################################################

def json_response(data):
	# create http response
	json_str = json.dumps(data, ensure_ascii=False).encode("utf-8");
	response = flask.Response(json_str);
	response.headers["Content-Type"] = "application/json; charset=utf-8";
	return response;

#### APPLICATION FACTORY #######################################################

def create_app(test_config=None):
	# create and configure app
	app = Flask(__name__);

	# load instance config, if it exists, when not testing,
	# otherwise use test_config
	if test_config is None:
		app.config.from_pyfile("config.py", silent=True);
	else:
		app.config.from_mapping(test_config);
	
	# app context
	app.app_context().push();

	# initialize
	models.init();
	
	@app.route("/addbook", methods=["POST"])
	def add_book():
		# parse request json
		data = request.get_json();
		if not data:
			abort(400, "no json data provided");

		book_id = data.get("id");
		book_title = data.get("title");

		# validate request data
		if book_id is None:
			abort(400, "failed to add book (missing required 'id')");
		if book_title is None:
			abort(400, "failed to add book (missing required 'title')");

		# build word index
		models.rec_add_title(book_title, book_id);
		models.group_add_book(book_id);
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

		return json_response(similar_books);
	
	@app.route("/group_ids")
	def get_group_ids():
		"""
		Retrive JSON with grouping information.  Returns a list of groups,
		where each group is a list of <book_id>s.  
		"""
		group_ids = database.get_group_ids();
		return json_response(group_ids);

	@app.route("/group_books")
	def get_group_books():
		"""
		Retrive JSON with grouping information.  Returns a list of groups,
		where each group is a list of book objects.
		"""
		group_books = database.get_group_books();
		return json_response(group_books);

	#### AFTER REQUEST ##################################################

	@app.after_request
	def after_request(response):
		# set Access-Control headers to allow cross-origin access
		# (note: this was a quick fix to get recommendations working
		#    from the web frontend.  This poses security concerns, and
		#    I'm sure there's a better solution for production!)
		# (see https://stackoverflow.com/a/42286498/1444650)
		response.headers.add('Access-Control-Allow-Origin', '*')
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
		response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
		return response


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