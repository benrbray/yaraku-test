import flask;
from flask import Flask, escape, abort, jsonify, request;
import requests;

from . import models;
from .models import redis;
import json;

from werkzeug.exceptions import HTTPException;
import os;

# application factory
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

	# initialize database
	#TODO: init_app?  use flask-redis?
	models.init_redis();

	@app.route("/", methods=["GET"])
	def index():
		return flask.render_template("index.html");

	@app.route("/books", methods=["GET"])
	def get_book_list():
		book_list = models.get_all_books();

		# TODO: encoding?
		return json.dumps(book_list, ensure_ascii=False).encode("utf-8"), 200;

	@app.route("/books/<book_id>", methods=["GET"])
	def get_book(book_id):
		book_data = models.get_book(book_id);

		# handle missing book
		if not book_data:
			abort(f"no book found with id={book_id}", 404);

		# respond with book data
		book_data["id"] = book_id;
		return json.dumps(book_data, ensure_ascii=False).encode("utf-8"), 200;

	@app.route("/books/<book_id>", methods=["DELETE"])
	def delete_book(book_id):
		# attempt to delete book
		success = models.delete_book(book_id);
		# handle failure
		if not success:
			abort(f"failed to delete book with id={book_id}", 500);
		# handle success
		return f"deleted book with id={book_id}", 200;

	@app.route("/books/csv")
	def get_csv():
		# stream db contents to csv
		# (https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/)
		@flask.stream_with_context
		def generate():
			book_list = models.get_all_books();
			for book in book_list:
				book_data = [ book["title"], book["author"] ];
				yield ','.join(book_data) + "\n";
		
		# create http response
		response = flask.Response(generate());
		response.headers["Content-Type"] = "text/csv; charset=utf-8";
		response.headers["Content-Disposition"] = "attachment; filename=result.csv";
		return response;

	@app.route("/books/xml")
	def get_xml():
		#TODO: generate XML (perhaps via ACCEPT http header?)
		return "TODO:  Generate XML"

	@app.route("/books", methods=["POST"])
	def add_book():
		# parse request json
		data = request.get_json();
		bookTitle = data.get("title");
		bookAuthor = data.get("author");

		# validate request data
		if bookTitle is None:
			abort(400, "failed to add book (missing required 'title')");
		if bookAuthor is None:
			abort(400, "failed to add book (missing required 'author')");

		# add to database
		# TODO: handle duplicate books?
		book_id = models.add_book(bookTitle, bookAuthor);

		# send book to ml service
		req = requests.post('http://ml:5000/addbook', json={
			"id" : book_id,
			"title" : bookTitle,
			"author" : bookAuthor
		});

		return json.dumps("added book"), 200

	#### ERRORS #########################################################

	#@app.errorhandler(Exception)
	def json_error(error):
		# preserve status code on HTTP errors
		code = 500;
		if isinstance(error, HTTPException) :
			code = error.code;
		# return error as JSON
		return jsonify(error=str(error)), code;

	return app;