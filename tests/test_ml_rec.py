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