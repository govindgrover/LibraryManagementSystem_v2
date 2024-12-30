export const BSToast = {
	template: `
		<div v-if="toasts.length" class="toast-container bottom-0 end-0 p-4">
			<div
			v-for="(toast, index) in toasts"
			:key="index"
			class="toast"
			role="alert"
			aria-live="assertive"
			aria-atomic="true"
			>
			<div v-if="toast.heading" class="toast-header">
				<strong class="me-auto">{{ toast.heading }}</strong>
				<button
				type="button"
				class="btn-close"
				@click="removeToast(index)"
				aria-label="Close"
				></button>
			</div>
			<div class="toast-body">{{ toast.body }}</div>
			</div>
		</div>
		`,
	setup() {
		const toasts = Vue.ref([]);

		const showToast = (body, heading = '') => {
			toasts.value.push({ body, heading });
			setTimeout(() => {
				toasts.value.shift();
			}, 5000); // Adjust the timeout as needed
		};

		const removeToast = (index) => {
			toasts.value.splice(index, 1);
		};

		return { toasts, showToast, removeToast };
	}
};
