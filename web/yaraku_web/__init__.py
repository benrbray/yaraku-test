import flask;
import flask_sqlalchemy;
from flask import Flask, escape, abort, jsonify, request;

from . import models;
from .models import db;
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
		DATABASE=os.path.join(app.instance_path, 'yaraku_web.sqlite')
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
	db.init_app(app);
	db.create_all();

	@app.route("/", methods=["GET"])
	def index():
		book_list = [];
		books = models.Book.query.all();
		for book in books:
			book_list.append({
				"id" : book.id,
				"title" : book.title,
				"author" : book.author
			});

		return flask.render_template("index.html");

	@app.route("/books", methods=["GET"])
	def get_book_list():
		books = models.Book.query.all();
		book_list = [];
		for book in books:
			book_list.append({
				"id" : book.id,
				"title" : book.title,
				"author" : book.author
			});

		# TODO: encoding?
		return json.dumps(book_list, ensure_ascii=False).encode("utf-8"), 200;

	@app.route("/books/<bookId>", methods=["GET"])
	def get_book(bookId):
		# query
		bookQuery = models.Book.query.filter_by(id=bookId).first();

		# handle book not found
		if bookQuery is None:
			abort(f"no book found with id={bookId}", 404);

		book = {
			"id" : bookQuery.id,
			"title" : bookQuery.title,
			"author" : bookQuery.author
		}
		return json.dumps(book, ensure_ascii=False).encode("utf-8"), 200;

	@app.route("/books/<bookId>", methods=["DELETE"])
	def delete_book(bookId):
		# delete book from database
		query = models.Book.query.filter_by(id=bookId).delete();
		db.session.commit();

		# send response
		response = {
			"message" : f"deleted book (id={bookId})"
		}
		return json.dumps(response, ensure_ascii=False).encode("utf-8"), 200;

	@app.route("/books/csv")
	def get_csv():
		# stream db contents to csv
		# (https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/)
		@flask.stream_with_context
		def generate():
			books = models.Book.query.all();
			for book in books:
				book_data = [ book.title, book.author ];
				yield ','.join(book_data) + "\n";
		
		# create http response
		response = flask.Response(generate());
		response.headers["Content-Type"] = "text/csv; charset=utf-8";
		response.headers["Content-Disposition"] = "attachment; filename=result.csv";
		return response;

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
		book = models.Book(title=bookTitle, author=bookAuthor);
		db.session.add(book);
		db.session.commit();
		return json.dumps("added book"), 200

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