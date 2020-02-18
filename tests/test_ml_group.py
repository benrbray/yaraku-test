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

def test_group_ids_1(redis_flush):
	# ask for group ids when no books exist
	response = ml.request_group_ids();
	assert(response.status_code == HTTP_OK);
	data = response.json();
	assert(data is not None);
	assert(len(data) == 0);
	
def test_group_books_1(redis_flush):
	# ask for groupings when no books exist
	response = ml.request_group_books();
	assert(response.status_code == HTTP_OK);
	data = response.json();
	assert(data is not None);
	assert(len(data) == 0);


def test_rec_3(redis_flush):
	# add a book to an empty database
	title = "Green Eggs and Ham";
	author = "Dr. Seuss";
	response = api.request_add_book(title, author);
	assert(response.status_code == HTTP_OK);

	# ask for group_ids (no guarantee ml has processed groups yet)
	response = ml.request_group_ids();
	assert(response.status_code == HTTP_OK);
	data = response.json();
	assert(data is not None);

	# ask for group_books (no guarantee ml will processed groups yet)
	response = ml.request_group_books();
	assert(response.status_code == HTTP_OK);
	data = response.json();
	assert(data is not None);