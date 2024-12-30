import { STATE } from './../../state.js'

export const Logout = {
	template: `
		<div class="row vertical-center">
			<div class="col text-center">
			<div class="col m-4 text-warning">
				<span class="mx-3">
				<i class="bi bi-box-arrow-in-left fs-1"></i>
				</span>
				<span class="display-6">Logout ?</span>
			</div>
	
			<form class="form p-2" @submit.prevent="handleLogout">
				<div class="row">
				<div class="d-grid col-sm-4 offset-sm-4 col-sm">
					<button type="submit" id="logout-button" class="btn btn-block btn-warning">
					Logout
					</button>
				</div>
				</div>
				<input type="hidden" name="op" value="logout" />
			</form>
			</div>
		</div>
		`,
	setup() {
		function handleLogout() {
			fetch('/acc/process/logout', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded',
				},
				body: new URLSearchParams({
					op: 'logout',
				}),
			})
				.then(response => {
					if (response.ok) {
						alert('Logged Out')

						STATE.isAuthenticated = false;
						localStorage.clear();

						window.location.href = '/';
					} else {
						alert('Unable to logout')
					}
				})
				.catch(error => {
					console.error('Error:', error);
				});
		}

		return {
			handleLogout,
		};
	}
};
