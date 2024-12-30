export const Register = {
	template: `
		<div class="row vertical-center">
			<div class="col text-center">
			<div class="col m-4 text-success">
				<span class="mx-3">
				<i class="bi bi-person-plus-fill fs-1"></i>
				</span>
				<span class="display-6">Register Account</span>
			</div>
	
			<form class="form p-2" @submit.prevent="register">
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<input type="email" id="_email" class="form-control" v-model="email" placeholder="Enter Email Address" required autofocus />
					<label for="_email">Email</label>
					</div>
				</div>
				</div>
	
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<input type="text" id="_name" class="form-control" v-model="name" placeholder="Enter Name" required />
					<label for="_name">Name</label>
					</div>
				</div>
				</div>
	
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<select class="form-select" id="_role" v-model="role">
						<option value="2" selected>Student</option>
						<option value="1">Librarian</option>
						<option value="0">Admin</option>
					</select>
					<label for="_role">User Role</label>
					</div>
				</div>
				</div>
	
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<select class="form-select" id="_gender" v-model="gender">
						<option value="F">Female</option>
						<option value="M">Male</option>
					</select>
					<label for="_gender">Choose Gender</label>
					</div>
				</div>
				</div>
	
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<input type="date" id="_dob" class="form-control" v-model="dob" placeholder="Choose Date of Birth" required />
					<label for="_dob">Date of Birth</label>
					</div>
				</div>
				</div>
	
				<div class="row">
				<div class="col-sm-4 offset-sm-4">
					<div class="form-floating mb-3">
					<input type="password" id="_pass" class="form-control" v-model="password" placeholder="Password" required />
					<label for="_pass">Password</label>
					</div>
				</div>
				</div>
	
				<div class="row">
				<div class="d-grid col-sm-4 offset-sm-4">
					<button type="submit" id="register-button" class="btn btn-block btn-success">Register</button>
				</div>
				</div>
	
				<!-- Hidden input field for operation -->
				<input type="hidden" name="op" value="register"/>
			</form>
	
			<div class="row my-4">
				<div class="d-grid col-sm-4 offset-sm-4">
				<router-link class="icon-link icon-link-hover d-inline-block" to="/login" style="text-decoration: none;">
					<i class="bi bi-caret-right-fill" aria-hidden="true"></i> Already have an account? Login
				</router-link>
				</div>
			</div>
			</div>
		</div>
		`,
	setup() {
		// Reactive properties for form inputs
		const email = Vue.ref('');
		const name = Vue.ref('');
		const role = Vue.ref('2'); // Default to Student
		const gender = Vue.ref('F'); // Default to Female
		const dob = Vue.ref('');
		const password = Vue.ref('');

		// Function to handle form submission
		function register() {
			fetch('/acc/process/register', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					email: email.value,
					name: name.value,
					role: role.value,
					gender: gender.value,
					dob: dob.value,
					password: password.value,
					op: 'register'
				}),
			})
				.then(response => response.json())
				.then(data => {
					if (data['status'] == 'ok') {
						alert('Registration Done')
						window.location.href = '/'
					} else {
						alert(data['msg'])
					}
				})
				.catch((error) => {
					console.error('Error:', error);
				});
		}

		return {
			email,
			name,
			role,
			gender,
			dob,
			password,
			register
		};
	},
};
