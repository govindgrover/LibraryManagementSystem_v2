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

# to log internal error responses from the API
from ..functions.functions import app_logger

# to restrict with a login
from ..functions.functions import login_required, restrict_access

# helps to fetch current accoubt details of the user to store in the session
from ..functions.accessibilty import getAccountDetailsToSession

# ============================== [ END IMPORTS ] ==============================


# API Endpoint as defined in the MAD1 - API
request_url_for_user_interaction	=	"http://127.0.0.1:5000/api/v2/interact/user"

@app.route("/book/issue", methods = ["POST"])
@login_required()
@restrict_access({2})
def process_book_issue(is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	request_params	= {
		"action": "book_borrow_request"
		, "body": {
			"book_id" : request.form["requested_book_id"]
		}
	}

	response_details = requests.post(
		request_url_for_user_interaction
		, json		=	request_params
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)


	if response_details.status_code == 204:

		return jsonify({
			"status"	:	"ok"
			, "msg"		:	[
				"Request has been raised successfully! Kindly check onto the portal regularly."
			]
		})
	elif response_details.status_code in (400, 406):
		return jsonify({
			"status"	:	"bad"
			, "msg"		:	response_details.json()["error"]["errors"]
		})
	elif response_details.status_code == 428:
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
				, request_url_for_user_interaction
				, request_params
				, (response_details.json()) if response_details.headers["Content-Type"] == "application/json" else response_details.content
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

@app.route("/book/feedback", methods = ["POST"])
@login_required()
@restrict_access({2})
def process_book_give_feedback(is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	request_params	= {
		"action": "book_feedback"
		, "body": {
			"book_id" 		:	request.form["requested_book_id"]
			, "rating"		:	int(request.form["rating"])
			, "feedback"	:	request.form["feedback"]
		}
	}

	response_details = requests.post(
		request_url_for_user_interaction
		, json		=	request_params
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)


	if response_details.status_code == 204:

		return jsonify({
			"status"	:	"ok"
			, "msg"		:	[
				"Thank you dear! For your kind words... :)"
			]
		})
	elif response_details.status_code in (400, 406):
		return jsonify({
			"status"	:	"bad"
			, "msg"		:	response_details.json()["error"]["errors"]
		})
	elif response_details.status_code == 428:
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
				, request_url_for_user_interaction
				, request_params
				, (response_details.json()) if response_details.headers["Content-Type"] == "application/json" else response_details.content
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


@app.route("/user/process/return", methods = ["POST"])
@login_required()
@restrict_access({2})
def process_book_return(is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	request_params	= {
		"action": "book_return"
		, "body": {
			"book_id" : request.form["book_id"]
		}
	}

	response_details = requests.post(
		request_url_for_user_interaction
		, json		=	request_params
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if response_details.status_code == 204:

		return jsonify({
			"status"	:	"ok"
			, "msg"		:	[
				"The selected book has been returned."
			]
		})
	elif response_details.status_code in (400, 406):
		return jsonify({
			"status"	:	"bad"
			, "msg"		:	response_details.json()["error"]["errors"]
		})
	elif response_details.status_code == 428:
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
				, request_url_for_user_interaction
				, request_params
				, (response_details.json()) if response_details.headers["Content-Type"] == "application/json" else response_details.content
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

@app.route("/book/get/details/<book_id>", methods = ["POST"])
@login_required()
@restrict_access({2})
def getBookDetails(book_id :str, is_allowed: bool = False) -> dict:
	if not is_allowed:
		return {}

	data_fetched	=	None

	data_fetched = requests.get(
		"http://127.0.0.1:5000/api/v2/fetch/details/books"
		, params	=	{
			"book_id"	:	book_id
		}
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if data_fetched.status_code == 302:
		return data_fetched.json()["data"]
	else:
		return {}

@app.route("/user/get/mylibrary", methods = ["POST"])
@login_required()
@restrict_access({2})
def getMyLibraryList(is_allowed :bool = False):
	if not is_allowed:
		return {}

	data_fetched	=	None

	data_fetched = requests.get(
		"http://127.0.0.1:5000/api/v2/interact/user"
		, json	=	{
			"action"	:	"get_my_active_records"
		}
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if data_fetched.status_code == 300:
		return data_fetched.json()["data"]
	else:
		return {}
