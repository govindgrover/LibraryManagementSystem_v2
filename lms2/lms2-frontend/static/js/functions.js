function makeHTMLToast(body, heading = '') {
	if (heading == '') {
		return `\
			<div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-custom-id="bstoast">\
				<div id="toast-body" class="toast-body">${body}</div>\
			</div>\
			`;
	}
	else {
		return `\
			<div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-custom-id="bstoast">\
				<div class="toast-header">\
					<strong class="me-auto">${heading}</strong>\
					<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>\
				</div>\
				<div id="toast-body" class="toast-body">${body}</div>\
			</div>\
			`;
	}
}

function showToasts(json_data, attr, title) {
	let toast_container = document.getElementById("toast_container");

	// removed past toasts
	toast_container.innerHTML = "";

	json_data[attr].forEach(m => {
		toast_container.innerHTML += makeHTMLToast(m, title);
	});

	let toastList = document.querySelectorAll("div[data-custom-id='bstoast']");
	var t;
	toastList.forEach(e => {
		t = new bootstrap.Toast(e);
		t.show();
	});

	return;
}

function sendFormData(givenForm, givenBSButton = null, auto_reload_on_success = true, customCallbackWithData = null) {
	givenForm.addEventListener("submit", (e) => {
		e.preventDefault();

		if (givenBSButton != null) {
			givenBSButton.toggle();
		}

		let givenFormData = new FormData(givenForm);

		fetch(
			givenForm.action
			, {
				method: givenForm.method
				, body: givenFormData
			}
		).then(
			response => response.json()			
		).then(
			data => {
				// time in ms for window reload
				let ms = 2000;

				if (data["status"] == "ok") {
					if (auto_reload_on_success) {
						data.msg.push("Reloading window in " + (ms/1000) + " sec.");

						setTimeout(() => {
							window.location.reload();
						}, ms);
					}
				}

				showToasts(data, 'msg', "Message");

				if (customCallbackWithData != null) {
					customCallbackWithData(data);
				}
			}
		).catch(
			err =>	{
				console.log("Error occured! Please contact developer.");
				console.log(err);
			}
		)
	});
}

export { showToasts, sendFormData };
