# ============================= [ START IMPORTS ] =============================

# flask functionalities
from flask import current_app as app
from flask import request, redirect
from flask import session, jsonify

# to handle requests
import requests

# for controller's operations
from datetime import datetime
from os.path import join as path_join
from os import remove as remove_file
from os import makedirs

# to log internal error responses from the API
from ..functions.functions import app_logger

# to restrict with a login
from ..functions.functions import login_required, restrict_access

# helps to fetch current accoubt details of the user to store in the session
from ..functions.accessibilty import getAccountDetailsToSession

# ============================== [ END IMPORTS ] ==============================


# API Endpoint as defined in the MAD1 - API
request_url_for_filtering_users	=	"http://127.0.0.1:5000/api/v2/fetch/details/users"


@app.route("/admin/process/get/users", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def process_get_app_users(is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")	

	filtering_params = {
		"filter_name"	:	"name_like"
		, "filter_value":	""			# to get list of all
	}

	response_filtered = requests.get(
		request_url_for_filtering_users
		, params	=	filtering_params
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if response_filtered.status_code == 302:
		# response - with data

		return jsonify({
			"status":	"ok"
			, "msg"	:	[
				"Loading data..."
			]
			, "data":	response_filtered.json()["data"]
		})
	elif response_filtered.status_code == 404:
		# response - as required data not found

		return jsonify({
			"status":	"bad"
			, "msg"	:	response_filtered.json()["error"]["errors"]
		})
	elif response_filtered.status_code == 406:
		# invalid input

		return jsonify({
			"status":	"bad"
			, "msg"	:	response_filtered.json()["error"]["errors"]
		})
	elif response_filtered.status_code == 428:
		# access token expired
		del session["app_user"]

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	"Session expired! Login again."
		})
	else:
		# something went wrong
		app_logger.critical(
			"A {} request has been made to {} with the data, {} and the response JSON is: {}".format(
				request.method
				, request_url_for_filtering_users
				, filtering_params
				, response_filtered.json() if response_filtered.headers["Content-Type"] == "application/json" else response_filtered.content
			)
		)
		# reported to the logger

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	[
				"Something went wrong"
			]
		})
		# response given

