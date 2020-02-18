import requests;
from urllib.parse import urljoin;
import os, csv;

# urls
WEB_URL = "http://web:5000";
ML_URL  = "http://ml:5000";

# http codes
HTTP_OK = 200;
HTTP_ACCEPTED = 202;
HTTP_NOT_FOUND = 404;

################################################################################

def request_similar_books(book_data):
	assert("title" in book_data);
	url = urljoin(ML_URL, "recommend");
	headers = { 'Content-Type': 'application/json' }
	payload = {
		"title"  : book_data["title"]
	}
	return requests.request("POST", url, headers=headers, json=payload);

def request_insert_book(book_data):
	url = urljoin(ML_URL, "addbook");
	headers = { 'Content-Type': 'application/json' }
	return requests.request("POST", url, headers=headers, json=book_data);

def request_group_ids():
	url = urljoin(ML_URL, "group_ids");
	return requests.request("GET", url);

def request_group_books():
	url = urljoin(ML_URL, "group_books");
	return requests.request("GET", url);

