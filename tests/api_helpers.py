import requests;
from urllib.parse import urljoin;

# urls
WEB_URL = "http://web:5000";
ML_URL  = "http://ml:5001";

# http codes
HTTP_OK = 200;
HTTP_ACCEPTED = 202;
HTTP_NOT_FOUND = 404;

#### REQUEST FUNCTIONS #########################################################

def request_add_book(title, author):
	url = urljoin(WEB_URL, "books");
	headers = { 'Content-Type': 'application/json' }
	payload = {
		"title"  : title,
		"author" : author
	}
	return requests.request("POST", url, headers=headers, json=payload);

def request_get_book(book_id):
	url = urljoin(WEB_URL, f"books/{book_id}");
	return requests.request("GET", url);

def request_delete_book(book_id):
	url = urljoin(WEB_URL, f"books/{book_id}");
	return requests.request("DELETE", url);