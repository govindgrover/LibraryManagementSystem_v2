export const NavBar = Vue.defineComponent({
	setup() {
		let user_name = localStorage.getItem('name')
		let user_role = localStorage.getItem('role')
		let is_logged_in = localStorage.getItem('user_id') != null ? true : false

		return {
			user_name,
			user_role,
			is_logged_in
		};
	},
	template: `
	<nav class="navbar border-bottom border-body navbar-expand-lg bg-body-tertiary mb-2" data-bs-theme="">
	<!-- for dark mode use => data-bs-theme="dark" -->

	<div class="container-fluid">
		<router-link to="./" class="navbar-brand">Library Management System v2 | IITM BS</router-link>

		<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#lib_nav"
		aria-controls="lib_nav" aria-expanded="false" aria-label="Toggle navigation">
		<span class="navbar-toggler-icon"></span>
		</button>

		<div class="collapse navbar-collapse" id="lib_nav">
			<ul class="navbar-nav ms-auto mb-2 mb-lg-0">
				<template v-if="is_logged_in">
					<li class="nav-item"><router-link to="/" class="nav-link text-info">Home</router-link></li>
				</template>

				<template v-if="user_role == 0">
					<li class="nav-item"><router-link to="/dashboard" class="nav-link text-primary">Dashboard</router-link></li>
					<li class="nav-item"><router-link to="/admin/manage/users" class="nav-link text-primary">Manage App Users</router-link></li>
					<li class="nav-item"><router-link to="/admin/manage/books" class="nav-link text-primary">Manage Books</router-link></li>
					<li class="nav-item"><router-link to="/admin/manage/masters" class="nav-link text-primary">Manage Masters</router-link></li>
				</template>

				<template v-else-if="user_role == 1">
					<li class="nav-item"><router-link to="/dashboard" class="nav-link text-primary">Dashboard</router-link></li>
					<li class="nav-item dropdown">
						<a class="nav-link dropdown-toggle text-primary" href="#" role="button" data-bs-toggle="dropdown"
						aria-expanded="false">
						Books
						</a>
						<ul class="dropdown-menu">
						<li><router-link class="dropdown-item" to="/lib/manage/books/add">Add New</router-link></li>
						<li><router-link class="dropdown-item" to="/lib/manage/books">View & Manage</router-link></li>
						</ul>
					</li>
					<li class="nav-item dropdown">
						<a class="nav-link dropdown-toggle text-primary" href="#" role="button" data-bs-toggle="dropdown"
						aria-expanded="false">
						Masters
						</a>
						<ul class="dropdown-menu">
						<li><router-link class="dropdown-item" to="/lib/manage/masters/add">Add New</router-link></li>
						<li><router-link class="dropdown-item" to="/lib/manage/masters">View & Manage</router-link></li>
						</ul>
					</li>
					<li class="nav-item"><router-link to="/lib/manage/issue-requests" class="nav-link text-primary">Issue Requests</router-link></li>
					<li class="nav-item"><router-link to="/lib/manage/borrow-history" class="nav-link text-primary">Active Borrows</router-link></li>
				</template>

				<template v-else-if="user_role == 2">
					<li class="nav-item"><router-link to="/browse" class="nav-link text-primary">Browse Books</router-link></li>
					<li class="nav-item"><router-link to="/mylibrary" class="nav-link text-primary">My Library</router-link></li>
				</template>

				<template v-if="is_logged_in">
					<li class="nav-item"><router-link to="/myaccount" class="nav-link text-success">My Account</router-link></li>
					<li class="nav-item"><router-link to="/logout" class="nav-link text-success">Logout</router-link></li>
				</template>
				<template v-else>
					<li class="nav-item"><router-link to="/login" class="nav-link text-success">Login</router-link></li>
					<li class="nav-item"><router-link to="/register" class="nav-link text-success">Register</router-link></li>
				</template>
			</ul>

			<template v-if="is_logged_in">
				<span class="navbar-text ps-3">
					<span style="font-size: small;">Welcome</span>
					<br />
					<i>@{ user_name }</i>
				</span>
			</template>
		</div>

		<span class="position-fixed bottom-0 start-0 nav-padding" @click="$router.go(-1)" title='Back'>
			<i class="bi bi-caret-left fs-1 text-secondary bubble" data-nav-icon="true"></i>
		</span>
		<span id="myr" class="position-fixed bottom-0 end-0 nav-padding" @click="$router.go(1)" title='Forward'>
			<i class="bi bi-caret-right fs-1 text-secondary bubble" data-nav-icon="true"></i>
		</span>
	</div>
</nav>
`
});
