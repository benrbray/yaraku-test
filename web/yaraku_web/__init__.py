# flask
import flask;
from flask import Flask, escape, abort, jsonify, request;
from flask_accept import accept, accept_fallback;
from werkzeug.exceptions import HTTPException;

# networking
import requests;

# system and file types
from xml.etree import ElementTree as XML;
import json;
import os;

# yaraku app source
from . import models;
from .models import redis;

#### HELPER FUNCTIONS ##########################################################

def json_utf8(obj):
	return json.dumps(obj, ensure_ascii=False).encode("utf-8");

################################################################################

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

	## Web Interface -----------------------------------------------------------

	@app.route("/", methods=["GET"])
	def index():
		return flask.render_template("index.html");

	## API ---------------------------------------------------------------------

	@app.route("/books", methods=["GET"])
	@accept_fallback
	def get_book_list():
		book_list = models.get_all_books();

		# create http response
		response = flask.Response(json_utf8(book_list));
		response.headers["Content-Type"] = "application/json; charset=utf-8";
		return response;

	@app.route("/books/csv")
	@get_book_list.support("text/csv")
	def get_books_csv():
		# stream db contents to csv
		# (https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/)
		@flask.stream_with_context
		def generate():
			#TODO: improve streaming with pagination
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
	@get_book_list.support("text/xml")
	def get_books_xml():
		# get book list
		book_list = models.get_all_books();

		# generate xml
		root = XML.Element("root");
		for book in book_list:
			book_elt = XML.SubElement(root, "book", id=book["id"]);
			XML.SubElement(book_elt, "title").text  = book["title"];
			XML.SubElement(book_elt, "author").text = book["author"];
		
		#tree = XML.ElementTree(root);
		xml_str = XML.tostring(root, encoding="utf8");

		# create http response
		response = flask.Response(xml_str);
		response.headers["Content-Type"] = "text/xml; charset=utf-8";
		response.headers["Content-Disposition"] = "attachment; filename=result.xml";
		return response;

	@app.route("/books/<book_id>", methods=["GET"])
	def get_book(book_id):
		# search for book_id in database
		book_data = models.get_book(book_id);

		# if book not found, reply with 404
		if not book_data:
			abort(f"no book found with id={book_id}", 404);

		# otherwise, reply with book json
		book_data["id"] = book_id;
		return json_utf8(book_data), 200;

	@app.route("/books/<book_id>", methods=["DELETE"])
	def delete_book(book_id):
		# attempt to delete book
		success = models.delete_book(book_id);
		# handle failure
		if not success:
			abort(f"failed to delete book with id={book_id}", 500);
		# handle success
		return f"deleted book with id={book_id}", 200;

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

		# reply with book_id for newly created book
		response = flask.Response(json_utf8({
			"id" : book_id
		}));
		response.headers["Content-Type"] = "application/json; charset=utf-8";
		response.headers["Content-Disposition"] = "attachment; filename=result.xml";
		return response;

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