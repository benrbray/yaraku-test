import pytest;
import requests;
from urllib.parse import urljoin;
import json, csv, os;
import redis;
import api_helpers as api;
import random;

# http codes
HTTP_OK = 200;
HTTP_ACCEPTED = 202;
HTTP_NOT_FOUND = 404;

#### TEST API ##################################################################

def test_api_1(redis_flush):
	db = redis_flush;

	# test that local server is up and running
	response = requests.request("GET", api.WEB_URL)
	assert(response.status_code == HTTP_OK);

## Add / Remove Books ----------------------------------------------------------

def test_add_book_1(redis_flush):
	# validate response
	response = api.request_add_book("Crime and Punishment", "Fyodor Dostoyevsky");
	assert(response.status_code == HTTP_OK);	
	# expect "id" field after adding book
	data = response.json();
	assert("id" in data);

def test_add_book_2(redis_flush):
	# validate response
	title = "Fyodor Dostoyevsky";
	author = "Crime and Punishment";
	response = api.request_add_book(title, author);
	assert(response.status_code == HTTP_OK);

	# expect "id" field after adding book
	data = response.json();
	assert("id" in data);

	# request book information
	response = api.request_get_book(data["id"]);
	assert(response.status_code == HTTP_OK);
	book_info = response.json();
	assert("title" in book_info);
	assert("author" in book_info);
	assert("id" in book_info);
	assert(book_info["title"] == title);
	assert(book_info["author"] == author);
	assert(book_info["id"] == data["id"]);

def test_delete_book_1(redis_flush):
	# attempt to add book
	title = "Fyodor Dostoyevsky";
	author = "Crime and Punishment";
	response = api.request_add_book(title, author);
	assert(response.status_code == HTTP_OK);

	# expect "id" field after adding book
	data = response.json();
	assert("id" in data);

	# request book information
	response = api.request_get_book(data["id"]);
	assert(response.status_code == HTTP_OK);

	# attempt to delete book
	response = api.request_delete_book(data["id"]);
	assert(response.status_code == HTTP_OK);

	response = api.request_get_book(data["id"]);
	assert(response.status_code == HTTP_NOT_FOUND);


def test_delete_book_2(redis_flush):
	# attempt to delete book that doesn't exist
	response = api.request_delete_book("9999");
	assert(response.status_code == HTTP_NOT_FOUND);

def test_crud(redis_flush):
	# upload book list using web api, keeping track of generated ids
	books_csv = api.upload_books_csv("data/books.csv");
	num_books = len(books_csv);
	
	# randomly delete a large number of books
	delete_count = random.randrange(num_books // 4, num_books // 2);
	delete_idxs = random.sample(range(num_books), delete_count);
	delete_ids  = { books_csv[idx]["id"] for idx in delete_idxs };

	for delete_id in delete_ids:
		response = api.request_delete_book(delete_id);
		assert(response.status_code == HTTP_OK);

	# check that deleted books are actually gone,
	# and that the other books are still there
	for book in books_csv:
		book_id = book["id"];
		response = api.request_get_book(book_id);

		if book_id in delete_ids:
			assert(response.status_code == HTTP_NOT_FOUND);
		else:
			assert(response.status_code == HTTP_OK);
			data = response.json();
			assert("author" in data);
			assert("title" in data);
			assert(data["author"] == book["author"]);
			assert(data["title"] == book["title"]);
			assert(data["id"] == book_id);

## Export Book List ------------------------------------------------------------

def test_export_json(redis_flush):
	db = redis_flush;

	url = urljoin(api.WEB_URL, "api/books");
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "application/json; charset=utf-8");

def test_export_csv_1(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/books");
	headers = { 'Accept': 'text/csv' }
	payload = {}

	# validate response
	response = requests.request("GET", url, headers=headers, data=payload)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/csv; charset=utf-8");

def test_export_csv_2(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/books/csv");

	# validate response
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/csv; charset=utf-8");

def test_export_xml(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/books");
	headers = { 'Accept': 'text/xml' }
	payload = {}

	# validate response
	response = requests.request("GET", url, headers=headers, data=payload)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/xml; charset=utf-8");

def test_export_xml_2(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/books/xml");

	# validate response
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/xml; charset=utf-8");

## Export Titles ---------------------------------------------------------------

def test_export_title_csv_1(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/titles");
	headers = { 'Accept': 'text/csv' }
	payload = {}

	# validate response
	response = requests.request("GET", url, headers=headers, data=payload)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/csv; charset=utf-8");

def test_export_title_csv_2(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/titles/csv");

	# validate response
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/csv; charset=utf-8");

def test_export_title_xml(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/titles");
	headers = { 'Accept': 'text/xml' }
	payload = {}

	# validate response
	response = requests.request("GET", url, headers=headers, data=payload)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/xml; charset=utf-8");

def test_export_title_xml_2(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/titles/xml");

	# validate response
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/xml; charset=utf-8");

## Export Authors ---------------------------------------------------------------

def test_export_author_csv_1(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/authors");
	headers = { 'Accept': 'text/csv' }
	payload = {}

	# validate response
	response = requests.request("GET", url, headers=headers, data=payload)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/csv; charset=utf-8");

def test_export_author_csv_2(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/authors/csv");

	# validate response
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/csv; charset=utf-8");

def test_export_author_xml(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/authors");
	headers = { 'Accept': 'text/xml' }
	payload = {}

	# validate response
	response = requests.request("GET", url, headers=headers, data=payload)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/xml; charset=utf-8");

def test_export_author_xml_2(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "api/authors/xml");

	# validate response
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/xml; charset=utf-8");
