import { DefaultPage } from './components/pages/DefaultPage.js'
import { Home } from './components/pages/Home.js'
import { NotFound } from './components/pages/NotFound.js'

import { Login } from './components/pages/Login.js'
import { Logout } from './components/pages/Logout.js'
import { Register } from './components/pages/Register.js'
import { MyAccount } from './components/pages/MyAccount.js'

import { ManageUsers } from './components/pages/AdminInterface/ManageUsers.js'

import { Dashboard } from './components/pages/ManagerInterface/Dashboard.js'
import { ActiveBorrows } from './components/pages/ManagerInterface/ActiveBorrows.js'
import { IssueRequests } from './components/pages/ManagerInterface/IssueRequests.js'
import { AddMasters } from './components/pages/ManagerInterface/AddMasters.js'
import { ManageMasters } from './components/pages/ManagerInterface/ManageMasters.js'
import { AddBook } from './components/pages/ManagerInterface/AddBook.js'
import { ManageBooks } from './components/pages/ManagerInterface/ManageBooks.js'

import { BrowseBooks } from './components/pages/UserInterface/BrowseBooks.js'
import { ViewBookDetails } from './components/pages/UserInterface/ViewBookDetails.js'
import { MyLibrary } from './components/pages/UserInterface/MyLibrary.js'


const routes = [
	{
		path: "/:catchAll(.*)",
		component: NotFound,
		name: 'NotFound',
		meta: {
			requiresAuth: false
		}
	},
	{
		path: '/',
		component: DefaultPage,
		name: 'DefaultPage',
		meta: {
			requiresAuth: false,
		}
	},


	{
		path: '/home',
		component: Home,
		name: 'Home',
		meta: {
			requiresAuth: true
		},
	},
	{
		path: '/login',
		component: Login,
		name: 'Login',
		meta: {
			requiresAuth: false,
			title: 'Login'
		},
	},
	{
		path: '/register',
		component: Register,
		name: 'Register',
		meta: {
			requiresAuth: false,
			title: 'Register'
		}
	},
	{
		path: '/logout',
		component: Logout,
		name: 'Logout',
		meta: {
			requiresAuth: true,
			title: 'Logout'
		},
	},
	{
		path: '/myaccount',
		component: MyAccount,
		name: 'MyAccount',
		meta: {
			requiresAuth: true
		}
	},


	{
		path: '/dashboard',
		component: Dashboard,
		name: 'Dashboard',
		meta: {
			requiresAuth: true,
			title: 'Dashboard',
			roleAuth: [0, 1]
		}
	},


	{
		path: '/admin/manage/users',
		component: ManageUsers,
		name: 'ManageUsers',
		meta: {
			requiresAuth: true,
			title: 'App-Users List',
			roleAuth: [0]
		}
	},
	{
		path: '/admin/manage/books',
		meta: {
			requiresAuth: true,
			roleAuth: 0,
		},
		redirect: {
			name: 'ManageBooks'
		}
	},
	{
		path: '/admin/manage/masters',
		meta: {
			requiresAuth: true,
			roleAuth: 0,
		},
		redirect: {
			name: 'ManageMasters'
		}
	},


	{
		path: '/lib/manage/books/add',
		component: AddBook,
		name: 'AddBook',
		meta: {
			requiresAuth: true,
			title: 'Add New Book',
			roleAuth: [1]
		}
	},
	{
		path: '/lib/manage/books',
		component: ManageBooks,
		name: 'ManageBooks',
		meta: {
			requiresAuth: true,
			title: 'Manage Books',
			roleAuth: [0, 1]
		}
	},
	{
		path: '/lib/manage/masters/add',
		component: AddMasters,
		name: 'AddMasters',
		meta: {
			requiresAuth: true,
			title: 'Add New Masters',
			roleAuth: [1]
		}
	},
	{
		path: '/lib/manage/masters',
		component: ManageMasters,
		name: 'ManageMasters',
		meta: {
			requiresAuth: true,
			title: 'Manage Masters',
			roleAuth: [0, 1]
		}
	},
	{
		path: '/lib/manage/issue-requests',
		component: IssueRequests,
		name: 'IssueRequests',
		meta: {
			requiresAuth: true,
			title: 'Manage Issue Requests',
			roleAuth: [1]
		}
	},
	{
		path: '/lib/manage/borrow-history',
		component: ActiveBorrows,
		name: 'ActiveBorrows',
		meta: {
			requiresAuth: true,
			title: 'Manage Active Borrows',
			roleAuth: [1]
		}
	},


	{
		path: '/browse',
		component: BrowseBooks,
		name: 'BrowseBooks',
		meta: {
			requiresAuth: true,
			title: 'Browse Books',
			roleAuth: [2]
		}
	},
	{
		path: '/browse/details/:id',
		component: ViewBookDetails,
		name: 'ViewBookDetails',
		meta: {
			requiresAuth: true,
			title: 'Book Details',
			roleAuth: [2]
		}
	},
	{
		path: '/mylibrary',
		component: MyLibrary,
		name: 'MyLibrary',
		meta: {
			requiresAuth: true,
			title: 'My Library',
			roleAuth: [2]
		}
	},
];

export const router = VueRouter.createRouter({
	history: VueRouter.createWebHistory(),
	routes
});
