export const AddMasters = {
	template: `
	<div class="container pt-5">
	<h1 class="mb-5">Add Master Record</h1>
	<div class="accordion" id="accordion-add-masters">

		<!-- add author -->
		<div class="accordion-item">
		<h2 class="accordion-header">
			<button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#addAuthor"
					aria-expanded="true" aria-controls="addAuthor">
			Add Author
			</button>
		</h2>
		<div id="addAuthor" class="accordion-collapse collapse show" data-bs-parent="#accordion-add-masters">
			<div class="accordion-body">
			<form class="form p-2" @submit.prevent="submitAuthor">
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<input type="text" id="_name" class="form-control" name="name" placeholder="Enter Author's Name" required />
					<label for="_name">Author's Name</label>
					</div>
				</div>
				</div>
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<input type="text" id="_bio" class="form-control" name="bio" placeholder="Enter Author's Bio" required />
					<label for="_bio">Author's Bio</label>
					</div>
				</div>
				</div>
				<div class="row">
				<div class="d-grid col-sm-4 offset-sm-4">
					<button type="submit" id="add-author-button" class="btn btn-block btn-success">Add Author</button>
				</div>
				</div>
			</form>
			</div>
		</div>
		</div>

		<!-- add publisher -->
		<div class="accordion-item">
		<h2 class="accordion-header">
			<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
					data-bs-target="#addPublisher" aria-expanded="false" aria-controls="addPublisher">
			Add Publisher
			</button>
		</h2>
		<div id="addPublisher" class="accordion-collapse collapse" data-bs-parent="#accordion-add-masters">
			<div class="accordion-body">
			<form class="form p-2" @submit.prevent="submitPublisher">
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<input type="text" id="_name" class="form-control" name="name" placeholder="Enter Publisher's Name" required />
					<label for="_name">Publisher's Name</label>
					</div>
				</div>
				</div>
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<input type="text" id="_desc" class="form-control" name="description" placeholder="Enter Publisher's Description" required />
					<label for="_desc">Publisher's Description</label>
					</div>
				</div>
				</div>
				<div class="row">
				<div class="d-grid col-sm-4 offset-sm-4">
					<button type="submit" id="add-publisher-button" class="btn btn-block btn-success">Add Publisher</button>
				</div>
				</div>
			</form>
			</div>
		</div>
		</div>

		<!-- add category -->
		<div class="accordion-item">
		<h2 class="accordion-header">
			<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
					data-bs-target="#addCategory" aria-expanded="false" aria-controls="addCategory">
			Add Category
			</button>
		</h2>
		<div id="addCategory" class="accordion-collapse collapse" data-bs-parent="#accordion-add-masters">
			<div class="accordion-body">
			<form class="form p-2" @submit.prevent="submitCategory">
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<input type="text" id="_name" class="form-control" name="name" placeholder="Enter Category's Name" required />
					<label for="_name">Category's Name</label>
					</div>
				</div>
				</div>
				<div class="row">
				<div class="d-grid col-sm-4 offset-sm-4">
					<button type="submit" id="add-category-button" class="btn btn-block btn-success">Add Category</button>
				</div>
				</div>
			</form>
			</div>
		</div>
		</div>

		<!-- add genre -->
		<div class="accordion-item">
		<h2 class="accordion-header">
			<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
					data-bs-target="#addGenre" aria-expanded="false" aria-controls="addGenre">
			Add Genre
			</button>
		</h2>
		<div id="addGenre" class="accordion-collapse collapse" data-bs-parent="#accordion-add-masters">
			<div class="accordion-body">
			<form class="form p-2" @submit.prevent="submitGenre">
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<input type="text" id="_name" class="form-control" name="name" placeholder="Enter Genre's Name" required />
					<label for="_name">Genre's Name</label>
					</div>
				</div>
				</div>
				<div class="row">
				<div class="d-grid col-sm-4 offset-sm-4">
					<button type="submit" id="add-genre-button" class="btn btn-block btn-success">Add Genre</button>
				</div>
				</div>
			</form>
			</div>
		</div>
		</div>

		<!-- add language -->
		<div class="accordion-item">
		<h2 class="accordion-header">
			<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
					data-bs-target="#addLanguage" aria-expanded="false" aria-controls="addLanguage">
			Add Language
			</button>
		</h2>
		<div id="addLanguage" class="accordion-collapse collapse" data-bs-parent="#accordion-add-masters">
			<div class="accordion-body">
			<form class="form p-2" @submit.prevent="submitLanguage">
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<input type="text" id="_name" class="form-control" name="name" placeholder="Enter Language's Name" required />
					<label for="_name">Language's Name</label>
					</div>
				</div>
				</div>
				<div class="row">
				<div class="d-grid col-sm-4 offset-sm-4">
					<button type="submit" id="add-language-button" class="btn btn-block btn-success">Add Language</button>
				</div>
				</div>
			</form>
			</div>
		</div>
		</div>

	</div>
	</div>
`,
setup() {
		const submitAuthor = async (event) => {
			const form = new FormData(event.target);

			try {
				const response = await fetch('/lib/process/author/add', {
					method: 'POST',
					body: form,
				});
				const result = await response.json();

				if (response.ok) {
					alert(result.msg)

					if (result.status == 'ok') {
						event.target.reset();
					}
				} else {
					alert('Failed to add author. Please try again.');
				}
			} catch (error) {
				console.error('Error submitting author:', error);
				alert('An error occurred. Please try again.');
			}
		};

		const submitPublisher = async (event) => {
			const form = new FormData(event.target);

			try {
				const response = await fetch('/lib/process/publisher/add', {
					method: 'POST',
					body: form,
				});

				const result = await response.json();

				if (response.ok) {
					alert(result.msg)

					if (result.status == 'ok') {
						event.target.reset();
					}
				} else {
					alert('Failed to add publisher. Please try again.');
				}
			} catch (error) {
				console.error('Error submitting publisher:', error);
				alert('An error occurred. Please try again.');
			}
		};

		const submitCategory = async (event) => {
			const form = new FormData(event.target);

			try {
				const response = await fetch('/lib/process/category/add', {
					method: 'POST',
					body: form,
				});

				const result = await response.json();

				if (response.ok) {
					alert(result.msg)

					if (result.status == 'ok') {
						event.target.reset();
					}
				} else {
					alert('Failed to add category. Please try again.');
				}
			} catch (error) {
				console.error('Error submitting category:', error);
				alert('An error occurred. Please try again.');
			}
		};

		const submitGenre = async (event) => {
			const form = new FormData(event.target);

			try {
				const response = await fetch('/lib/process/genre/add', {
					method: 'POST',
					body: form,
				});

				const result = await response.json();

				if (response.ok) {
					alert(result.msg)

					if (result.status == 'ok') {
						event.target.reset();
					}
				} else {
					alert('Failed to add genre. Please try again.');
				}
			} catch (error) {
				console.error('Error submitting genre:', error);
				alert('An error occurred. Please try again.');
			}
		};

		const submitLanguage = async (event) => {
			const form = new FormData(event.target);

			try {
				const response = await fetch('/lib/process/language/add', {
					method: 'POST',
					body: form,
				});

				const result = await response.json();

				if (response.ok) {
					alert(result.msg)

					if (result.status == 'ok') {
						event.target.reset();
					}
				} else {
					alert('Failed to add language. Please try again.');
				}
			} catch (error) {
				console.error('Error submitting language:', error);
				alert('An error occurred. Please try again.');
			}
		};

		return {
			submitAuthor,
			submitPublisher,
			submitCategory,
			submitGenre,
			submitLanguage,
		};
	},
};