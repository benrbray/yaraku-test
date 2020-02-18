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

#### REQUEST FUNCTIONS #########################################################

def request_add_book(title, author):
	url = urljoin(WEB_URL, "api/books");
	headers = { 'Content-Type': 'application/json' }
	payload = {
		"title"  : title,
		"author" : author
	}
	return requests.request("POST", url, headers=headers, json=payload);

def request_get_book(book_id):
	url = urljoin(WEB_URL, f"api/books/{book_id}");
	return requests.request("GET", url);

def request_delete_book(book_id):
	url = urljoin(WEB_URL, f"api/books/{book_id}");
	return requests.request("DELETE", url);

#### TESTING WITH MANY BOOKS ###################################################

def upload_books_csv(file_path):
	# read book list from disk
	books_csv = [];
	with open(os.path.join("data","books.csv")) as csvfile:
		for row in csv.reader(csvfile, skipinitialspace=True):
			books_csv.append({
				"title": row[0],
				"author": row[1]
			});
	num_books = len(books_csv);
	assert(num_books == 60);
	
	# use web api to upload all books individually,
	# keeping track of their reported ids
	for book in books_csv:
		response = request_add_book(book["title"], book["author"]);
		assert(response.status_code == HTTP_OK);
		data = response.json();
		assert("id" in data);
		book["id"] = data["id"];

	return books_csv;