// common between all web views

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

function displayBookList(bookList, tableBodyElt){
	// clear previous table
	// TODO:  re-use old table rows
	while(tableBodyElt.firstChild){
		tableBodyElt.removeChild(tableBodyElt.firstChild);
	}

	// create new table rows
	bookList.forEach(book => {
		tableBodyElt.appendChild(makeBookTableRow(book))
	});	
}