import yaraku_ml;
import yaraku_ml.services;
import time;

if __name__ == "__main__":
	# initialize word2vec
	yaraku_ml.services.init();

	# run flask in debug mode
	print("Starting YARAKU ML...");
	app = yaraku_ml.create_app();
	app.run(host="0.0.0.0", debug=True, use_reloader=False);