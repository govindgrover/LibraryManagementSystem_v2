export const BrowseBooks = {
	template: `
			<div>
				<h1 class="mb-5">Browse Books</h1>
			
				<h4 v-if="dataToBrowse.length === 0" class="text-center text-warning">
					Currently there are no books to display!
				</h4>
			
				<div v-if="dataToBrowse.length > 0" class="row row-cols-1 row-cols-md-3 g-4 mb-5">
					<div v-for="(book, index) in dataToBrowse" :key="index" class="col">
					<div class="card h-100">
						<img 
						:src="getCompleteCILink(book.cover_image)"
						class="card-img-top" 
						:alt="book.title"
						/>
						<div class="card-body">
						<h5 class="card-title">
							<span class="badge text-bg-light">@{ book.language }</span>
							@{ book.title }
						</h5>
						<p class="card-text">
							<span v-for="(author, authorIndex) in book.authors" :key="authorIndex" class="badge text-bg-success mx-2">@{ author }</span>
						</p>
						<p class="card-text">@{ book.description }</p>
						<p class="card-text"><strong>ISBN:</strong> @{ book.isbn }</p>
						<p class="card-text"><strong>Edition:</strong> @{ book.edition }</p>
						<p class="card-text"><strong>Price:</strong> ₹@{ book.price }</p>
						<p class="card-text"><strong>Publication Date:</strong> @{ book.publication_date }</p>
						<p class="card-text">
							<span v-for="(category, categoryIndex) in book.category" :key="categoryIndex" class="badge rounded-pill text-bg-info mx-2">@{ category }</span>
						</p>
						<p class="card-text">
							<span v-for="(genre, genreIndex) in book.genre" :key="genreIndex" class="badge rounded-pill text-bg-warning mx-2">@{ genre }</span>
						</p>
						<router-link :to="getBookDetailsLink(book.book_id)" class="btn btn-primary">View Details</router-link>
						</div>
					</div>
					</div>
				</div>
			</div>
`,

	setup() {
		const dataToBrowse = Vue.ref([]);

		const fetchBooks = async () => {
			try {
				const response = await fetch('/lib/process/get/books', { method: 'POST' });
				const result = await response.json();
				dataToBrowse.value = result.data || [];
			} catch (error) {
				console.error('Error fetching books:', error);
			}
		};

		const getCompleteCILink = (link) =>  `http://127.0.0.1:8000/static/ci/${link}`
		const getBookDetailsLink = (link) =>  `/browse/details/${link}`


		Vue.onBeforeMount(() => {
			fetchBooks();
		});

		return {
			dataToBrowse,
			getCompleteCILink,
			getBookDetailsLink,
		};
	}
}	