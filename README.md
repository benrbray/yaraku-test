# Yaraku Books

Benjamin Bray (benrbray@gmail.com)

*18 February 2020*



## Overview

This project implements a simple web service that allows the user to upload book titles and ask for book recommendations based on the uploaded catalog of books.  This document contains a ful description of the project's functionality and a discussion of design choices made during development.

### Setup

The project is designed to run on `localhost` as a web application.  The web interface runs on `localhost:5000` and the standalone machine learning service runs on `localhost:5001`. 

This application should work on both Linux/macOS, although I was only able to test on a machine running `Ubuntu 18.04`.  The application is containerized with `Docker` and assembled with `Docker Compose`, which must both be installed on the host system.  Since the project uses `Docker` to install its dependencies, internet access is assumed when building. 

To start the application (in detached mode), navigate to the top-level project folder and run:

````
docker-compose up -d
````

Include the optional `--build` flag to re-build if the source changes.  To stop the application:

````
docker-compose down
````

Docker has a habit of leaving behind images and containers, so I included a `Makefile` with a basic cleanup command.  (*Caution:* Depending on your Docker installation, this may influence your Docker images beyond just this project!)

````
make cleanup
````

### Testing

The `tests` folder contains a suite of tests intended to test the basic functionality of each container, as well as interaction between containers.  For simplicity, tests are packaged in a third docker container which is part of the same network as the application containers.  

To run the tests, make sure the application is running and use the following command to enter a shell on the testing container: 

```
docker exec -it yaraku_tests_1 bash
```

An interactive shell will start.  Now, run the `pytest` command to begin testing.

### Project Dependencies

Only Docker and `docker-compose` are needed to run the application.  When the project is run for the first time, Docker will build a set of docker images that include all of the application's dependencies.

I chose the following tools to implement the project:

* `Docker` and `docker-compose` for containerization and distribution.
* `flask` with `python3` for the web API, deployed with `gunicorn`.
* `redis` as a database and message broker, with the `rq` job queue for scheduling background workers.
* `nltk` for basic text processing (tokenization, stemming).
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

## Functionality

### Books API

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

* Due to the use of `rq` and `redis`, this application won't be able to run on Windows systems (except possibly through WSL, although this is untested).
* By default, `rq` considers jobs to fail if they take longer than 180 seconds.  Depending on the needs of the application, this limit could be extended.
* By default, `rq` only stores the results of tasks for 500 seconds.  Depending on the needs of the application, this limit could be extended.