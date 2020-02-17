let formAddBook = null;
let bookTableBody = null;

window.onload = function(){
	bookTableBody = document.getElementById("bookTableBody");
	formAddBook = document.getElementById("formAddBook");
	formAddBook.onsubmit = handleAddBook;

	refreshBookList();
}

//// DATA ////////////////////////////////////////////////////////////

function refreshBookList(){
	// build request
	let request = new XMLHttpRequest();
	request.open("GET", "/books", true);

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

	// delete button
	let btn_delete = document.createElement("button");
	btn_delete.innerText = "X";
	btn_delete.className = "btn btn-outline-danger btn-sm"
	btn_delete.setAttribute("type", "button");
	btn_delete.onclick = () => { handleDeleteBook(book.id) };
	
	// row data
	let td_delete = document.createElement("td");
	td_delete.appendChild(btn_delete);
	row.appendChild(td_delete);
	
	let td_title = document.createElement("td");
	let a_title = document.createElement("a");
	a_title.innerText = book.title;
	a_title.setAttribute("href", "/web/books/" + book.id);
	td_title.appendChild(a_title);
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

function handleDeleteBook(bookId){
	// build request
	let request = new XMLHttpRequest();
	request.open("DELETE", "/books/" + bookId, true);
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
	request.open("POST", "/books", true);
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