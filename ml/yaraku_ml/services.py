import gensim;
import gensim.downloader;
import sklearn as skl;
import numpy as np;
import nltk;

model = None;
stopwords = None;
tokenizer = None;
stemmer = None;

def init():
	global model;
	print("Downloading Pre-trained Word Vectors...");
	#model = gensim.downloader.load("glove-wiki-gigaword-50");

	# create stopwords list
	nltk.download("stopwords");
	global stopwords;
	stopwords = set(nltk.corpus.stopwords.words("english"));

	# initialize tokenizer
	nltk.download("punkt");
	global tokenizer;
	tokenizer = nltk.tokenize.RegexpTokenizer("\w+");

	# initialize stemmer
	global stemmer;
	stemmer = nltk.stem.PorterStemmer();


def tokenize_title(title):
	words = tokenizer.tokenize(title.lower());
	words = [stemmer.stem(w) for w in words if w not in stopwords];
	return words;