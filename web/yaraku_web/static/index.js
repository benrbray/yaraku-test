// runs on "index.html"

let formAddBook = null;
let bookTableBody = null;

window.onload = function(){
	bookTableBody = document.getElementById("bookTableBody");
	formAddBook = document.getElementById("formAddBook");
	formAddBook.onsubmit = handleAddBook;

	refreshBookList();
}

function refreshBookList(){
	// build request
	let request = new XMLHttpRequest();
	request.open("GET", "/api/books", true);

	request.onload = function(evt){
		displayBookList(JSON.parse(evt.target.response), bookTableBody);
	}

	request.onerror = function(){
		// TODO: handle errors in book list request
	}

	request.send();
}

//// EVENT HANDLERS //////////////////////////////////////////////////

function handleDeleteBook(bookId){
	// build request
	let request = new XMLHttpRequest();
	request.open("DELETE", "/api/books/" + bookId, true);
	request.setRequestHeader("Content-Type", "application/json");

	request.onload = function(){
		refreshBookList();
	}

	request.onerror = function(){
		// TODO: handle delete error
	}

	request.send();
}

function handleAddBook(event){
	event.preventDefault();

	// build request
	let request = new XMLHttpRequest();
	request.open("POST", "/api/books", true);
	request.setRequestHeader("Content-Type", "application/json");
	
	request.onload = function(){
		// TODO: handle response to book add
		refreshBookList();
	}

	request.onerror = function(){
		// TODO: handle errors in book list request
		refreshBookList();
	}

	// build request data
	var message = {
		title  : formAddBook.elements.title.value,
		author : formAddBook.elements.author.value
	}

	request.send(JSON.stringify(message));

	return false;
}