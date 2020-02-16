import flask_sqlalchemy;

db = flask_sqlalchemy.SQLAlchemy();

class Book(db.Model):
	__tablename__ = "books";
	id = db.Column(db.Integer, primary_key=True);
	#TODO: variable-length strings?  can titles be >100 characters?
	#TODO: String vs Text?
	title = db.Column(db.String(100));
	author = db.Column(db.String(100));