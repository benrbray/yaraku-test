let formAddBook = null;
let bookTableBody = null;

window.onload = function(){
	bookTableBody = document.getElementById("bookTableBody");
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

function makeBookTableRow(book){
	let row = document.createElement("tr");
	
	let td_title = document.createElement("td");
	td_title.innerText = book.title;
	row.appendChild(td_title);

	let td_author = document.createElement("td");
	td_author.innerText = book.author;
	row.appendChild(td_author);

	return row;
}

function displayBookList(bookList){
	// clear previous table
	// TODO:  re-use old table rows
	while(bookTableBody.firstChild){
		bookTableBody.removeChild(bookTableBody.firstChild);
	}

	// create new table rows
	bookList.forEach(book => {
		bookTableBody.appendChild(makeBookTableRow(book))
	});	
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