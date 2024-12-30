export const IssueRequests = {
	template: `
		<h1 class="mb-5">Manage Issue Requests</h1>

		<div class="table-responsive mb-5">
			<table @click="processPurchase($event)" id="theRequestsDataTable" class="table table-striped table-hover caption-top">
			</table>
		</div>

		<div class="modal fade" id="purchase_book_modal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="account_delete_modal_Label" aria-hidden="true">
			<div class="modal-dialog modal-dialog-centered">
				<div class="modal-content">
					<div class="modal-header">
						<h1 class="modal-title fs-5" id="purchase_book_modal_Label">Please complete the required!</h1>
						<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
					</div>
					<form @submit.prevent="purchaseBook($event)" name="purchase-book-form">
						<div class="modal-body">
							<div class="input-group mb-3">
								<label class="input-group-text" for="transaction_id">Transaction ID</label>
								<input type="text" class="form-control" id="transaction_id" name="transaction_id" required />					
							</div>

							<div class="input-group mb-3">
								<label class="input-group-text" for="written_cost">Price Charged</label>
								<input type="numeric" class="form-control" id="written_cost" name="written_cost" required />					
							</div>

							<input type="hidden" class="form-control" app-data-id='hidden_user_id' name="book_requested_by" value="" required />
							<input type="hidden" class="form-control" app-data-id='hidden_book_id' name="requested_book_id" value="" required />
						</div>
						<div class="modal-footer">
							<button type="button" class="btn btn-outline-warning" data-bs-dismiss="modal">Cancel</button>
							<button type="submit" class="btn btn-outline-info">Proceed ?</button>
						</div>
					</form>
				</div>
			</div>
		</div>

	`,
	setup() {
		const dataTableId = Vue.ref('#theRequestsDataTable');
		const requestData = Vue.ref([]);

		const purchaseBook = async (event) => {
			const form = event.target
			const formData = new FormData(form);
			const jsonData = Object.fromEntries(formData.entries());

			try {
				const response = await fetch('/lib/process/issue-requests/purchase', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify(jsonData),
				})
				const data = await response.json()

				alert(data.msg)
				if (data.status == 'ok') {
					fetchDataFromController('/lib/process/get/issue-requests', loadRequestData);
				}
			} catch (err) {
				console.error('Error occurred! Please contact developer.', err);
			}
		}

		const fetchDataFromController = async (action, loadDataCallback) => {
			try {
				const response = await fetch(action, { method: 'POST' });
				const data = await response.json();
				// showToasts(data, 'msg', 'Message');
				loadDataCallback(data, dataTableId.value);
			} catch (err) {
				console.error('Error occurred! Please contact developer.', err);
			}
		};

		const loadRequestData = (data, dataTableId) => {
			if ($.fn.DataTable.isDataTable(dataTableId)) {
				$(dataTableId).DataTable().clear();
				$(dataTableId).DataTable().destroy();
			}

			if (!data || data.status !== 'ok') {
				return;
			}

			$(dataTableId).DataTable({
				caption: 'For: Raised Requests of Books',
				retrieve: true,
				columnDefs: [
					{
						targets: -1,
						searchable: false,
						orderable: false,
					},
				],
				columns: [
					{ title: 'Title', data: 'book_title' },
					{ title: 'ISBN', data: 'book_isbn' },
					{ title: 'Date Requested', data: 'date_of_request' },
					{ title: 'Requested By', data: 'requested_by_name' },
					{ title: 'Chargeable Rate', data: 'max_price' },
					{
						title: 'Action',
						data: null,
						render: (data, type, row) => `
					<form @submit.prevent="handleFormSubmit" name="issue-book-form">
						<input type="hidden" name="book_requested_by" value="${row.requested_by_id}" />
						<input type="hidden" name="requested_book_id" value="${row.book_id}" />

						<div class="btn-group" role="group">
							<button type="submit" class="btn btn-outline-success">Issue</button>
							<button type="button" class="btn btn-outline-info open-modal" data-bs-toggle="modal" data-bs-target="#purchase_book_modal">Purchase</button>
						</div>
					</form>
					`,
					},
				],
				data: data.data,
				rowId: (row) => row.book_id,
				drawCallback: () => {
					const forms = document.querySelectorAll("form[name='issue-book-form']");
					forms.forEach(form => {
						form.addEventListener('submit', handleFormSubmit);
					});
				},
			});
		};

		const handleFormSubmit = async (event) => {
			event.preventDefault();
			const form = event.target;
			const formData = new FormData(form);
			const jsonData = Object.fromEntries(formData.entries());

			try {
				const response = await fetch('/lib/process/issue-requests/issue', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify(jsonData),
				});

				const result = await response.json();

				if (result.status === 'ok') {
					fetchDataFromController('/lib/process/get/issue-requests', loadRequestData);
				}
			} catch (err) {
				console.error('Error occurred during form submission.', err);
			}
		};

		const processPurchase = (event) => {
			const form = event.target.parentElement.parentElement

			const bookRequestedBy = form.querySelector('input[name="book_requested_by"]').value;
			const requestedBookId = form.querySelector('input[name="requested_book_id"]').value;
	
			const purchaseForm = document.forms['purchase-book-form']

			purchaseForm.querySelector('input[name="book_requested_by"]').value = bookRequestedBy
			purchaseForm.querySelector('input[name="requested_book_id"]').value = requestedBookId
		}

		Vue.onMounted(() => {
			fetchDataFromController('/lib/process/get/issue-requests', loadRequestData);
		});

		return {
			dataTableId,
			requestData,
			handleFormSubmit,
			purchaseBook,
			processPurchase
		}
	},
};