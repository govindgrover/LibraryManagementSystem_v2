import { STATE } from './../../state.js'

export const Login = {
	template: `
		<div class="row vertical-center">
			<div class="col text-center">
				<div class="col m-4 text-primary">
					<span class="mx-3">
						<i class="bi bi-box-arrow-in-right fs-1"></i>
					</span>
					<span class="display-6">Login</span>
				</div>

				<form class="form p-2" @submit.prevent="login">
					<div class="row">
						<div class="col-sm-4 offset-sm-4">
							<div class="form-floating mb-3">
								<input type="email" id="_email" class="form-control" v-model="email"
									placeholder="Enter Email Address" required autofocus />
								<label for="_email">Email</label>
							</div>
						</div>
					</div>

					<div class="row">
						<div class="col-sm-4 offset-sm-4">
							<div class="form-floating mb-3">
								<input type="password" id="_pass" class="form-control" v-model="password"
									placeholder="Password" required />
								<label for="_pass">Password</label>
							</div>
						</div>
					</div>

					<div class="row">
						<div class="d-grid col-sm-4 offset-sm-4">
							<button type="submit" id="login-button" class="btn btn-primary">Login</button>
						</div>
					</div>
				</form>

				<div class="row my-4">
					<div class="d-grid col-sm-4 offset-sm-4">
						<router-link to="/register" class="icon-link icon-link-hover d-inline-block" style="text-decoration: none;">
							<i class="bi bi-caret-right-fill" aria-hidden="true"></i> Don't have an account? Register
						</router-link>
					</div>
				</div>
			</div>
		</div>
	`,
	setup() {
		let email = Vue.ref('')
		let password = Vue.ref('')
		// let toastRef = Vue.ref('toastRef'); 

		function login() {
			fetch('/acc/process/login', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					email: email.value,
					password: password.value,
				}),
			})
				.then(response => response.json())
				.then(data => {
					// toastRef.BSToastComponent.showToast(data['msg'], 'Success');

					if (data['status'] === 'ok') {
						alert('Logged In')

						for (let key in data['data']) {
							localStorage.setItem(key, data['data'][key])
						}

						STATE.isAuthenticated = true;

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

		return {
			email, password, login
		}
	},
}