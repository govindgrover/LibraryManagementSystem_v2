export const Home = {
	setup() {
		let user_name = Vue.ref(localStorage.getItem('name'))

		return {
			user_name
		}
	},
	template: `
		<div class="container">
			<p>Dear @{user_name}, Kindly use navigation panel to browse features.</p>
		</div>
	`
}