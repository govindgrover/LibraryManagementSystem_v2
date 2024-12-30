export const ManageMasters = {
	template: `
		<h1 class="mb-5">View & Update Records</h1>
	
		<div class="row">
			<div class="col">
			<select @change="updateTable($event)" class="form-select form-select-sm mb-3" aria-label="Select master to view" autofocus>
				<option value="" selected disabled>Select Master</option>
				<option value="author">Author</option>
				<option value="publisher">Publisher</option>
				<option value="category">Category</option>
				<option value="genre">Genre</option>
				<option value="language">Language</option>
			</select>
			</div>
		</div>
	
		<hr class="border-secondary mb-3" />
	
		<div :key="tableKey" class="table-responsive mb-5">
			<table @click='openSidePanel($event)' id="theDataTable" class="table table-striped table-hover caption-top"></table>
		</div>

		<div class="offcanvas offcanvas-end" data-bs-backdrop="static" tabindex="-1" id="informationOffcanvas_author"
			aria-labelledby="offcanvasRightLabel">
			<div class="offcanvas-header">
				<h5 class="offcanvas-title" id="informationOffcanvas_Label">Update the selected author</h5>
				<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
			</div>
			<div class="offcanvas-body px-4">
				<form @submit.prevent="sendUpdateCommand($event)" class="form" action="/lib/process/author/modify/name" method="POST" name="update-author-name-form">
					<div class="row">
						<div class="input-group mb-3">
							<input type="text" class="form-control" placeholder="Updated Author's Name" name="updated_name" />
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>
					<input type="hidden" app-data-id="hidden_author_id" name="author_id" value="" />
				</form>

				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form" action="/lib/process/author/modify/bio" method="POST" name="update-author-bio-form">
					<div class="row">
						<div class="input-group mb-3">
							<input type="text" class="form-control" placeholder="Updated Author's Bio" name="updated_bio" />
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_author_id" name="author_id" value="" />
				</form>

				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/author/modify/active" method="POST" name="update-author-active-status-form">
					<div class="row">
						<div class="col-6 offset-md-2 form-check align-self-center form-switch form-check-reverse mb-3">
							<label class="form-check-label" for="update_author_active_status_checkbox">Active Status</label>
							<input class="form-check-input" type="checkbox" role="switch" name="updated_active_status"
								id="update_author_active_status_checkbox">
						</div>

						<div class="col-4">
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_author_id" name="author_id" value="" />
				</form>

				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/author/modify/delete" method="POST" name="delete-author-form">
					<div class="row">
						<div class="col">
							<button class="btn btn-outline-danger" type="submit">Delete ?</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_author_id" name="author_id" value="" />
				</form>

			</div>
		</div>

		<div class="offcanvas offcanvas-end" data-bs-backdrop="static" tabindex="-1" id="informationOffcanvas_publisher"
			aria-labelledby="offcanvasRightLabel">
			<div class="offcanvas-header">
				<h5 class="offcanvas-title" id="informationOffcanvas_Label">Update the selected publisher</h5>
				<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
			</div>
			<div class="offcanvas-body px-4">
				<form @submit.prevent="sendUpdateCommand($event)" class="form" action="/lib/process/publisher/modify/name" method="POST" name="update-publisher-name-form">
					<div class="row">
						<div class="input-group mb-3">
							<input type="text" class="form-control" placeholder="Updated Publisher's Name"
								name="updated_name" />
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>
					<input type="hidden" app-data-id="hidden_publisher_id" name="publisher_id" value="" />
				</form>

				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form" action="/lib/process/publisher/modify/desc" method="POST" name="update-publisher-desc-form">
					<div class="row">
						<div class="input-group mb-3">
							<input type="text" class="form-control" placeholder="Updated Publisher's Description"
								name="updated_desc" />
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_publisher_id" name="publisher_id" value="" />
				</form>

				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/publisher/modify/active" method="POST" name="update-publisher-active-status-form">
					<div class="row">
						<div class="col-6 offset-md-2 form-check align-self-center form-switch form-check-reverse mb-3">
							<label class="form-check-label" for="update_publisher_active_status_checkbox">Active
								Status</label>
							<input class="form-check-input" type="checkbox" role="switch" name="updated_active_status"
								id="update_publisher_active_status_checkbox">
						</div>

						<div class="col-4">
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_publisher_id" name="publisher_id" value="" />
				</form>
				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/publisher/modify/delete" method="POST" name="delete-publisher-form">
					<div class="row">
						<div class="col">
							<button class="btn btn-outline-danger" type="submit">Delete ?</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_publisher_id" name="publisher_id" value="" />
				</form>
			</div>
		</div>

		<div class="offcanvas offcanvas-end" data-bs-backdrop="static" tabindex="-1" id="informationOffcanvas_category"
			aria-labelledby="offcanvasRightLabel">
			<div class="offcanvas-header">
				<h5 class="offcanvas-title" id="informationOffcanvas_Label">Update the selected category</h5>
				<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
			</div>
			<div class="offcanvas-body px-4">
				<form @submit.prevent="sendUpdateCommand($event)" class="form" action="/lib/process/category/modify/name" method="POST" name="update-category-name-form">
					<div class="row">
						<div class="input-group mb-3">
							<input type="text" class="form-control" placeholder="Updated Category's Name"
								name="updated_name" />
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>
					<input type="hidden" app-data-id="hidden_category_id" name="category_id" />
				</form>

				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/category/modify/active" method="POST" name="update-category-active-status-form">
					<div class="row">
						<div class="col-6 offset-md-2 form-check align-self-center form-switch form-check-reverse mb-3">
							<label class="form-check-label" for="update_category_active_status_checkbox">Active
								Status</label>
							<input class="form-check-input" type="checkbox" role="switch" name="updated_active_status"
								id="update_category_active_status_checkbox">
						</div>

						<div class="col-4">
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_category_id" name="category_id" />
				</form>
				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/category/modify/delete" method="POST" name="delete-category-form">
					<div class="row">
						<div class="col">
							<button class="btn btn-outline-danger" type="submit">Delete ?</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_category_id" name="category_id" value="" />
				</form>
			</div>
		</div>

		<div class="offcanvas offcanvas-end" data-bs-backdrop="static" tabindex="-1" id="informationOffcanvas_genre"
			aria-labelledby="offcanvasRightLabel">
			<div class="offcanvas-header">
				<h5 class="offcanvas-title" id="informationOffcanvas_Label">Update the selected genre</h5>
				<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
			</div>
			<div class="offcanvas-body px-4">
				<form @submit.prevent="sendUpdateCommand($event)" class="form" action="/lib/process/genre/modify/name" method="POST" name="update-genre-name-form">
					<div class="row">
						<div class="input-group mb-3">
							<input type="text" class="form-control" placeholder="Updated Genre's Name"
								name="updated_name" />
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>
					<input type="hidden" app-data-id="hidden_genre_id" name="genre_id" value="" />
				</form>

				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/genre/modify/active" method="POST" name="update-genre-active-status-form">
					<div class="row">
						<div class="col-6 offset-md-2 form-check align-self-center form-switch form-check-reverse mb-3">
							<label class="form-check-label" for="update_genre_active_status_checkbox">Active Status</label>
							<input class="form-check-input" type="checkbox" role="switch" name="updated_active_status"
								id="update_genre_active_status_checkbox">
						</div>

						<div class="col-4">
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_genre_id" name="genre_id" />
				</form>
				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/genre/modify/delete" method="POST" name="delete-genre-form">
					<div class="row">
						<div class="col">
							<button class="btn btn-outline-danger" type="submit">Delete ?</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_genre_id" name="genre_id" value="" />
				</form>
			</div>
		</div>

		<div class="offcanvas offcanvas-end" data-bs-backdrop="static" tabindex="-1" id="informationOffcanvas_language"
			aria-labelledby="offcanvasRightLabel">
			<div class="offcanvas-header">
				<h5 class="offcanvas-title" id="informationOffcanvas_Label">Update the selected language</h5>
				<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
			</div>
			<div class="offcanvas-body px-4">
				<form @submit.prevent="sendUpdateCommand($event)" class="form" action="/lib/process/language/modify/name" method="POST" name="update-language-name-form">
					<div class="row">
						<div class="input-group mb-3">
							<input type="text" class="form-control" placeholder="Updated Language's Name"
								name="updated_name" />
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>
					<input type="hidden" app-data-id="hidden_language_id" name="language_id" value="" />
				</form>

				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/language/modify/active" method="POST" name="update-language-active-status-form">
					<div class="row">
						<div class="col-6 offset-md-2 form-check align-self-center form-switch form-check-reverse mb-3">
							<label class="form-check-label" for="update_language_active_status_checkbox">Active
								Status</label>
							<input class="form-check-input" type="checkbox" role="switch" name="updated_active_status"
								id="update_language_active_status_checkbox">
						</div>

						<div class="col-4">
							<button class="btn btn-outline-warning" type="submit">Update</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_language_id" name="language_id" value="" />
				</form>
				<hr class="border-danger" />

				<form @submit.prevent="sendUpdateCommand($event)" class="form text-center" action="/lib/process/language/modify/delete" method="POST" name="delete-language-form">
					<div class="row">
						<div class="col">
							<button class="btn btn-outline-danger" type="submit">Delete ?</button>
						</div>
					</div>

					<input type="hidden" app-data-id="hidden_language_id" name="language_id" value="" />
				</form>
			</div>
		</div>
		`,
	setup() {
		const selectedMaster = Vue.ref('');
		const dataTable = Vue.ref(null);
		const tableKey = Vue.ref(0);

		const updateTable = (event) => {
			tableKey.value += 1;
			fetchData(event.target.value);
		}

		const fetchData = async (masterType) => {
			try {
				const response = await fetch(
					`/lib/process/get/${masterType}`
					, {
						method: 'POST'
					}
				);
				const data = await response.json();
				loadDataToTable(masterType, data);
			} catch (error) {
				console.error('Error fetching data:', error);
			}
		};

		const loadDataToTable = (masterType, data) => {
			if ($.fn.DataTable.isDataTable('#theDataTable')) {
				$('#theDataTable').DataTable().clear();
				$('#theDataTable').DataTable().destroy();
			}

			let cols = {
				'author': [
					{ title: 'Name', data: 'name' },
					{ title: 'Biography', data: 'bio' },
					{ title: 'Date Created', data: 'uploaded_on' },
					{
						title: 'Action',
						defaultContent: `<button type='button' class='btn btn-outline-secondary open-author' data-bs-toggle='offcanvas' data-bs-target='#informationOffcanvas_author' aria-controls='informationOffcanvas_author'>Open</button>`,
					},
				],
				'publisher': [
					{ title: 'Name', data: 'name' },
					{ title: 'Description', data: 'desc' },
					{ title: 'Date Created', data: 'uploaded_on' },
					{
						title: 'Action',
						defaultContent: `<button type='button' class='btn btn-outline-secondary open-publisher' data-bs-toggle='offcanvas' data-bs-target='#informationOffcanvas_publisher' aria-controls='informationOffcanvas_publisher'>Open</button>`,
					},
				],
				'category': [
					{ title: 'Name', data: 'name' },
					{ title: 'Date Created', data: 'uploaded_on' },
					{
						title: 'Action',
						defaultContent: `<button type='button' class='btn btn-outline-secondary open-category' data-bs-toggle='offcanvas' data-bs-target='#informationOffcanvas_category' aria-controls='informationOffcanvas_category'>Open</button>`,
					},
				],
				'genre': [
					{ title: 'Name', data: 'name' },
					{ title: 'Date Created', data: 'uploaded_on' },
					{
						title: 'Action',
						defaultContent: `<button type='button' class='btn btn-outline-secondary open-genre' data-bs-toggle='offcanvas' data-bs-target='#informationOffcanvas_genre' aria-controls='informationOffcanvas_genre'>Open</button>`,
					},
				],
				'language': [
					{ title: 'Name', data: 'name' },
					{ title: 'Date Created', data: 'uploaded_on' },
					{
						title: 'Action',
						defaultContent: `<button type='button' class='btn btn-outline-secondary open-language' data-bs-toggle='offcanvas' data-bs-target='#informationOffcanvas_language' aria-controls='informationOffcanvas_language'>Open</button>`,
					},
				],
			}

			if (data.status === 'ok') {
				$('#theDataTable').DataTable({
					caption: `For: ${masterType.charAt(0).toUpperCase() + masterType.slice(1)}`,
					retrieve: true,
					columnDefs: [
						{
							targets: -1,
							searchable: false,
							orderable: false,
						},
					],
					columns: cols[masterType],
					data: data.data,
					rowId: (row) => masterType == 'language' ? row[`lang_id`] : row[`${masterType}_id`],
					rowCallback: (row, data) => {
						$(row).addClass(data.is_active == 0 ? 'table-warning' : 'table-success');
					},
				});
			}
		};

		const fetchDataFromController = async (masterType) => {
			try {
				const response = await fetch(`/lib/process/get/${masterType}`, { method: 'POST' });
				const data = await response.json();
				loadDataToTable(masterType, data);
			} catch (error) {
				console.error('Error fetching data:', error);
			}
		};

		const openSidePanel = (event) => {
			const authorButton = event.target.closest('.open-author');
			if (authorButton) {
				document.querySelectorAll("input[app-data-id='hidden_author_id']").forEach(element => {
					element.setAttribute("value", authorButton.closest('tr').id);
				});

				const isActive_author = authorButton.closest('tr').classList[0] == 'table-success';
				document.getElementById("update_author_active_status_checkbox").checked = isActive_author;
			}

			const publisherButton = event.target.closest('.open-publisher');
			if (publisherButton) {
				document.querySelectorAll("input[app-data-id='hidden_publisher_id']").forEach(element => {
					element.setAttribute("value", publisherButton.closest('tr').id);
				});

				const isActive_publisher = publisherButton.closest('tr').classList[0] == 'table-success';
				document.getElementById("update_publisher_active_status_checkbox").checked = isActive_publisher;
			}

			const categoryButton = event.target.closest('.open-category');
			if (categoryButton) {
				document.querySelectorAll("input[app-data-id='hidden_category_id']").forEach(element => {
					element.setAttribute("value", categoryButton.closest('tr').id);
				});

				const isActive_category = categoryButton.closest('tr').classList[0] == 'table-success';
				document.getElementById("update_category_active_status_checkbox").checked = isActive_category;
			}

			const genreButton = event.target.closest('.open-genre');
			if (genreButton) {
				document.querySelectorAll("input[app-data-id='hidden_genre_id']").forEach(element => {
					element.setAttribute("value", genreButton.closest('tr').id);
				});

				const isActive_genre = genreButton.closest('tr').classList[0] == 'table-success';
				document.getElementById("update_genre_active_status_checkbox").checked = isActive_genre;
			}

			const languageButton = event.target.closest('.open-language');
			if (languageButton) {
				document.querySelectorAll("input[app-data-id='hidden_language_id']").forEach(element => {
					element.setAttribute("value", languageButton.closest('tr').id);
				});

				const isActive_language = languageButton.closest('tr').classList[0] == 'table-success';
				document.getElementById("update_language_active_status_checkbox").checked = isActive_language;
			}
		};

		const sendUpdateCommand = (event) => {
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
						fetchDataFromController(data['last_master'])
					});
			} catch (error) {
				console.error('Error fetching data:', error);
			}
		}

		return {
			tableKey, selectedMaster, dataTable, updateTable, fetchData, fetchDataFromController,
			openSidePanel, sendUpdateCommand
		};
	},
};
