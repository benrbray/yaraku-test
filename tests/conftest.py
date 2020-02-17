import redis;
import pytest;

################################################################################

@pytest.fixture
def redis_conn():
	"""
	Return a connection to the redis database.
	"""
	db = redis.Redis(host="redis", port=6379, decode_responses=True);
	return db;

@pytest.fixture
def redis_flush():
	"""
	Return a connection to the redis database after flushing its contents.
	"""
	db = redis.Redis(host="redis", port=6379, decode_responses=True);
	db.flushdb();

	return db;