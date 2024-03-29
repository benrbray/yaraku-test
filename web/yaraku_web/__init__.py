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
from . import database;
from .database import redis;

#### HELPER FUNCTIONS ##########################################################

def json_response(data):
	# create http response
	json_str = json.dumps(data, ensure_ascii=False).encode("utf-8");
	response = flask.Response(json_str);
	response.headers["Content-Type"] = "application/json; charset=utf-8";
	return response;

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
	
	## Web Interface -----------------------------------------------------------

	@app.route("/", methods=["GET"])
	@app.route("/web", methods=["GET"])
	def index():
		return flask.render_template("index.html");

	@app.route("/web/books/<book_id>", methods=["GET"])
	def web_book(book_id):
		# get book data
		book_data = database.get_book(book_id);
		book_data["id"] = book_id;
		# if book not found, reply with 404
		if not book_data:
			abort(404, f"no book found with id={book_id}");
		# otherwise, show page with book info
		return flask.render_template("book.html", book_data=book_data);

	@app.route("/web/groups", methods=["GET"])
	def web_groups():
		# get group data
		group_books = database.get_group_books();
		# respond
		return flask.render_template("groups.html", group_books=group_books);

	## Export Books ------------------------------------------------------------
	
	@app.route("/api/books", methods=["GET"])
	@accept_fallback
	def get_book_list():
		book_list = database.get_all_books();
		return json_response(book_list);

	@app.route("/api/books/csv")
	@get_book_list.support("text/csv")
	def get_books_csv():
		# stream db contents to csv
		# (https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/)
		@flask.stream_with_context
		def generate():
			#TODO: improve streaming with pagination
			book_list = database.get_all_books();
			for book in book_list:
				book_data = [ book["title"], book["author"] ];
				yield ','.join(book_data) + "\n";
		
		# create http response
		response = flask.Response(generate());
		response.headers["Content-Type"] = "text/csv; charset=utf-8";
		response.headers["Content-Disposition"] = "attachment; filename=result.csv";
		return response;

	@app.route("/api/books/xml")
	@get_book_list.support("text/xml")
	def get_books_xml():
		# get book list
		book_list = database.get_all_books();

		# generate xml
		root = XML.Element("root");
		for book in book_list:
			book_elt = XML.SubElement(root, "book", id=book["id"]);
			XML.SubElement(book_elt, "title").text  = book["title"];
			XML.SubElement(book_elt, "author").text = book["author"];
		
		xml_str = XML.tostring(root, encoding="utf8");

		# create http response
		response = flask.Response(xml_str);
		response.headers["Content-Type"] = "text/xml; charset=utf-8";
		response.headers["Content-Disposition"] = "attachment; filename=result.xml";
		return response;

	## Export Titles -----------------------------------------------------------

	@app.route("/api/titles", methods=["GET"])
	@accept_fallback
	def get_titles():
		book_list = database.get_all_books();
		title_list = [ { "title" : book["title"] } for book in book_list ];
		return json_response(title_list);

	@app.route("/api/titles/csv", methods=["GET"])
	@get_titles.support("text/csv")
	def get_titles_csv():
		# stream db contents to csv
		# (https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/)
		@flask.stream_with_context
		def generate():
			#TODO: improve streaming with pagination
			book_list = database.get_all_books();
			for book in book_list:
				book_data = [ book["title"] ];
				yield ','.join(book_data) + "\n";
		
		# create http response
		response = flask.Response(generate());
		response.headers["Content-Type"] = "text/csv; charset=utf-8";
		response.headers["Content-Disposition"] = "attachment; filename=titles.csv";
		return response;

	@app.route("/api/titles/xml", methods=["GET"])
	@get_titles.support("text/xml")
	def get_titles_xml():
		# get book list
		book_list = database.get_all_books();

		# generate xml
		root = XML.Element("root");
		for book in book_list:
			book_elt = XML.SubElement(root, "book", id=book["id"]);
			XML.SubElement(book_elt, "title").text  = book["title"];
		
		xml_str = XML.tostring(root, encoding="utf8");

		# create http response
		response = flask.Response(xml_str);
		response.headers["Content-Type"] = "text/xml; charset=utf-8";
		response.headers["Content-Disposition"] = "attachment; filename=titles.xml";
		return response;

	

	## Export Authors -----------------------------------------------------------

	@app.route("/api/authors", methods=["GET"])
	@accept_fallback
	def get_authors():
		author_list = database.get_authors();
		return json_response(author_list);

	@app.route("/api/authors/csv", methods=["GET"])
	@get_authors.support("text/csv")
	def get_authors_csv():
		# stream db contents to csv
		# (https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/)
		@flask.stream_with_context
		def generate():
			#TODO: improve streaming with pagination
			author_list = database.get_authors();
			for author in author_list:
				yield author + "\n";
		
		# create http response
		response = flask.Response(generate());
		response.headers["Content-Type"] = "text/csv; charset=utf-8";
		response.headers["Content-Disposition"] = "attachment; filename=authors.csv";
		return response;

	@app.route("/api/authors/xml", methods=["GET"])
	@get_authors.support("text/xml")
	def get_authors_xml():
		# get book list
		author_list = database.get_authors();

		# generate xml
		root = XML.Element("root");
		for author in author_list:
			author_elt = XML.SubElement(root, "author");
			XML.SubElement(author_elt, "name").text  = author;
		
		xml_str = XML.tostring(root, encoding="utf8");

		# create http response
		response = flask.Response(xml_str);
		response.headers["Content-Type"] = "text/xml; charset=utf-8";
		response.headers["Content-Disposition"] = "attachment; filename=authors.xml";
		return response;

	## CRUD Operations ---------------------------------------------------------

	@app.route("/api/books/<book_id>", methods=["GET"])
	def get_book(book_id):
		# search for book_id in database
		book_data = database.get_book(book_id);

		# if book not found, reply with 404
		if not book_data:
			abort(404, f"no book found with id={book_id}");

		# otherwise, reply with book json
		book_data["id"] = book_id;
		return json_response(book_data);

	@app.route("/api/books/<book_id>", methods=["DELETE"])
	def delete_book(book_id):
		# attempt to delete book
		delete_count = database.delete_book(book_id);
		# handle failure
		if delete_count < 1:
			abort(404, f"failed to delete; no book exists with id={book_id}");
		# handle success
		return f"deleted book with id={book_id}", 200;

	@app.route("/api/books", methods=["POST"])
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
		book_id = database.add_book(bookTitle, bookAuthor);

		# send book to ml service
		req = requests.post('http://ml:5000/addbook', json={
			"id" : book_id,
			"title" : bookTitle,
			"author" : bookAuthor
		});

		# reply with book_id for newly created book
		response = json_response({
			"id" : book_id
		});
		response.headers["Content-Disposition"] = "attachment; filename=result.xml";
		return response;

	#### ERRORS ################################################################

	@app.errorhandler(Exception)
	def json_error(error):
		# preserve status code on HTTP errors
		code = 500;
		if isinstance(error, HTTPException) :
			code = error.code;
		# return error as JSON
		return jsonify(error=str(error)), code;

	return app;