export const ActiveBorrows = {
	template: `
		<h1 class="mb-5">Manage Active Borrows</h1>

		<div class="d-flex justify-content-between align-items-center my-5">
			<!-- <h5 class="mb-0">Here is some analysis</h5> -->
			<form @submit.prevent="sendBorrownaceReport" name="get-borrowance-form">
				<button id="get-borrowance-button" class="btn btn-outline-info" type="submit">Request full report?</button>
			</form>
		</div>

		<div class="table-responsive mb-5">
			<table id="theBorrowDataTable" class="table table-striped table-hover caption-top">
			</table>
		</div>
	`,
	setup() {
		const borrowData = Vue.ref([]);
		const dataTableId = Vue.ref('#theBorrowDataTable');

		const sendBorrownaceReport = async () => {
			try {
				const response = await fetch('/lib/process/get-borrowance-report', { method: 'POST' })
				const data = await response.json()

				if (data)
					if (data.status == 'ok') {
						alert(data.msg)
					}
			}
			catch (err) {
					console.error('Error occurred! Please contact developer.', err);
			}
		}

		// Function to fetch data from the controller
		const fetchDataFromController = async (action) => {
			try {
				const response = await fetch(action, { method: 'POST' });
				const data = await response.json();
				if (data.status === 'ok') {
					borrowData.value = data.data;
					initializeDataTable();
				}
			} catch (err) {
				console.error('Error occurred! Please contact developer.', err);
			}
		};

		// Function to initialize the DataTable
		const initializeDataTable = () => {
			if ($.fn.DataTable.isDataTable(dataTableId.value)) {
				$(dataTableId.value).DataTable().clear();
				$(dataTableId.value).DataTable().destroy();
			}

			if (borrowData.value.length === 0) return;

			$(dataTableId.value).DataTable({
				caption: 'For: Currently Active Borrows',
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
					{ title: 'Issued To', data: 'issued_to_name' },
					{ title: 'Date of Issue', data: 'date_of_issue' },
					{ title: 'Date of Return', data: 'date_of_return' },
					{
						title: 'Action',
						data: null,
						render: (data, type, row) => `
				<form @submit.prevent="handleFormSubmit" name="revoke-access-form">
					<button type="submit" class="btn btn-outline-warning">Revoke Access</button>
					<input type="hidden" name="issued_to_id" value="${row.issued_to_id}" />
					<input type="hidden" name="issued_book_id" value="${row.book_id}" />
				</form>
				`,
					},
				],
				data: borrowData.value,
				rowId: (row) => row.book_id,
				drawCallback: () => {
					const forms = document.querySelectorAll("form[name='revoke-access-form']");
					forms.forEach(form => {
						form.addEventListener('submit', handleFormSubmit);
					});
				},
			});
		};

		// Function to handle form submission
		const handleFormSubmit = async (event) => {
			event.preventDefault();
			const form = event.target;
			const formData = new FormData(form);
			const jsonData = Object.fromEntries(formData.entries());

			try {
				const response = await fetch(
					'/lib/process/borrow-history/revoke',
					{
						method: 'POST',
						headers: {
							'Content-Type': 'application/json',
						},
						body: JSON.stringify(jsonData),
					});
				const result = await response.json();
				if (result.status === 'ok') {
					fetchDataFromController('/lib/process/get/borrow-history');
				}
			} catch (err) {
				console.error('Error occurred during form submission.', err);
			}
		};

		Vue.onMounted(() => {
			fetchDataFromController('/lib/process/get/borrow-history');
		});

		return {
			borrowData,
			dataTableId,
			handleFormSubmit,
			sendBorrownaceReport,
		};
	},
};