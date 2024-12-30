export const MyLibrary = {
	template: `
		<div>
		<h1 class="mb-5">@{ user_name }'s Library</h1>

		<div v-if="myLibrary.length === 0">
			<h4 class="text-center text-warning">
			Currently there are no books to display!
			</h4>
		</div>

		<div class="row row-cols-1 row-cols-md-2 row-cols-lg-2 g-4 mb-5" v-else>
			<div v-for="(book, index) in myLibrary" :key="index" class="col">
			<div class="card h-100">
				<img :src="getCompleteCILink(book.cover_image)" class="card-img-top" :alt="book.title">
				<div class="card-body">
				<h5 class="card-title">
					@{ book.book_title }
				</h5>

				<div v-if="book.is_purchased">
					<div>
					<p class="card-text text-success">
						<i class="bi bi-cart-check-fill"></i>&nbsp;Purchased
					</p>
					</div>

					<hr class="text-info" />

					<div class="d-grid gap-2">
					<a :href="'/book/read/' + book.content_access_token" class="btn btn-outline-success" target="_blank">Read Now !</a>
					</div>
				</div>
				<div v-else>
					<p class="card-text">
					<div class="text-primary">
						<strong>Due Date: @{ book.date_of_return }</strong>
						<br />
						Book issued from: <em>@{ book.issued_by_name }</em>
					</div>

					<hr class="text-info" />

					<form @submit.prevent="returnBook(book.book_id)">
						<div class="d-grid gap-2">
						<div class="btn-group" role="group">
							<button type="submit" class="btn btn-outline-danger">Return ?</button>
							<a :href="'/book/read/' + book.content_access_token" class="btn btn-outline-primary" target="_blank">Read Now !</a>
						</div>
						</div>
					</form>
					</p>
				</div>

				<hr class="text-primary" />

				<h5 class="card-title mb-3">
					<span class="badge text-bg-light">@{ book.language }</span>
					@{ book.title }
				</h5>

				<p class="card-text">
					<span v-for="(author, authorIndex) in book.authors" :key="authorIndex" class="badge text-bg-success mx-1">
					@{ author }
					</span>
				</p>
				<p class="card-text">@{ book.description }</p>
				<p class="card-text"><strong>ISBN:</strong> @{ book.isbn }</p>
				<p class="card-text"><strong>Edition:</strong> @{ book.edition }</p>
				<p class="card-text"><strong>Publication Date:</strong> @{ book.publication_date }</p>
				<p class="card-text">
					<span v-for="(category, categoryIndex) in book.category" :key="categoryIndex" class="badge rounded-pill text-bg-info mx-1">
					@{ category }
					</span>
				</p>
				<p class="card-text">
					<span v-for="(genre, genreIndex) in book.genre" :key="genreIndex" class="badge rounded-pill text-bg-warning mx-1">
					@{ genre }
					</span>
				</p>
				</div>
			</div>
			</div>
		</div>
		</div>
	`,

	setup() {
		const user_name = Vue.ref(localStorage.getItem('name'))
		const myLibrary = Vue.ref([]);

		const fetchMyLibrary = async () => {
			try {
				const response = await fetch('/user/get/mylibrary', {
					method: 'POST'
				});

				const result = await response.json();
				myLibrary.value = result || [];

			} catch (error) {
				console.error('Error fetching library:', error);
			}
		};

		const getCompleteCILink = (link) =>  `http://127.0.0.1:8000/static/ci/${link}`

		const returnBook = async (bookId) => {
			try {
				const response = await fetch('/user/process/return', {
					method: 'POST',
					headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
					body: new URLSearchParams({ book_id: bookId })
				});
				if (response.ok) {
					alert('Book returned successfully!');
					fetchMyLibrary();
				} else {
					alert('Failed to return the book.');
				}
			} catch (error) {
				console.error('Error returning book:', error);
			}
		};

		Vue.onBeforeMount(() => {
			fetchMyLibrary();
		});

		return {
			myLibrary,
			user_name,
			getCompleteCILink,
			returnBook
		};
	}
}