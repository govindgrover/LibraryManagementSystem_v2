export const ManageUsers = {
	template: `
		<h1 class="mb-5">View & Update Records</h1>

		<div class="table-responsive mb-5">
			<table id="theAppUserListDataTable" class="table table-striped table-hover caption-top">
			<!-- Table header and body will be dynamically populated -->
			</table>
		</div>
	`,
	setup() {
		const fetchDataFromController = async (action, loadDataCallback) => {
			try {
				const response = await fetch(action, {
					method: "POST"
				});
				const data = await response.json();
				loadDataCallback(data, "#theAppUserListDataTable");
			} catch (err) {
				console.error("Error occurred! Please contact developer.", err);
			}
		};

		const loadRequestData = (data, dataTableId) => {
			if ($.fn.DataTable.isDataTable(dataTableId)) {
				$(dataTableId).DataTable().clear();
				$(dataTableId).DataTable().destroy();
			}

			if ($.isEmptyObject(data)) {
				return;
			}

			if (data["status"] === "ok") {
				$(dataTableId).DataTable({
					caption: "For: List of App Users",
					retrieve: true,
					columnDefs: [
						{
							targets: -1,
							searchable: true,
							orderable: true
						}
					],
					columns: [
						{
							title: "Profile Pic",
							defaultContent: "<img class='img-thumbnail' src='' alt='' width='64px' height='64px' />"
						},
						{ title: "Name", data: "name" },
						{ title: "E-Mail", data: "email" },
						{ title: "Role", data: "role" },
						{ title: "DOB", data: "dob" },
						{ title: "Gender", data: "gender" }
					],
					data: data["data"],
					rowId: function (row, data) {
						return row.user_id;
					},
					rowCallback: function (row, data) {
						if (data.is_active == 0) {
							row.setAttribute("class", "table-warning");
						} else if (data.is_active == 1) {
							row.setAttribute("class", "table-success");
						} else if (data.is_deleted == 1) {
							row.setAttribute("class", "table-danger");
						}
						row.childNodes[0].setAttribute("class", "text-center");
						row.childNodes[0].childNodes[0].setAttribute("src", "http://127.0.0.1:8000/static/pp/" + data.profile_picture);
					}
				});
			}
		};

		Vue.onMounted(() => {
			fetchDataFromController("/admin/process/get/users", loadRequestData);
		});

		return {};
	}
};
