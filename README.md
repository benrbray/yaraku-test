# Yaraku Code Test

Benjamin Bray (benrbray@gmail.com)

*18 February 2020*

## Overview

This project implements a simple web service that allows the user to upload book titles and ask for book recommendations and groupings based on the uploaded catalog of books.

### Setup (Makefile)

The project is designed to run on `localhost` as a web application.  The web interface runs on `localhost:5000` and the standalone machine learning service runs on `localhost:5001`. 

This application should work on both Linux/macOS, although I was only able to test on a machine running `Ubuntu 18.04`.  The application is containerized with `Docker` and assembled with `Docker Compose`, which must both be installed on the host system.  Since the project uses `Docker` to install its dependencies, internet access is assumed when building. 

For convenience, I have included a `Makefile` to start, stop, and test the application.

```
make start         # start the application
make stop          # stop the application
make build         # re-build docker images and start application
make test          # run test suite
make upload_books  # upload a .csv file containing 60 books
```

Docker has a habit of leaving behind images and containers, so I included a `Makefile` with a basic cleanup command.  (*Caution:* Depending on your Docker installation, this may influence your Docker images beyond just this project!)

````
make cleanup
````

### Setup (Manually)

To start the application (in detached mode), navigate to the top-level project folder and run:

````
docker-compose up -d
````

Include the optional `--build` flag to re-build if the source changes.  To stop the application:

````
docker-compose down
````

### Testing

The `tests` folder contains a suite of tests intended to test the basic functionality of each container, as well as interaction between containers.  

* I chose the `pytest`  testing framework.
* For simplicity, tests are packaged in a third docker container which is part of the same network as the application containers.  
* For convenience, the testing container is set to run indefinitely when the application starts. 

You may run the tests at any time by running:

```
docker exec yaraku_tests_1 pytest
```

Alternatively, you can drop into a shell and run the tests manually:

```
docker exec -it yaraku_tests_1 bash
>>> pytest
```

### Logs

To view logs for individual containers:

```
docker logs yaraku_web_1
docker logs yaraku_ml_1
docker logs yaraku_worker_1
docker logs yaraku_tests_1
```

### Project Dependencies

Only Docker and `docker-compose` are needed to run the application.  When the project is run for the first time, Docker will build a set of docker images that include all of the application's dependencies.

I chose the following tools to implement the project:

* `Docker` and `docker-compose` for containerization and distribution.
* `flask` with `python3` for the web API, deployed with `gunicorn`.
* `redis` as a database and message broker, with the `rq` job queue for scheduling background workers.
* `nltk` for basic text processing (tokenization, stemming, stopword removal).
* `gensim` for precomputed word2vec embedings.

This combination has the following advantages:

* **Modularity:** Each service is maintained independently, making it easy to modify code, add features, and swap out services as needed.  Additionally, it is only necessary to re-deploy components which have been changed.
* **Scalability:** Containers can be duplicated as needed to scale up to demand in real-time.
* **Simplicity:** Each of the components listed above is fairly lightweight, with enough features to handle the use cases outlined in the project spec.  If needed, we could swap in more feature-rich tools without much extra effort (for instance, `django` instead of `flask`, `celery` instead of `rq`)

### Components

The application is divided into four Docker containers.

* `web` Contains a Flask application responsible for handling all requests to the books API and web front-end.
* `ml` Contains a Flask application responsible for handling requests to the machine learning service (which includes book recommendations and groupings).  Delegates the model training / computations to a background `worker` .
* `worker` runs in the background, and runs a K-means algorithm on word2vec embeddings of book titles in order to generate groupings.
* `tests` contains basic tests of application functionality.

## `ml` Data API

The `ml` service (running on `localhost:5001`) exposes a REST API for book recommendations and grouping.  All request data data should be encoded as `application/json`.

#### `POST /addbook`

Inform the `ml` service that a new book has been added to the database.  Used to update the recommendation word index, and to help the `ml` service decide when to update groupings.  Expects `application/json` data with the `title` and `id` fields present.  For example,

```
curl --location --request POST 'localhost:5001/addbook' \
--header 'Content-Type: application/json' \
--data-raw '{
	"id" : 0,
	"title" : "Green Eggs and Ham"
}'
```

Acknowledges the request with `200 OK`, or responds with an error.

### Recommendations

Given a title as input, the recommendation service recommends books which share at least one word in common.

* Titles are ranked by the number of shared words.  
* To compute a recommendation, the `ml` service maintains a table mapping each word seen so far to a list of titles which contain that word.
* As a preprocessing step, titles are converted to lower case, tokenized, and stemmed using `nltk`.  This step increases the likelihood that titles will overlap (for example, "gamer" and "game" map to the same entry in the word index).

#### `POST /recommend`

Request book recommendations based on a book title.  Expects `application/json` data with the `title` field present.  The title does not need to exist in the database.  For example,

```
curl --location --request POST 'localhost:5001/recommend' \
--header 'Content-Type: application/json' \
--data-raw '{
	"title" : "Green Eggs and Ham"
}'
```

Optionally, you may include a `count` field indicating the maximum number of recommendations to return.  By default, `count=5`.

```
curl --location --request POST 'localhost:5001/recommend' \
--header 'Content-Type: application/json' \
--data-raw '{
	"title" : "Green Eggs and Ham",
	"count" : 100
}'
```

### Grouping

The machine learning service automatically divides uploaded books into groups.  Groups are re-computed after every `N` additions to the database.  (by default, `N=5`).  Groups are computed by a background worker, using K-means on pre-trained word vectors loaded from `gensim`.  By default, there are `K=5` clusters. 

#### `GET /group_ids`

Query the ML service for groupings of books.  The `application/json` response contains a list of groups, where each group is a list of `<book_id>`s.

```
curl --location --request GET 'localhost:5001/group_ids'
```

#### `GET /group_books`

Query the ML service for groupings of books.  The `application/json` response contains a list of groups, where each group is a list of book objects (with author, title, and id fields)

```
curl --location --request GET 'localhost:5001/group_books'
```

## `web` Books API

The `web` service (running on `localhost:5000`) exposes a REST API for adding, reading, and deleting books.  All request data data should be encoded as `application/json`.  Typically, the API endpoints send and receive book objects, which have the following form:

```json
{
    "title" : "This is the Book's Title: With a Subtitle",
    "author" : "First M. Last"
    "id" : "<book_id>"
}
```

The title and author can be any valid utf-8 strings.  The `author` and `id` fields can be omitted in most situations, except when uploading a new book.

#### `GET /api/books`

Returns a list of all saved books.  Defaults to an `application/json` response.

```
curl --location --request GET 'localhost:5000/api/books'
```

Also supports `text/csv` and `text/xml` responses when an `Accept` header is present.

```
curl --location --request GET 'localhost:5000/api/books' \
--header 'Accept: text/csv'
```

```
curl --location --request GET 'localhost:5000/api/books' \
--header 'Accept: text/xml'
```

#### `GET /api/titles`

Similar to `GET /api/books`, but returns a list of titles instead.  

* Supports CSV and XML through Accept headers
* Additionally, supports `GET /api/titles/csv` and `GET /api/titles/xml`

#### `GET /api/authors`

Similar to `GET /api/books`, but returns a list of authors instead.  

* Supports CSV and XML through Accept headers
* Additionally, supports `GET /api/authors/csv` and `GET /api/authors/xml`





#### `GET /api/books/csv` and `GET /api/books/xml`

Convenient alternatives for downloading the list of books in CSV or XML format.  Useful when it  may be inconvenient to set the accept header.

#### `POST /api/books`

Add a new book to the database.  Expects `application/json` data with `title` and `author` fields present.  For example,

```
curl --location --request POST 'localhost:5000/api/books' \
--header 'Content-Type: application/json' \
--data-raw '{
	"title" : "Crime and Punishment",
	"author": "Fyodor Dostoevsky"
}'
```

When successful, will reply with the `book_id` of the created book.

```json
{
    "id": "2"
}
```

#### `GET /api/book/<book_id>`

Retrieve information about the book corresponding to `<book_id>`.  Expects `application/json` data with the `id` field present.  For example,

```
curl --location --request GET 'localhost:5000/api/books/2'
```

If no such book exists, will reply with a `404 NOT FOUND` error.  If the book exists, the book object will be returned with a `200 OK`:

```json
{
    "title": "Crime and Punishment",
    "author": "Fyodor Dostoevsky",
    "id": "2"
}
```

#### `DELETE /api/book/<book_id>`

Delete the book corresponding to `<book_id>`.  Expects `application/json` data with the `id` field present.  For example,

```
curl --location --request DELETE 'localhost:5000/api/books/2'
```

Possible responses:

* `200 OK` if the book was successfully deleted.
* `404 NOT FOUND` if no book was found with that identifier.
* `500 ERROR` if the book exists but could not be deleted (unlikely).

## Limitations

Below, I discuss some limitations of the appliation.  These limitations are also reflected in `#TODO` comments that I intentionally left throughout the code.

#### Database

* Due to the use of `rq` and `redis`, this application won't be able to run on Windows systems (except possibly through WSL, although this is untested).
* By default, `rq` considers jobs to fail if they take longer than 180 seconds.  Depending on the needs of the application, this limit could be extended.
* By default, `rq` only stores the results of tasks for 500 seconds.  Depending on the needs of the application, this limit could be extended.
* For the most part, the application does not gracefully handle Redis connection failures.  If any Redis command fails, the database will need to be cleaned up manually (or flushed entirely).  Because this application is very low-stakes, I made this tradeoff in the interest of time and simplicity.  For high-stakes applications, it would be important to ensure the database code is robust to failures.
* The application uses a number of O(N) database accesses, where N is the number of books.  For hundreds of books, this is acceptable, but the application may slow down dramatically if thousands of books are added.  This could be solved with paging, or by batching requests.

#### Synchronization Issues

Because `ml` and `web` are separate services working on the same data, they may not always be in sync.  In particular, the following may occur:

* The `ml` service might recommend a book that has already been deleted.
* The `ml` service might not have assigned a grouping to recently-added books. 
* Groups computed by the `ml` service may contain books that have been deleted. 

At the moment, these errors won't cause the application to crash, but they are not handled very gracefully.

### Machine Learning

* The grouping system always uses `K=5` clusters.  Ideally, K would scale appropriately with the number of books and their similarity / dissimilarity.