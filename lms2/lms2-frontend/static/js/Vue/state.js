const STATE = Vue.reactive({
	isAuthenticated: false
});

// checking localStorage if the details are stored
if (localStorage.getItem('user_id') != null) {
	STATE.isAuthenticated = true;
}

export {
	STATE
};
