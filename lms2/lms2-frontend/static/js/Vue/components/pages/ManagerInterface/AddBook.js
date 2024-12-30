export const AddBook = {
	template: `
	<div class="container pt-5">
		<h1 class="mb-3">Add new Book</h1>
		<form @submit.prevent="submitBook($event)" class="row g-3 mb-2" action="/lib/process/books/add" name="add-book-form" method="POST" enctype="multipart/form-data">
		<div class="col-md-6">
			<label for="title" class="form-label">Title</label>
			<input type="text" class="form-control" id="title" name="title" autofocus />
		</div>
		<div class="col-md-6">
			<label for="isbn" class="form-label">ISBN</label>
			<input type="text" class="form-control" id="isbn" name="isbn" />
		</div>
		<div class="col-12">
			<label for="book_description" class="form-label">Description</label>
			<textarea class="form-control" id="book_description" name="book_description"></textarea>
		</div>
		<div class="col-md-4">
			<label for="edition" class="form-label">Edition</label>
			<input type="text" class="form-control" id="edition" name="edition" />
		</div>
		<div class="col-md-5">
			<label for="pub_date" class="form-label">Publication Date</label>
			<input type="date" class="form-control" id="pub_date" name="pub_date" />
		</div>
		<div class="col-md-3">
			<label for="price" class="form-label">Price (in Rs.)</label>
			<input type="number" class="form-control" id="price" name="price" value="0.0" />
		</div>
		<div class="col-md-6">
			<label for="publisher_id" class="form-label">Select Publisher</label>
			<select id="publisher_id" class="form-select" name="publisher_id">
			<option selected>Choose...</option>
			<option v-for="publisher in publishers" :value="publisher.publisher_id" :key="publisher.publisher_id">
				@{ publisher.name }
			</option>
			</select>
		</div>
		<div class="col-md-6">
			<label for="language_id" class="form-label">Select Language</label>
			<select id="language_id" class="form-select" name="language_id">
			<option selected>Choose...</option>
			<option v-for="language in languages" :value="language.lang_id" :key="language.lang_id">
				@{ language.name}
			</option>
			</select>
		</div>
		<div class="col-md-4">
			<label for="author_ids" class="form-label">Select Author(s)</label>
			<select id="author_ids" class="form-select" name="author_ids" multiple>
			<option selected>Choose...</option>
			<option v-for="author in authors" :value="author.author_id" :key="author.author_id">
				@{ author.name}
			</option>
			</select>
		</div>
		<div class="col-md-4">
			<label for="category_ids" class="form-label">Select Category(ies)</label>
			<select id="category_ids" class="form-select" name="category_ids" multiple>
			<option selected>Choose...</option>
			<option v-for="category in categories" :value="category.category_id" :key="category.category_id">
				@{ category.name}
			</option>
			</select>
		</div>
		<div class="col-md-4">
			<label for="genre_ids" class="form-label">Select Genre(s)</label>
			<select id="genre_ids" class="form-select" name="genre_ids" multiple>
			<option selected>Choose...</option>
			<option v-for="genre in genres" :value="genre.genre_id" :key="genre.genre_id">
				@{ genre.name}
			</option>
			</select>
		</div>
		<div class="col-12">
			<label for="book_content" class="form-label">Select book's content to upload (single file)</label>
			<input class="form-control" type="file" id="book_content" name="book_content" />
		</div>
		<div class="col-12">
			<button type="submit" id="add-book-button" class="btn btn-primary btn-block">Proceed</button>
		</div>
		</form>
	</div>
	`,
	setup() {
		const publishers = Vue.ref([]);
		const languages = Vue.ref([]);
		const authors = Vue.ref([]);
		const categories = Vue.ref([]);
		const genres = Vue.ref([]);

		const fetchAuthors = async () => {
			try {
				const response = await fetch('/lib/process/get/author', { method: 'POST' });
				const data = await response.json();
				authors.value = data['data'];
			} catch (error) {
				console.error('Error fetching authors:', error);
			}
		};

		const fetchPublishers = async () => {
			try {
				const response = await fetch('/lib/process/get/publisher', { method: 'POST' });
				const data = await response.json();
				publishers.value = data['data'];
			} catch (error) {
				console.error('Error fetching publishers:', error);
			}
		};

		const fetchCategories = async () => {
			try {
				const response = await fetch('/lib/process/get/category', { method: 'POST' });
				const data = await response.json();
				categories.value = data['data'];
			} catch (error) {
				console.error('Error fetching categories:', error);
			}
		};

		const fetchGenres = async () => {
			try {
				const response = await fetch('/lib/process/get/genre', { method: 'POST' });
				const data = await response.json();
				genres.value = data['data'];
			} catch (error) {
				console.error('Error fetching genres:', error);
			}
		};

		const fetchLanguages = async () => {
			try {
				const response = await fetch('/lib/process/get/language', { method: 'POST' });
				const data = await response.json();
				languages.value = data['data'];
			} catch (error) {
				console.error('Error fetching languages:', error);
			}
		};

		const submitBook = async (event) => {
			event.preventDefault();

			const form = new FormData(event.target);

			try {
				const response = await fetch('/lib/process/books/add', {
					method: 'POST',
					body: form,
				});

				const result = await response.json();

				if (response.ok) {
					alert(result.msg);
					if (result.status == 'ok') {
						event.target.reset();
					}
				} else {
					alert('Failed to add book. Please try again.');
				}
			} catch (error) {
				console.error('Error submitting book:', error);
				alert('An error occurred. Please try again.');
			}
		};

		Vue.onBeforeMount(() => {
			fetchPublishers();
			fetchLanguages();
			fetchAuthors();
			fetchCategories();
			fetchGenres();
		});

		return {
			authors,
			publishers,
			categories,
			genres,
			languages,
			submitBook,
		};
	}
};
