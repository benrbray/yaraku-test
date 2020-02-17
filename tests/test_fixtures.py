import pytest;
import requests;
import redis;
import api_helpers as api;


#### TEST FIXTURES (defined in conftest.py) ####################################

def test_redis_conn(redis_conn):
	db = redis_conn;
	num_keys = db.dbsize();
	assert(num_keys >= 0);

def test_redis_flush(redis_flush):
	db = redis_flush;
	num_keys = db.dbsize();
	assert(num_keys == 0);