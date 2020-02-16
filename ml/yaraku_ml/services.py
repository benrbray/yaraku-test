import gensim;
import gensim.downloader;
import sklearn as skl;
import numpy as np;

model = None;

def init():
	global model;
	print("Downloading Pre-trained Word Vectors...");
	#model = gensim.downloader.load("glove-wiki-gigaword-50");