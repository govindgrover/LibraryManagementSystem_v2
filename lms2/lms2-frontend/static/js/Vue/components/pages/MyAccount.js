import { router } from "../../router.js";

export const MyAccount = {
	template: `
			<div class="container pt-5">
				<h1 class="mb-5">My Account</h1>
		
				<div class="card text-center mb-5">
				<div class="card-header">
					Account Details
				</div>
		
				<div class="card-body">
					<div>
					<img
						:src="profilePictureUrl"
						alt="Profile Picture"
						class="img-thumbnail rounded mx-auto d-block"
						width="256px"
						height="256px"
						style="border-color: #A9DFBF; cursor: pointer;"
						@click="openProfilePictureModal"
					/>
					<span class="fs-6 text-secondary mt-3">Click image to update</span>
					</div>
		
					<h4 class="card-title my-4">
					Hello, @{ user.name }
					</h4>
		
					<div class="card-text m-5">
					<form @submit.prevent="updateNameFunc" name="update-name-form">
						<div class="row">
						<div class="input-group mb-3">
							<label for="updateName" class="col-sm-2 col-form-label">Name</label>
							<div class="col-sm-8">
							<input
								type="text"
								class="form-control"
								name="updatedName"
								id="updatedName"
							/>
							</div>
							<div class="col-sm-2">
							<button class="btn btn-outline-warning" type="submit">
								Update
							</button>
							</div>
						</div>
						</div>
					</form>
		
					<div class="mb-3 row" v-for="(value, label) in userDetails" :key="label">
						<label :for="'static' + label" class="col-sm-2 col-form-label">@{ label }</label>
						<div class="col-sm-10">
						<input
							type="text"
							readonly
							class="form-control-plaintext"
							:id="'static' + label"
							:value="value"
						/>
						</div>
					</div>
		
					<form @submit.prevent="updatePassFunc" name="update-pass-form">
						<div class="row">
						<div class="input-group mb-3">
							<label for="updatePassword" class="col-sm-2 col-form-label">Password</label>
							<div class="col-sm-8">
							<input
								type="password"
								class="form-control"
								id="updatePassword"
								name="updatedPassword"
							/>
							</div>
							<div class="col-sm-2">
							<button class="btn btn-outline-warning" type="submit">
								Update
							</button>
							</div>
						</div>
						</div>
					</form>
		
					<form @submit.prevent="updateReportFormatFunc" name="update-report-form">
						<div class="row">
						<div class="input-group mb-3">
							<label for="updateReportFormat" class="col-sm-2 col-form-label">
							Monthly Report Format
							</label>
							<div class="col-sm-8 d-flex justify-content-center align-items-center">
							<label class="form-check-label ms-2" for="reportFormatHTML">HTML</label>
							<div class="form-check form-switch">
								<input
									v-if="user.pdfReportSetting == true"
								class="form-check-input"
								type="checkbox"
								role="switch"
								id="update-reportFormat"
								name="updated_report_value"
								checked
								/>
								<input
									v-if="user.pdfReportSetting == false"
								class="form-check-input"
								type="checkbox"
								role="switch"
								name="updated_report_value"
								id="update-reportFormat"
								/>
							</div>
							<label class="form-check-label me-2" for="reportFormatPDF">PDF</label>
							</div>
							<div class="col-sm-2">
							<button class="btn btn-outline-warning" type="submit">
								Update
							</button>
							</div>
						</div>
						</div>
					</form>
					</div>
		
					<button class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#account_delete_modal">
					Delete Account
					</button>
				</div>
		
				<div class="card-footer text-body-secondary">
					<i>Account Status: <b>Active</b></i>
				</div>
				</div>
			</div>

			<div class="modal fade" id="account_delete_modal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="account_delete_modal_Label" aria-hidden="true">
				<div class="modal-dialog modal-dialog-centered">
					<div class="modal-content">
						<div class="modal-header">
							<h1 class="modal-title fs-5" id="account_delete_modal_Label">Confirm Account Deletion</h1>
							<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
						</div>
						<div class="modal-body">
							The action could not be undone.
						</div>
						<div class="modal-footer">
							<form @submit.prevent="deleteAccFunc" name="account-delete-form">
								<button type="button" class="btn btn-outline-success" data-bs-dismiss="modal">Cancel</button>
								<button type="submit" id="account-delete-button" class="btn btn-outline-danger">Delete ?</button>
							</form>
						</div>
					</div>
				</div>
			</div>

			<div class="modal fade" id="update_account_pp_modal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1"aria-labelledby="update_account_pp_modal_Label" aria-hidden="true">
				<div class="modal-dialog modal-dialog-centered">
					<div class="modal-content">
						<div class="modal-header">
							<h1 class="modal-title fs-5" id="update_account_pp_modal_Label">Update Profile Picture</h1>
							<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
						</div>
						<form @submit.prevent="updatePPFunc" name="acc-update-pp" enctype="multipart/form-data">
							<div class="modal-body">
								<div class="input-group mb-3">
									<input type="file" class="form-control" id="update-pp-input" name="new_pp">
									<label class="input-group-text" for="update-pp-input">To upload</label>
								</div>
							</div>

							<div class="modal-footer">
								<button type="button" class="btn btn-outline-danger" data-bs-dismiss="modal">Cancel</button>
								<button type="submit" id="acc-update-pp-button" class="btn btn-outline-info">Change ?</button>
							</div>
						</form>
					</div>
				</div>
			</div>
	`,
	data() {
		return {
			// user: {
			// 	name: localStorage.getItem('name'),
			// 	role: localStorage.getItem('role'),
			// 	email: localStorage.getItem('email'),
			// 	dob: localStorage.getItem('dob'),
			// 	gender: localStorage.getItem('gender'),
			// 	profilePicture: localStorage.getItem('profile_picture'),
			// },
			updatedName: '',
			updatedPassword: '',
			newProfilePicture: null,
		};
	},
	computed: {
		profilePictureUrl() {
			return this.user.profilePicture;
		},
		userDetails() {
			return {
				'User Role': this.user.role,
				Email: this.user.email,
				'Date of Birth': this.user.dob,
				Gender: this.user.gender,
			};
		},
	},
	setup() {
		let user = Vue.reactive({
			name: localStorage.getItem('name'),
			role: localStorage.getItem('role'),
			email: localStorage.getItem('email'),
			dob: localStorage.getItem('dob'),
			gender: localStorage.getItem('gender'),
			profilePicture: localStorage.getItem('profile_picture'),
			pdfReportSetting: localStorage.getItem('pdf_report_setting'),
		});

		function updateNameFunc() {
			let f = new FormData(document.forms['update-name-form']);

			fetch('/acc/update/name', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					updated_name: f.get('updatedName')
				}),
			})
				.then(response => response.json())
				.then(data => {
					// toastRef.BSToastComponent.showToast(data['msg'], 'Success');

					if (data['status'] == 'ok') {
						localStorage.clear()		// cleared old user-information

						for (let key in data['data']) {
							localStorage.setItem(key, data['data'][key])
						}

						Object.assign(user, data['data']);
					} else {
						alert(data['msg'])
					}
				})
				.catch((error) => {
					console.log(error)
					// toastRef.BSToastComponent.showToast(data['msg'], 'Error');
				});
		}

		function updatePassFunc() {
			let f = new FormData(document.forms['update-pass-form']);

			fetch('/acc/update/password', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					updated_password: f.get('updatedPassword')
				}),
			})
				.then(response => response.json())
				.then(data => {
					// toastRef.BSToastComponent.showToast(data['msg'], 'Success');

					if (data['status'] == 'ok') {
						alert('Password Updated!!')
					} else {
						alert(data['msg'])
					}
				})
				.catch((error) => {
					console.log(error)
					// toastRef.BSToastComponent.showToast(data['msg'], 'Error');
				});
		}

		function updateReportFormatFunc() {
			let f = new FormData(document.forms['update-report-form']);

			fetch('/acc/update/monthly-report-format', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					updateReportFormat: f.get('updated_report_value')
				}),
			})
				.then(response => response.json())
				.then(data => {
					// toastRef.BSToastComponent.showToast(data['msg'], 'Success');

					if (data['status'] == 'ok') {
						localStorage.clear()		// cleared old user-information

						for (let key in data['data']) {
							localStorage.setItem(key, data['data'][key])
						}

						Object.assign(user, data['data']);
						alert("Done")
					} else {
						alert(data['msg'])
					}
				})
				.catch((error) => {
					console.log(error)
					// toastRef.BSToastComponent.showToast(data['msg'], 'Error');
				});
		}

		function deleteAccFunc() {
			let f = new FormData(document.forms['account-delete-form']);

			fetch('/acc/process/account-delete', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
				}),
			})
				.then(response => response.json())
				.then(data => {
					// toastRef.BSToastComponent.showToast(data['msg'], 'Success');

					if (data['status'] == 'ok') {
						localStorage.clear()		// cleared old user-information
						window.location.href = '/'
					} else {
						alert(data['msg'])
					}
				})
				.catch((error) => {
					console.log(error)
					// toastRef.BSToastComponent.showToast(data['msg'], 'Error');
				});
		}

		function updatePPFunc() {
			let f = new FormData(document.forms['acc-update-pp']);

			fetch('/acc/update/pp', {
				method: 'POST',
				// headers: {
				// 	'Content-Type': 'application/json',
				// },
				body: f,
			})
				.then(response => response.json())
				.then(data => {
					// toastRef.BSToastComponent.showToast(data['msg'], 'Success');

					if (data['status'] == 'ok') {
						localStorage.clear()		// cleared old user-information

						for (let key in data['data']) {
							localStorage.setItem(key, data['data'][key])
						}

						Object.assign(user, data['data']);
						alert("Picture Updated!");
					} else {
						alert(data['msg'])
					}
				})
				.catch((error) => {
					console.log(error)
					// toastRef.BSToastComponent.showToast(data['msg'], 'Error');
				});
		}

		function openProfilePictureModal() {
			let accUpdateModal = document.getElementById("update_account_pp_modal");

			const modal = new bootstrap.Modal('#update_account_pp_modal', {
				//
			})

			modal.show(accUpdateModal);
		}

		return {
			user, updateNameFunc, updatePassFunc, updateReportFormatFunc, updatePPFunc, deleteAccFunc, openProfilePictureModal
		}
	},
};
