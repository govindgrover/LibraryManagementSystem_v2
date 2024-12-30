export const ViewBookDetails = {
	template: `
		<div>
		<h1 class="mb-5">@{ bookDetails.title }</h1>

		<div class="card mb-5">
			<div class="card-header text-center">
			Book Details
			</div>

			<div class="card-body p-5">
			<div class="">
				<img
				:src="getCompleteCILink(bookDetails.cover_image)"
				:alt="bookDetails.title"
				class="img-thumbnail rounded mx-auto d-block"
				width="300px"
				height="400px"
				style="border-color: #A9DFBF;"
				/>
			</div>

			<h5 class="card-title text-center my-4">
				<span class="badge text-bg-light">@{ bookDetails.language }</span>
			</h5>
			<h4 class="card-title text-center my-4">
				<span v-for="(author, authorIndex) in bookDetails.authors" :key="authorIndex" class="badge text-bg-success mx-2">@{ author }</span>
			</h4>

			<div class="card-text m-3">
				<div class="row">
				<div class="col-md-2"><b>Description</b></div>
				<div class="col-md-10">@{ bookDetails.description }</div>
				</div>
			</div>

			<div class="card-text m-3">
				<div class="row">
				<div class="col-md-2"><b>ISBN</b></div>
				<div class="col-md-10">@{ bookDetails.isbn }</div>
				</div>
			</div>

			<div class="card-text m-3">
				<div class="row">
				<div class="col-md-2 my-2"><b>Publisher</b></div>
				<div class="col-md-4">@{ bookDetails.publisher }</div>
				<div class="col-md-2 my-2"><b>Publication Date</b></div>
				<div class="col-md-4">@{ bookDetails.publication_date }</div>
				</div>
			</div>

			<div class="card-text m-3">
				<div class="row">
				<div class="col-md-2 my-2"><b>Categories</b></div>
				<div class="col-md-4">
					<span v-for="(category, categoryIndex) in bookDetails.category" :key="categoryIndex" class="badge rounded-pill text-bg-info mx-1">@{ category }</span>
				</div>
				<div class="col-md-2 my-2"><b>Genres</b></div>
				<div class="col-md-4">
					<span v-for="(genre, genreIndex) in bookDetails.genre" :key="genreIndex" class="badge rounded-pill text-bg-warning mx-1">@{ genre }</span>
				</div>
				</div>
			</div>

			<div class="card-text m-3">
				<div class="row">
					<div class="col-md-2 my-2"><b>Feedbacks</b></div>
						<div class="col-md-10">
							<span v-for="(feedback, feedbackIndex) in bookDetails.feedbacks" :key="feedbackIndex" class="my-1">
								<span class="badge rounded-pill m-2" style="background-color: goldenrod;">
									@{ feedback.rating }
								</span>
								@{ feedback.feedback }
								<br />
							</span>
						</div>
					</div>
				</div>

			<div class="card-text m-3">
				<div class="row">
				<div class="col-md-6 my-2">
					<form @submit.prevent="raiseIssueRequest($event)" class="d-grid gap-2" name="raise-book-issue-request-form" action="/book/issue" method="POST">
					<input type="hidden" name="requested_book_id" :value="bookDetails.book_id" required />
					<button class="btn btn-block btn-outline-primary" type="submit">Issue or Buy (₹@{ bookDetails.price }) ?</button>
					</form>
				</div>
				<div class="col-md-6 my-2 d-grid gap-2">
					<button class="btn btn-outline-info" type="button" data-bs-toggle="modal" data-bs-target="#give_feedback_modal">Give Feedback</button>
				</div>
				</div>
			</div>
			</div>
		</div>

		<!-- Feedback modal -->
		<div class="modal fade" id="give_feedback_modal" tabindex="-1" aria-labelledby="give_feedback_modal_label" aria-hidden="true">
			<div class="modal-dialog">
			<form @submit.prevent="giveFeedback($event)" action="/book/feedback" name="book-feedback-form" method="POST">
				<div class="modal-content">
				<div class="modal-header">
					<h5 class="modal-title" id="give_feedback_modal_label">Give Feedback</h5>
					<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
				</div>
				<div class="modal-body">
					<div class="input-group mb-3">
					<label class="input-group-text" for="feedback">Feedback</label>
					<input type="text" class="form-control" id="feedback" name="feedback" required />
					</div>
					<div class="input-group mb-3">
					<label class="input-group-text" for="rating">Rating</label>
					<input type="number" class="form-control" id="rating" name="rating" min="1" max="5" step="1" required />
					</div>
				</div>
				<input type="hidden" name="requested_book_id" :value="bookDetails.book_id" required />
				<div class="modal-footer">
					<button type="button" class="btn btn-outline-danger" data-bs-dismiss="modal">Cancel</button>
					<button type="submit" class="btn btn-outline-success">Submit</button>
				</div>
				</div>
			</form>
			</div>
		</div>
		</div>
	`,

	setup() {
		const bookDetails = Vue.ref({
			title: '',
			cover_image: '',
			language: '',
			authors: [],
			description: '',
			isbn: '',
			publisher: '',
			publication_date: '',
			category: [],
			genre: [],
			feedbacks: [],
			price: 0,
			book_id: 0
		});

		const route = VueRouter.useRoute();
		const bookId = route.params.id;

		const fetchBookDetails = async () => {
			try {
				const response = await fetch(`/book/get/details/${bookId}`, { method: 'POST' });
				const result = await response.json();

				bookDetails.value = result || {};
			} catch (error) {
				console.error('Error fetching book details:', error);
			}
		};

		const giveFeedback = async (event) => {
			const form = event.target
			const formData = new FormData(form)

			try {
				const response = await fetch('/book/feedback', {
					method: 'POST',
					// headers: { 'Content-Type': 'application/json' },
					body: formData
				});

				const result = await response.json()

				if (response.ok) {
					alert(result.msg)
					if (result.status == 'ok') {
						document.querySelector('#give_feedback_modal .btn-close').click();
					}
				} else {
					alert('Failed to submit feedback.');
				}
			} catch (error) {
				console.error('Error submitting feedback:', error);
			}
		};

		const raiseIssueRequest = async (event) => {
			const form = event.target
			const formData = new FormData(form)

			try {
				const response = await fetch('/book/issue', {
					method: 'POST',
					body: formData
				});
				const result = await response.json()

				console.log(result)

				if (response.ok) {
					alert(result.msg)
				} else {
					alert('Failed to submit issue/purchase request.');
				}
			} catch (error) {
				console.error('Error submitting issue/purchase request:', error);
			}
		};

		const getCompleteCILink = (link) => `http://127.0.0.1:8000/static/ci/${link}`

		Vue.onBeforeMount(() => {
			fetchBookDetails();
		});

		return {
			bookDetails,
			getCompleteCILink,
			giveFeedback,
			raiseIssueRequest,
		};
	}
}