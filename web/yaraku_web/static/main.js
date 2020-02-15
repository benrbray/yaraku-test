let formAddBook = null;

window.onload = function(){
	formAddBook = document.getElementById("formAddBook");
	formAddBook.onsubmit = handleAddBook;
}

//// DATA ////////////////////////////////////////////////////////////

function refreshBookList(){
	// build request
	let request = new XMLHttpRequest();
	request.open("GET", "/json", true);

	request.onload = function(evt){
		console.log(evt.target.response);
		displayBookList(JSON.parse(evt.target.response));
	}

	request.onerror = function(){
		// TODO: handle errors in book list request
	}

	request.send();
}

function displayBookList(bookList){
	console.log(bookList);
}

//// EVENT HANDLERS //////////////////////////////////////////////////

function handleAddBook(event){
	event.preventDefault();

	// build request
	let request = new XMLHttpRequest();
	request.open("POST", "/add", true);
	request.setRequestHeader("Content-Type", "application/json");
	
	request.onload = function(){
		// TODO: handle response to book add
	}

	request.onerror = function(){
		// TODO: handle errors in book list request
	}

	// build request data
	var message = {
		title  : formAddBook.elements.title.value,
		author : formAddBook.elements.author.value
	}
	
	request.send(JSON.stringify(message));

	return false;
}