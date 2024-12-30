# ============================= [ START IMPORTS ] =============================

# flask functionalities
from flask import current_app as app
from flask import request, session, jsonify

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
from ..functions.functions import login_required

# helps to fetch current accoubt details of the user to store in the session
from ..functions.accessibilty import getAccountDetailsToSession

# ============================== [ END IMPORTS ] ==============================

# API Endpoint as defined in the MAD1 - API
request_url = "http://127.0.0.1:5000/api/v2/user/account"


@app.route("/acc/process/login", methods = ["POST"])
def process_login():
	if "app_user" in session:
		# ### 
		# session.clear()

		return jsonify({
			"status": "bad"
			, "msg": [
				"Already logged in!!"
			]
		})
	# okay, the user is not logged in yet...



	# *****************************************************************
	# **** [ PS: WE CAN PRE-VALIDATE THE PROVIDED FORM DATA HERE ] ****
	# *****************************************************************


	login_credentials = {
		"action"	:	"login"
		, "body"	:	{
			"email"			:	request.get_json()["email"]
			, "password"	:	request.get_json()["password"]
		}
	}
	# setting up the request body

	response_login = requests.post(
		request_url
		, json = login_credentials
	)
	# now, have the response

	if response_login.status_code == 206:
		# successful login... contains JWT

		session["app_user"] = dict()
		# creating a empty dict to store the user details

		session["app_user"]["access_token"] = response_login.json()["data"]["token"]
		# saved the JWT token

		# now since we have the access token, we can request the API to send
		# further account details for more interactive-ness with the user.
		acc_details = getAccountDetailsToSession(True)
		if len(acc_details):
			return jsonify({
				"status"	:	"ok"
				, "msg"		:	[
					"Login Successfull"
				]
				, 'data'	:	acc_details
			})
		else:
			del session["app_user"]
			# unset the app_user

			return jsonify({
				"status"	:	"bad"
				, "msg"		:	[
					"Unable to fetch account details"
				]
			})
		# return the info.

	elif response_login.status_code == 401:
		# invalid credentials
		return jsonify({
			"status"	:	"bad"
			, "msg"		:	[
				"Invalid login credentials !"
			]
		})

	elif response_login.status_code == 406:
		# invalid credentials
		return jsonify({
			"status"	:	"bad"
			, "msg"		:	response_login.json()["error"]["errors"]
		})

	elif response_login.status_code == 404:
		# user not found
		return jsonify({
			"status"	:	"bad"
			, "msg"		:	[
				"User not found !"
			]
		})
	else:
		# something went wrong
		app_logger.critical(
			"A {} request has been made to {} with the data, {} and the response JSON is: {}".format(
				request.method
				, request_url
				, login_credentials
				, response_login.json()
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

@app.route("/acc/process/logout", methods = ["POST"])
@login_required()
def process_logout():
	logout_data	= {
			"action": "logout"
	}

	response_logout = requests.post(
		request_url
		, data		=	logout_data
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if response_logout.status_code == 204:
		del session["app_user"]

		return jsonify({
			"status"	:	"ok"
			, "msg"		:	[
				"Logged out successfully!"
			]
		})
	elif response_logout.status_code == 400:
		return jsonify({
			"status"	:	"bad"
			, "msg"		:	[
				"Could not logout! Please try later"
			]
		})

	elif response_logout.status_code == 428:
		del session["app_user"]

		return jsonify({
			"status"	:	"ok"
			, "msg"		:	[
				"Session expired! Login again."
			]
		})

	else:
		# something went wrong
		app_logger.critical(
			"A {} request has been made to {} with the data, {} and the response JSON is: {}".format(
				request.method
				, request_url
				, logout_data
				, response_logout.json()
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

@app.route("/acc/process/register", methods = ["POST"])
def process_register():
	# session.clear()

	if "app_user" in session:
		return jsonify({
			"status": "bad"
			, "msg": [
				"Already logged in!!"
			]
		})
	# okay, the user is not logged in yet...


	# *****************************************************************
	# **** [ PS: WE CAN PRE-VALIDATE THE PROVIDED FORM DATA HERE ] ****
	# *****************************************************************


	user_details = {
		"action"	:	"register"
		, "body"	:	{
			"role"			:	request.get_json()["role"]
			, "name"		:	request.get_json()["name"]
			, "dob"			:	datetime.strftime(datetime.strptime(request.get_json()["dob"], '%Y-%m-%d'), '%d-%m-%Y')
			, "gender"		:	request.get_json()["gender"]
			, "email"		:	request.get_json()["email"]
			, "password"	:	request.get_json()["password"]
		}
	}
	# setting up the request body

	response_register = requests.put(
		request_url
		, json = user_details
	)
	# now, have the response

	if response_register.status_code == 204:
		# successfully registered

		return jsonify({
			"status"	:	"ok"
			, "msg"		:	[
				"Successfully Registered! Login to continue."
			]
		})

	elif response_register.status_code == 406:
		# input error

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	response_register.json()["error"]["errors"]
		})

	else:
		# something went wrong

		app_logger.critical(
			"A {} request has been made to {} with the data, {} and the response JSON is: {}".format(
				request.method
				, request_url
				, user_details
				, response_register.json()
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

@app.route("/acc/process/account-delete", methods = ["POST"])
@login_required()
def process_accountDelete():
	logout_data	= {
		"action": "delete"
	}

	response_logout = requests.delete(
		request_url
		, data		=	logout_data
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if response_logout.status_code == 204:
		del session["app_user"]

		return jsonify({
			"status"	:	"ok"
			, "msg"		:	[
				"Account deleted successfully!"
				, "Logging out..."
			]
		})
	elif response_logout.status_code == 400:
		return jsonify({
			"status"	:	"bad"
			, "msg"		:	[
				"Could not process the request! Please try later"
			]
		})

	elif response_logout.status_code == 428:
		del session["app_user"]

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	[
				"Session expired! Login again."
			]
		})

	else:
		# something went wrong
		app_logger.critical(
			"A {} request has been made to {} with the data, {} and the response JSON is: {}".format(
				request.method
				, request_url
				, logout_data
				, response_logout.json()
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

@app.route("/acc/update/name", methods = ["POST"])
@login_required()
def update_account_name():
	request_data	=	{
		"action": "update"
		
		, "body": {
			"field_to_update" : "name"
			, "new_value": request.get_json()["updated_name"]
		}
	}

	response_update_name = requests.post(
		request_url
		, json = request_data
		, headers = {
			"Authorization": "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if response_update_name.status_code == 204:
		# successfully registered

		acc_details = getAccountDetailsToSession(True)
		if len(acc_details):
			return jsonify({
				"status"	:	"ok"
				, "msg"		:	[
					"Updated Successfull"
				]
				, 'data'	:	acc_details
			})


	elif response_update_name.status_code == 406:

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	response_update_name.json()["error"]["errors"]
		})

	elif response_update_name.status_code == 428:
		del session["app_user"]

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	[
				"Session expired! Login again."
			]
		})

	else:
		# something went wrong
		app_logger.critical(
			"A {} request has been made to {} with the data, {} and the response JSON is: {}".format(
				request.method
				, request_url
				, request_data
				, response_update_name.json()
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

@app.route("/acc/update/password", methods = ["POST"])
@login_required()
def update_account_passsword():
	request_data	=	{
		"action": "update"
		
		, "body": {
			"field_to_update" : "password"
			, "new_value": request.get_json()["updated_password"]
		}
	}

	response_update_name = requests.post(
		request_url
		, json = request_data
		, headers = {
			"Authorization": "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if response_update_name.status_code == 204:
		# successfully updated

		acc_details = getAccountDetailsToSession(True)
		if len(acc_details):
			return jsonify({
				"status"	:	"ok"
				, "msg"		:	[
					"Updated Successfull"
				]
				, 'data'	:	acc_details
			})


	elif response_update_name.status_code == 406:

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	response_update_name.json()["error"]["errors"]
		})

	elif response_update_name.status_code == 428:
		del session["app_user"]

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	[
				"Session expired! Login again."
			]
		})

	else:
		# something went wrong
		app_logger.critical(
			"A {} request has been made to {} with the data, {} and the response JSON is: {}".format(
				request.method
				, request_url
				, request_data
				, response_update_name
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

@app.route("/acc/update/pp", methods = ["POST"])
@login_required()
def update_account_profile_picture():

	if "new_pp" not in request.files:
		return jsonify({
			"status":	"bad"
			, "msg"	:	[
				"Please upload file to proceed!"
			]
		})

	request_data	=	{
		"action": "update"
		, "field_to_update"	:	"pic"
	}

	# creating temp dir if not exists
	makedirs(
		path_join (
			app.root_path
			, app.config["TEMP_UPLOAD_FOLDER"]
		)
		, exist_ok = True
	)

	# setting temp path to file
	tmp = path_join(
		app.root_path
		, app.config["TEMP_UPLOAD_FOLDER"]
		, request.files["new_pp"].filename
	)


	# saving the uploaded file to custom temp.
	request.files["new_pp"].save(
		tmp
	)
	# we can change the filename here too..

	uploadedFile = open(tmp, "rb")

	response_update_pp = requests.post(
		request_url
		, data = request_data
		, files = {"new_value": uploadedFile}
		, headers = {
			"Authorization": "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	uploadedFile.close()
	# closed the file

	remove_file(
		tmp
	)
	# deleted the temp file


	if response_update_pp.status_code == 204:
		# successfully updated

		acc_details = getAccountDetailsToSession(True)
		if len(acc_details):
			return jsonify({
				"status"	:	"ok"
				, "msg"		:	[
					"Updated Successfull"
				]
				, 'data'	:	acc_details
			})


	elif response_update_pp.status_code in (400, 406):
		# validation error

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	response_update_pp.json()["error"]["errors"]
		})
	
	elif response_update_pp.status_code == 428:
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
				, request_url
				, request_data
				, response_update_pp.json()
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

@app.route("/acc/update/monthly-report-format", methods = ["POST"])
@login_required()
def update_monthly_report_format():
	prefer_pdf = False

	if 'updateReportFormat' in request.get_json() and request.get_json()["updateReportFormat"] == 'on':
		prefer_pdf = True

	request_data	=	{
		"action": "update_report_preference"
		
		, "body": {
			"field_to_update" : "monthly_report_format"
			, "new_value": prefer_pdf
		}
	}

	response_update_name = requests.post(
		request_url
		, json = request_data
		, headers = {
			"Authorization": "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if response_update_name.status_code == 204:
		# successfully registered

		acc_details = getAccountDetailsToSession(True)
		if len(acc_details):
			return jsonify({
				"status"	:	"ok"
				, "msg"		:	[
					"Updated Successfull"
				]
				, 'data'	:	acc_details
			})


	elif response_update_name.status_code == 406:

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	response_update_name.json()["error"]["errors"]
		})

	elif response_update_name.status_code == 428:
		del session["app_user"]

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	[
				"Session expired! Login again."
			]
		})

	else:
		# something went wrong
		app_logger.critical(
			"A {} request has been made to {} with the data, {} and the response JSON is: {}".format(
				request.method
				, request_url
				, request_data
				, response_update_name.json()
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
