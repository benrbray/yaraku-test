import pytest;
import requests;
from urllib.parse import urljoin;
import json;
import redis;
import csv;
from enum import Enum;

WEB_URL = "http://web:5000";
ML_URL  = "http://ml:5001";

HTTP_OK = 200;
HTTP_ACCEPTED = 202;

#### TEST FIXTURES #############################################################

## Fixtures --------------------------------------------------------------------

@pytest.fixture
def redis_conn():
	"""
	Return a connection to the redis database.
	"""
	db = redis.Redis(host="redis", port=6379, decode_responses=True);
	return db;

@pytest.fixture
def redis_flush():
	"""
	Return a connection to the redis database after flushing its contents.
	"""
	db = redis.Redis(host="redis", port=6379, decode_responses=True);
	db.flushdb();

	return db;

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
	response = requests.request("GET", WEB_URL)
	assert(response.status_code == HTTP_OK);

## Add / Remove Books ----------------------------------------------------------

def test_add_book_1():
	db = redis_flush;

	# build request
	url = urljoin(WEB_URL, "books");
	headers = { 'Content-Type': 'application/json' }
	payload = {
		"title"  : "Crime and Punishment",
		"author" : "Fyodor Dostoyevsky"
	}

	# validate response
	response = requests.request("POST", url, headers=headers, json=payload)
	assert(response.status_code == HTTP_OK);

def test_add_book_2():
	db = redis_flush;

	# build request
	url = urljoin(WEB_URL, "books");
	headers = { 'Content-Type': 'application/json' }
	payload = {
		"title"  : "Crime and Punishment",
		"author" : "Fyodor Dostoyevsky"
	}

	# validate response
	response = requests.request("POST", url, headers=headers, json=payload)
	print(response.text);
	assert(response.status_code == HTTP_OK);


## Export Book List ------------------------------------------------------------

def test_export_json(redis_flush):
	db = redis_flush;

	url = urljoin(WEB_URL, "books");
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/json; charset=utf-8");

def test_export_csv_1(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(WEB_URL, "books");
	headers = { 'Accept': 'text/csv' }
	payload = {}

	# validate response
	response = requests.request("GET", url, headers=headers, data=payload)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/csv; charset=utf-8");

def test_export_csv_2(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(WEB_URL, "books/csv");

	# validate response
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/csv; charset=utf-8");

def test_export_xml(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(WEB_URL, "books");
	headers = { 'Accept': 'text/xml' }
	payload = {}

	# validate response
	response = requests.request("GET", url, headers=headers, data=payload)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/xml; charset=utf-8");

def test_export_xml_2(redis_flush):
	db = redis_flush;

	# build request
	url = urljoin(WEB_URL, "books/xml");

	# validate response
	response = requests.request("GET", url)
	assert(response.status_code == HTTP_OK);
	assert(response.headers.get('content-type') == "text/xml; charset=utf-8");

