# python
import collections;

# redis
from redis import Redis;
import rq;
from rq.job import Job;

# app source
from . import nlp;
from . import database;
from .database import redis;

# initialize redis connections
queue = rq.Queue(connection=redis);

def init_redis():
	pass;

#### DATABASE ACCESS ###########################################################

## Word Index ------------------------------------------------------------------

def rec_add_title(book_title, book_id):
	# split title into words
	words = nlp.stem_title(book_title);

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
	words = nlp.stem_title(book_title);

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
	words = nlp.stem_title(book["title"]);

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
	buffer_size = int(redis.incr("group:waiting"));

	# once queue has reached max length, schedule grouping job
	# for now, regroup after every fifth addition
	# TODO: read max_size from config file
	max_size = 5;
	if buffer_size >= max_size:
		group_regroup();
		redis.set("group:waiting", 0);

def group_regroup():
	print("ml :: regrouping!!");
	# schedule worker process
	# TODO: ensure regroup job isn't already running
	job = queue.enqueue("tasks.process");
	print("\tjob id:", job.id);
	# respond with job identifier
	return {
		"task_id" : job.id
	};