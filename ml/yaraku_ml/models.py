# python
import collections;

# redis
from redis import Redis;
import rq;
from rq.job import Job;

# app source
from . import services;


# initialize redis connections
redis = Redis(host='redis', port=6379, decode_responses=True)
queue = rq.Queue(connection=redis);

def init_redis():
	pass;

#### DATABASE ACCESS ###########################################################

## Word Index ------------------------------------------------------------------

def rec_add_title(book_title, book_id):
	# split title into words
	words = services.tokenize_title(book_title);

	# for each word in title, store book_id in word lookup table
	pipe = redis.pipeline();
	for word in words:
		word_key = f"word:{word}";
		pipe.sadd(word_key, book_id);
	
	pipe.execute();

	# success
	return True;

def rec_delete_title(book_title, book_id):
	# split title into words
	words = services.tokenize_title(book_title);

	# for each word in title, remove book_id from word lookup table
	pipe = redis.pipeline();
	for word in words:
		word_key = f"word:{word}";
		pipe.srem(word_key, book_id);
	
	pipe.execute();

	# success
	return True;


def rec_recommend(book, num_recommend=5):
	# split title into words
	words = services.tokenize_title(book["title"]);

	# find all books with at least one word in common
	pipe = redis.pipeline();
	for word in words:
		word_key = f"word:{word}";
		pipe.smembers(word_key);

	# exclude empty query results
	common_counts = collections.Counter();
	for s in pipe.execute():
		if s and len(s) > 0:
			common_counts.update(s);
	
	# no recommendations?
	if len(common_counts) == 0:
		return [];
	
	# retrieve title/author for recommended books
	pipe = redis.pipeline();
	similar_ids = common_counts.most_common(num_recommend);
	for book_id,_ in similar_ids:
		book_key = f"book:{book_id}";
		pipe.hgetall(book_key);
	
	similar_books = pipe.execute();

	# include book_id with each recommendation
	for idx, (book_id, freq) in enumerate(similar_ids):
		similar_book = similar_books[idx];
		if similar_book:
			similar_book["id"] = book_id;
	
	return [sb for sb in similar_books if sb];

## Grouping --------------------------------------------------------------------

def group_add_book(book_id):
	# keep track of number of books added since last update to groups
	buffer_size = redis.incr("group:waiting");

	# once queue has reached max length, schedule grouping job
	# TODO: read max_size from config file
	max_size = 2;
	if buffer_size > max_size:
		group_regroup();

def group_regroup():
	print("ml :: regrouping!!");
	# schedule worker process
	# TODO: ensure regroup job isn't already running
	job = queue.enqueue("tasks.process");
	print("\t", job.id);
	# respond with job identifier
	return {
		"task_id" : job.id
	};

## Books API -------------------------------------------------------------------

def get_book(id):
	book_key = f"book:{id}";
	return redis.hgetall(book_key);

def get_all_books():
	#TODO: pagination? (use sorted set / zrange)
	#TODO: pipeline in batches?  (if expecting large number of books)

	# get (ordered) list of book_ids
	book_ids = list(redis.zrange("book_ids", 0, -1));

	# pipelined read
	pipe = redis.pipeline();
	for book_id in book_ids:
		book_key = f"book:{book_id}";
		pipe.hgetall(book_key);
	
	book_list = [];
	for idx,book in enumerate(pipe.execute()):
		# skip empty books
		if not book: continue;
		# retain book id
		book["id"] = book_ids[idx];
		book_list.append(book);
	
	return book_list;


def add_book(title, author):
	# TODO: error handling for redis add_book?
	# generate new book id
	book_id = redis.incr("next_book_id", 1);
	redis.zadd("book_ids", { book_id : book_id });
	# set book data
	book_key = f"book:{book_id}";
	redis.hset(book_key, "title", title);
	redis.hset(book_key, "author", author);
	# success
	return book_id;

def delete_book(id):
	# delete book object
	book_key = f"book:{id}";
	redis.delete(book_key);
	# delete id
	redis.zrem("book_ids", id);
	# success
	return True;