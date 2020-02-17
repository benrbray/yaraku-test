import pytest;
import requests;
from urllib.parse import urljoin;
import json, csv, os;
import redis;
import api_helpers as api;
import ml_helpers as ml;
import random;

# http codes
HTTP_OK = 200;
HTTP_ACCEPTED = 202;
HTTP_BAD_REQUEST = 400;
HTTP_NOT_FOUND = 404;

################################################################################

def test_rec_1(redis_flush):
	# ask for recommendations when no books exist
	response = ml.request_similar_books({
		"title" : "Green Eggs and Ham",
		"author" : "Dr. Seuss"
	})

	assert(response.status_code == HTTP_OK);
	data = response.json();
	assert(data is not None);
	assert(len(data) == 0);

def test_rec_2(redis_flush):
	# make invalid request to /recommend
	url = urljoin(ml.ML_URL, "recommend");
	headers = { 'Content-Type': 'application/json' }
	payload = { "nonsense" : 45993020 }
	response = requests.request("POST", url, headers=headers, json=payload);
	
	# expect 400 bad request
	assert(response.status_code == HTTP_BAD_REQUEST);

def test_rec_3(redis_flush):
	# add a book to an empty database
	title = "Green Eggs and Ham";
	author = "Dr. Seuss";
	response = api.request_add_book(title, author);
	assert(response.status_code == HTTP_OK);

	# get recommendation for title with words in common
	response = ml.request_similar_books({
		"title" : "How to Cook Eggs: A Beginner's Guide",
		"author" : "John Smith"
	});
	assert(response.status_code == HTTP_OK);
	data = response.json();
	assert(data is not None);
	assert(len(data) > 0);
	
	# expect results to contain the book we added
	similar_book = data[0];
	assert("title" in similar_book);
	assert("author" in similar_book);
	assert(similar_book["title"] == title);
	assert(similar_book["author"] == author);

	# get recommendation for title with words in common
	response = ml.request_similar_books({
		"title" : "No Words in Common"
	});
	assert(response.status_code == HTTP_OK);
	data = response.json();
	assert(data is not None);
	# expect no results
	assert(len(data) == 0);