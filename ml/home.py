import yaraku_ml;
import yaraku_ml.nlp;
import time;

if __name__ == "__main__":
	# initialize nlp
	yaraku_ml.nlp.init();

	# run flask in debug mode
	print("Starting YARAKU ML...");
	app = yaraku_ml.create_app();
	app.run(host="0.0.0.0", debug=True, use_reloader=False);