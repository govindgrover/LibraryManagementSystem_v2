export const Dashboard = {
	template: `
	<div>
		<h1 class="mb-5">Dashboard</h1>

		<div class="d-flex justify-content-between align-items-center my-5">
			<h5 class="mb-0">Here is some analysis</h5>
			<button id="get-report-button" class="btn btn-outline-info" @click="requestReport">Request this report?</button>
		</div>

		<div class="row row-cols-1 row-cols-md-2 g-4 mb-5 text-center">
			<div v-for="(link, index) in graphData" :key="index" class="col">
				<img
					:src="getCompleteGraphLink(link)"
					class="img-fluid rounded mx-auto d-block"
					width = "600px"
					height = "500px"
					style = "border: double lightskyblue 1.09px;"
				/>
			</div>
		</div>
	</div>
	`,

	setup() {
		const graphData = Vue.ref([]);

		const fetchGraphData = async () => {
			try {
				const response = await fetch('/lib/get/dash-graphs', { method: 'POST' });
				const data = await response.json();

				graphData.value = data.data;
			} catch (error) {
				console.error('Error fetching graph data:', error);
			}
		};

		const requestReport = async () => {
			try {
				const response = await fetch('/lib/process/get-activity-report', {
					method: 'POST',
				});
				const result = await response.json()

				if (response.ok) {
					alert(result.msg);
				} else {
					alert('Failed to request the report. Please try again.');
				}
			} catch (error) {
				console.error('Error requesting report:', error);
				alert('An error occurred. Please try again.');
			}
		};

		const getCompleteGraphLink = (val) => `http://127.0.0.1:8000/get-graphs/${val}`

		Vue.onBeforeMount(() => {
			fetchGraphData();
		});

		return {
			graphData,
			requestReport,
			getCompleteGraphLink,
		};
	},
};
