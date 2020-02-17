from redis import Redis;

redis = Redis(host='redis', port=6379, decode_responses=True)

def init_redis():
	pass;

#### DATABASE ACCESS ###########################################################

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
	book_id = str(redis.incr("next_book_id", 1));
	redis.zadd("book_ids", { book_id : book_id });
	# set book data
	book_key = f"book:{book_id}";
	redis.hset(book_key, "title", title);
	redis.hset(book_key, "author", author);
	# success: return new book_id
	return book_id;

def delete_book(id):
	# delete book object
	book_key = f"book:{id}";
	delete_count = redis.delete(book_key);
	# delete id
	zrem_count = redis.zrem("book_ids", id);

	# deletion may expose database integrity issues
	if delete_count < zrem_count:
		raise Exception(f"while deleting {book_key}, noticed dangling book object");
	if delete_count > zrem_count:
		raise Exception(f"while deleting {book_key}, noticed missing book object");
	
	# success
	return delete_count;