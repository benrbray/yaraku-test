import time;
import database;
from database import redis as db;
import nlp;

def process():
	print("worker :: computing groups");
	nlp.init();
	
	# get list of all books
	book_list = database.get_all_books();
	num_books = len(book_list);

	if num_books == 0:
		db.set("group:count", 0);
		return False;

	# convert titles to lists of word tokens
	book_titles = [];
	max_len = 0;
	for book in book_list:
		words = nlp.tokenize_title(book["title"]);
		book_titles.append(words);
		max_len = max(max_len, len(words));

	# assign groups based on word length
	num_groups = max_len;
	groups = [ [] for k in range(num_groups) ];

	for idx in range(num_books):
		book_id = book_list[idx]["id"];
		words = book_titles[idx];
		groups[len(words)-1].append(book_id);

	# clear old groups
	old_num_groups = db.getset("group:count", 0);
	if old_num_groups is not None:
		pipe = db.pipeline(transaction=True);
		for k in range(int(old_num_groups)):
			group_key = f"group:{k}";
			pipe.delete(group_key);
		result = pipe.execute();

	# save new groups
	db.set("group:count", num_groups);
	for k in range(num_groups):
		group_key = f"group:{k}"
		if len(groups[k]) > 0:
			db.sadd(group_key, *groups[k]);
	
	return True;