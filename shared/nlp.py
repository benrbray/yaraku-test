"""
NLP.PY
Contains helper functions for working with text data.
"""

import nltk;

stopwords = None;
tokenizer = None;
stemmer = None;

def init():
	# create stopwords list
	global stopwords;
	if stopwords is None:
		nltk.download("stopwords");
		stopwords = set(nltk.corpus.stopwords.words("english"));

	# initialize tokenizer
	global tokenizer;
	if tokenizer is None:
		nltk.download("punkt");
		tokenizer = nltk.tokenize.RegexpTokenizer("\w+");

	# initialize stemmer
	global stemmer;
	if stemmer is None:
		stemmer = nltk.stem.PorterStemmer();


def tokenize_title(title):
	"""
	Converts the title to a sequence of words in several steps:
		1. convert to lower case
		2. tokenize
		2. remove stop words (the, and, by, ...)
		3. stemming via Porter stemmer
	@param (title) string
	"""
	words = tokenizer.tokenize(title.lower());
	words = [stemmer.stem(w) for w in words if w not in stopwords];
	return words;