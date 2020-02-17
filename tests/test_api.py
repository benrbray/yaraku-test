import pytest;
import requests;
from urllib.parse import urljoin;
import json;
import redis;
import csv;
import api_helpers as api;

# http codes
HTTP_OK = 200;
HTTP_ACCEPTED = 202;
HTTP_NOT_FOUND = 404;

#### TEST FIXTURES (defined in conftest.py) ####################################

## Test Fixtures ---------------------------------------------------------------

def test_redis_conn(redis_conn):
	db = redis_conn;
	num_keys = db.dbsize();
	assert(num_keys >= 0);

def test_redis_flush(redis_flush):
	db = redis_flush;
	num_keys = db.dbsize();
	assert(num_keys == 0);

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

## Export Book List ------------------------------------------------------------

def test_export_json(redis_flush):
	db = redis_flush;

	url = urljoin(api.WEB_URL, "books");
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "application/json; charset=utf-8");

def test_export_csv_1(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "books");
	headers = { 'Accept': 'text/csv' }
	payload = {}

	# validate response
	response = requests.request("GET", url, headers=headers, data=payload)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/csv; charset=utf-8");

def test_export_csv_2(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "books/csv");

	# validate response
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/csv; charset=utf-8");

def test_export_xml(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "books");
	headers = { 'Accept': 'text/xml' }
	payload = {}

	# validate response
	response = requests.request("GET", url, headers=headers, data=payload)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/xml; charset=utf-8");

def test_export_xml_2(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(api.WEB_URL, "books/xml");

	# validate response
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/xml; charset=utf-8");