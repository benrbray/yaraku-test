import yaraku_web;

if __name__ == "__main__":
	# run flask in debug mode
	print("Starting YARAKU BOOKS...");
	app = yaraku_web.create_app();
	app.run(host="0.0.0.0", debug=True);