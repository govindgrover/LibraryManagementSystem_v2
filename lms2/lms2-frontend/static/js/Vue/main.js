import { STATE } from './state.js'

import { router } from './router.js'
import { NavBar } from './components/NavBar.js'
import { BSToast } from './components/BSToast.js';

router.beforeEach(async (to, from) => {
	if (to.meta.requiresAuth) {
		if (!STATE.isAuthenticated) {
			return { name: 'Login' }
		}
	}

	if(STATE.isAuthenticated) {
		if (['Login', 'Register'].indexOf(to.name) != -1) {
			return { name: 'Logout' }
		}
		else {
			if ('roleAuth' in to.meta) {
				if ((typeof(to.meta.roleAuth) === 'object' && to.meta.roleAuth.indexOf(Number(localStorage.getItem('role'))) == -1) || (typeof(to.meta.roleAuth) === 'number' && to.meta.roleAuth !== localStorage.getItem('role'))) {
					window.location.href = '/access_denied'
					return false
				}
			}
		}
	}

	if (STATE.isAuthenticated && to.path == '/') {
		return { name: 'Home' }
	}

})

router.afterEach(async (to, from) => {
	document.title = to.meta.title || 'Project LMS v2.0'
})

const app = Vue.createApp({
	setup() {
		const toastRef = Vue.ref(null);

		Vue.onMounted(() => {
			document.querySelectorAll('i[data-nav-icon="true"]').forEach((elem) => {
				elem.addEventListener('mouseover', () => {
					elem.classList.replace('bi-caret-left', 'bi-caret-left-fill');
					elem.classList.replace('bi-caret-right', 'bi-caret-right-fill');
				});
		
				elem.addEventListener('mouseout', () => {
					elem.classList.replace('bi-caret-left-fill', 'bi-caret-left');
					elem.classList.replace('bi-caret-right-fill', 'bi-caret-right');
				});
		
				elem.addEventListener('touchstart', () => {
					elem.classList.replace('bi-caret-left', 'bi-caret-left-fill');
					elem.classList.replace('bi-caret-right', 'bi-caret-right-fill');
				});
		
				elem.addEventListener('touchend', () => {
					elem.classList.replace('bi-caret-left-fill', 'bi-caret-left');
					elem.classList.replace('bi-caret-right-fill', 'bi-caret-right');
				});
			})
		})

		return {
			toastRef, STATE
		}
	},
	data() {
		return {
		}
	},
})

app.config.compilerOptions.delimiters = ['@{', '}'];

app.component('navbar', NavBar);
app.component('bs-toast', BSToast);

app.use(router)
app.mount('#app')
