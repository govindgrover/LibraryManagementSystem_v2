export const ManageBooks = {
	template: `
		<div class="container pt-5">
		<h1 class="mb-5">View & Update Books</h1>
	
		<div class="table-responsive mb-5">
			<table @click="eitherBtnClicked($event)" id="theBookDataTable" class="table table-striped table-hover caption-top"></table>
		</div>
	
		<!-- Update book records offcanvas -->
		<div class="offcanvas offcanvas-end" tabindex="-1" id="informationOffcanvas_for_book" aria-labelledby="informationOffcanvas_for_bookLabel">
			<div class="offcanvas-header">
			<h5 id="informationOffcanvas_for_bookLabel">Update the selected book</h5>
			<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
			</div>
			<div class="offcanvas-body px-4">
			<!-- Forms for updating book attributes -->
			<!-- Book Title Form -->
			<form @submit.prevent="sendUpdateCommand($event)" class="form" action="/lib/process/book/modify/title" method="POST" name="update-book-title-form">
				<div class="row">
				<div class="input-group mb-3">
					<input type="text" class="form-control" placeholder="Updated Book's Title" name="updated_title" />
					<button class="btn btn-outline-warning" type="submit">Update</button>
				</div>
				</div>
				<input type="hidden" app-data-id="hidden_book_id" name="book_id" value="" />
			</form>
			<hr class="border-danger" />
			
			<!-- Book Description Form -->
			<form @submit.prevent="sendUpdateCommand($event)" class="form" action="/lib/process/book/modify/desc" method="POST" name="update-book-desc-form">
				<div class="row">
				<div class="input-group mb-3">
					<input type="text" class="form-control" placeholder="Updated Book's Desc" name="updated_desc" />
					<button class="btn btn-outline-warning" type="submit">Update</button>
				</div>
				</div>
				<input type="hidden" app-data-id="hidden_book_id" name="book_id" value="" />
			</form>
			<hr class="border-danger" />
			
			<!-- Book Price Form -->
			<form @submit.prevent="sendUpdateCommand($event)" class="form" action="/lib/process/book/modify/price" method="POST" name="update-book-price-form">
				<div class="row">
				<div class="input-group mb-3">
					<input type="number" class="form-control" placeholder="Updated Book's Price" name="updated_price" />
					<button class="btn btn-outline-warning" type="submit">Update</button>
				</div>
				</div>
				<input type="hidden" app-data-id="hidden_book_id" name="book_id" value="" />
			</form>
			<hr class="border-danger" />
			
			<!-- Book Cover Image Form -->
			<form @submit.prevent="sendUpdateCommand($event, true)" class="form" action="/lib/process/book/modify/cimg" method="POST" name="update-book-cover-image-form">
				<div class="row">
				<div class="input-group mb-3">
					<input type="file" class="form-control" placeholder="Updated Book's Cover Image" name="updated_cimg" />
					<button class="btn btn-outline-warning" type="submit">Update</button>
				</div>
				</div>
				<input type="hidden" app-data-id="hidden_book_id" name="book_id" value="" />
			</form>
			<hr class="border-danger" />
			
			<!-- Book Active Status Form -->
			<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/book/modify/active" method="POST" name="update-book-active-status-form">
				<div class="row">
				<div class="col-6 offset-md-2 form-check align-self-center form-switch form-check-reverse mb-3">
					<label class="form-check-label" for="update_book_active_status_checkbox">Active Status</label>
					<input class="form-check-input" type="checkbox" role="switch" name="updated_active_status" id="update_book_active_status_checkbox">
				</div>
				<div class="col-4">
					<button class="btn btn-outline-warning" type="submit">Update</button>
				</div>
				</div>
				<input type="hidden" app-data-id="hidden_book_id" name="book_id" value="" />
			</form>
			<hr class="border-danger" />
			
			<!-- Book Delete Form -->
			<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/book/modify/delete" method="POST" name="delete-book-form">
				<div class="row">
				<div class="col">
					<button class="btn btn-outline-danger" type="submit">Delete ?</button>
				</div>
				</div>
				<input type="hidden" app-data-id="hidden_book_id" name="book_id" value="" />
			</form>
			</div>
		</div>
	
		<!-- BS Modal to show book details -->
		<div class="modal fade" id="view_book_details_modal" tabindex="-1" aria-labelledby="view_book_details_modal_Label" aria-hidden="true">
			<div class="modal-dialog modal-lg">
			<div class="modal-content">
				<div class="modal-header">
				<h5 class="modal-title" id="view_book_details_modal_Label">Book details</h5>
				<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
				</div>
				<div id="modalContentBody" class="modal-body p-3"></div>
				<div class="modal-footer">
				<button type="button" class="btn btn-outline-info" data-bs-dismiss="modal">Close</button>
				</div>
			</div>
			</div>
		</div>
		</div>
	`,
	setup() {
		const tableData = Vue.ref([]);
		const tableId = '#theBookDataTable';

		// Fetch data from the server and update the table
		const fetchDataFromController = async (action) => {
			try {
				const response = await fetch(action, { method: 'POST' });
				const data = await response.json();
				loadBooksData(data, tableId);
			} catch (err) {
				console.error('Error occurred! Please contact the developer.', err);
			}
		};

		const loadBooksData = (data, dataTableId) => {
			if ($.fn.DataTable.isDataTable(dataTableId)) {
				$(dataTableId).DataTable().clear();
				$(dataTableId).DataTable().destroy();
			}

			if (data.status === 'ok') {
				$(dataTableId).DataTable({
					caption: 'For: Books',
					retrieve: true,
					columnDefs: [
						{
							targets: -1,
							searchable: false,
							orderable: false,
						},
					],
					columns: [
						{ title: 'Title', data: 'title' },
						{ title: 'ISBN', data: 'isbn' },
						{ title: 'Edition', data: 'edition' },
						{ title: 'Price', data: 'price' },
						{ title: 'Publication Date', data: 'publication_date' },
						{
							title: 'Action',
							defaultContent: `
								<div class='btn-group' role='group'>
								<button type='button' class='btn btn-outline-secondary panel-btn' data-btn='update' data-bs-toggle='offcanvas' data-bs-target='#informationOffcanvas_for_book' aria-controls='informationOffcanvas_for_book'>Update</button>
								<button type='button' class='btn btn-primary view-book-details' data-btn='view' data-bs-toggle='modal' data-bs-target='#view_book_details_modal'>View</button>
								</div>
							`,
							createdCell: (cell, cellData, rowData) => {
								$(cell).find('.view-book-details').attr('app-data-book-id', rowData.book_id);
							},
						},
					],
					data: data.data,
					rowId: (row) => row.book_id,
					rowCallback: (row, data) => {
						if (data.is_active == 0) {
							row.setAttribute('class', 'table-warning');
						} else if (data.is_active == 1) {
							row.setAttribute('class', 'table-success');
						}

						$(row).find('.view-book-details').data('hidden_data', {
							title: data.title,
							authors: data.authors,
							publisher: data.publisher,
							category: data.category,
							genre: data.genre,
							language: data.language,
							description: data.description,
							feedbacks: data.feedbacks,
							cover_image: data.cover_image,
						});
					},
				});
			}


		};

		const openSidePanel = (event) => {
			const btn = event.target.closest('.panel-btn');
			if (btn) {
				document.querySelectorAll("input[app-data-id='hidden_book_id']").forEach(element => {
					element.setAttribute("value", btn.closest('tr').id);
				});

				const isActive_book = btn.closest('tr').classList[0] == 'table-success';
				document.getElementById("update_book_active_status_checkbox").checked = isActive_book;
			}
		}

		const openBookDetailsModal = (event) => {
			let bookId = event.target.getAttribute('app-data-book-id')
			let bookDetails = $('button[app-data-book-id="' + bookId + '"]').data('hidden_data')
			let modalBody = $('#modalContentBody')
			let detailsHtml = null

			modalBody.innerHTML = ""

			if (bookDetails != null) {
				detailsHtml = `
					<div class="row mb-3">
						<div class="col-3"><b>Title:</b></div>
						<div class="col">${bookDetails.title || 'N/A'}</div>
					</div>
					<div class="row mb-3">
						<div class="col-3"><b>Authors:</b></div>
						<div class="col">${bookDetails.authors ? bookDetails.authors.join(', ') : 'N/A'}</div>
					</div>
					<div class="row mb-3">
						<div class="col-3"><b>Publisher:</b></div>
						<div class="col">${bookDetails.publisher || 'N/A'}</div>
					</div>
					<div class="row mb-3">
						<div class="col-3"><b>Category:</b></div>
						<div class="col">${bookDetails.category || 'N/A'}</div>
					</div>
					<div class="row mb-3">
						<div class="col-3"><b>Genre:</b></div>
						<div class="col">${bookDetails.genre || 'N/A'}</div>
					</div>
					<div class="row mb-3">
						<div class="col-3"><b>Language:</b></div>
						<div class="col">${bookDetails.language || 'N/A'}</div>
					</div>
					<div class="row mb-3">
						<div class="col-3"><b>Description:</b></div>
						<div class="col">${bookDetails.description || 'N/A'}</div>
					</div>
					<div class="row mb-3">
						<div class="col-3"><b>Feedbacks:</b></div>
						<div class="col">
						${bookDetails.feedbacks ? bookDetails.feedbacks.map(f => `${f.rating} Stars - ${f.feedback}`).join('<br/>') : 'N/A'}
						</div>
					</div>
					<div class="row mb-3">
						<div class="col-3"><b>Cover Image:</b></div>
						<div class="col text-center">
						<img src="http://127.0.0.1:8000/static/ci/${bookDetails.cover_image || 'default_image_url'}" alt="Book Cover" class="img-fluid">
						</div>
					</div>
				`;
				modalBody.html(detailsHtml)
			} else {
				modalBody.html('<p>No details available.</p>')
			}

			$('#view_book_details_modal').modal('show')
		}

		const eitherBtnClicked = (event) => {
			let op = event.target.getAttribute('data-btn')

			if (op == 'update') {
				openSidePanel(event)
			}
			else if (op == 'view') {
				openBookDetailsModal(event)
			}
		}

		const sendUpdateCommand = (event, is_img = false) => {
			if (is_img) {
				const form = document.forms['update-book-cover-image-form']
				const formData = new FormData(form)

				try {
					fetch(form.action,
					{
						method: 'POST'
						, body: formData
					})
						.then((response) => response.json())
						.then((data) => {
							alert(data['msg'])

							if (data['status'] == 'ok') {
								fetchDataFromController('/lib/process/get/books');
							}
						});
				} catch (error) {
					console.error('Error fetching data:', error);
				}
			}
			else {
				const form = event.target
				const formData = new FormData(form)
				const jsonData = Object.fromEntries(formData.entries());

				try {
					fetch(form.action,
					{
						method: 'POST'
						, headers: {
							"Content-Type": "application/json",
						}
						, body: JSON.stringify(jsonData)
					})
						.then((response) => response.json())
						.then((data) => {
							alert(data['msg'])

							if (data['status'] == 'ok') {
								fetchDataFromController('/lib/process/get/books');
							}
						});
				} catch (error) {
					console.error('Error fetching data:', error);
				}
			}
		}

		Vue.onMounted(() => {
			fetchDataFromController('/lib/process/get/books');
		});

		return {
			tableData, eitherBtnClicked, sendUpdateCommand
		};
	},
}	