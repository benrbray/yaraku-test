import time;
import database;
from database import redis as db;
import nlp;

# scientific libraries
import gensim.downloader;
import numpy as np;
import sklearn as skl;
import sklearn.cluster;

w2v_model = None;

def init_word2vec():
	global w2v_model;
	if w2v_model is not None:
		return;
	
	w2v_model = gensim.downloader.load("glove-wiki-gigaword-50");

def process():
	print("worker :: computing groups");

	# initialization
	nlp.init();
	init_word2vec();
	
	# get list of all books
	book_list = database.get_all_books();
	num_books = len(book_list);

	if num_books == 0:
		db.set("group:count", 0);
		return False;

	# compute word2vec embeddings for each title
	w2v_dim = 50;
	title_vecs = np.zeros((num_books, w2v_dim));

	for idx in range(num_books):
		title_words = nlp.tokenize_title(book_list[idx]["title"]);
		title_vec = np.zeros(w2v_dim);
		for w in title_words:
			if w in w2v_model:
				title_vec += w2v_model.word_vec(w);
			else:
				print(w)
		
		title_vecs[idx,:] = title_vec;

	# k-means clustering
	num_groups = 5;
	kmeans = skl.cluster.KMeans(n_clusters=num_groups).fit(title_vecs);

	groups = [ [] for k in range(num_groups) ];
	for idx in range(num_books):
		book_id = book_list[idx]["id"];
		groups[kmeans.labels_[idx]].append(book_id);

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