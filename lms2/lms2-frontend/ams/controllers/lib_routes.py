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
from ..functions.accessibilty import getDashboardGraphLinks

# ============================== [ END IMPORTS ] ==============================


# API Endpoint as defined in the MAD1 - API
request_url_for_adding_master		=	"http://127.0.0.1:5000/api/v2/book/master"
request_url_for_filtering_masters	=	"http://127.0.0.1:5000/api/v2/fetch/details/master"
request_url_for_updating_masters	=	"http://127.0.0.1:5000/api/v2/book/master"

request_url_for_adding_book			=	"http://127.0.0.1:5000/api/v2/book/operation"
request_url_for_updating_book		=	"http://127.0.0.1:5000/api/v2/book/operation/"

request_url_for_book_issuing		=	"http://127.0.0.1:5000/api/v2/interact/librarian"

# params: /author, /publisher, /category, /genre, /language
request_params_for_masters	=	{
	"author"		:	"/author"
	, "publisher"	:	"/publisher"
	, "category"	:	"/category"
	, "genre"		:	"/genre"
	, "language"	:	"/language"
}

def __process_add_content(request_file_name :str, book_id :str):
	request_data	=	{
		"action"	:	"add_content"
		, "book_id"	:	book_id
	}

	# setting temp path
	tmp = path_join(
		app.root_path
		, app.config["TEMP_UPLOAD_FOLDER"]
	)
	# creating temp dir if not exists
	makedirs(
		tmp
		, exist_ok = True
	)

	tmp = path_join(
		tmp
		, request.files[request_file_name].filename
	)
	# now 'tmp' contains full path to the file

	# saving the uploaded file to custom temp.
	request.files[request_file_name].save(
		tmp
	)
	# we can change the filename here too.. and thus remove that '$' sepration
	# from the API...

	uploadedFile = open(tmp, "rb")

	response_add_book_content = requests.put(
		request_url_for_adding_book
		, data = request_data
		, files = {"book_content": uploadedFile}
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
 
	return response_add_book_content

@app.route("/lib/process/<master>/add", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def process_add_master(master, is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	if master not in request_params_for_masters:
		return jsonify({
			"status": "bad"
			, "msg": [
				"The master to be added is invalid!"
			]
		})


	put_data	= {
		"action": "add"
		, "body": {
		}
	}

	if master == "author":
		put_data["body"]["author_name"]	=	request.form["name"]
		put_data["body"]["author_bio"]	=	request.form["bio"]
	elif master == "publisher":
		put_data["body"]["publisher_name"]	=	request.form["name"]
		put_data["body"]["publisher_desc"]	=	request.form["description"]
	elif master == "category":
		put_data["body"]["category_name"]	=	request.form["name"]
	elif master == "genre":
		put_data["body"]["genre_name"]	=	request.form["name"]
	elif master == "language":
		put_data["body"]["language_name"]	=	request.form["name"]

	response_put = requests.put(
		request_url_for_adding_master + request_params_for_masters[master]
		, json		=	put_data
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)


	if response_put.status_code == 204:

		return jsonify({
			"status"	:	"ok"
			, "msg"		:	[
				"{} added successfully!".format(
					master.capitalize()
				)
			]
		})
	elif response_put.status_code == 406:
		return jsonify({
			"status"	:	"bad"
			, "msg"		:	response_put.json()["error"]["errors"]
		})
	elif response_put.status_code == 428:
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
				, request_url_for_adding_master
				, put_data
				, response_put.json() if response_put.headers["Content-Type"] == "application/json" else response_put.content
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


@app.route("/lib/process/get/<master>", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def process_get_masters(master, is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	if master not in request_params_for_masters:
		return jsonify({
			"status": "bad"
			, "msg": [
				"The master to be viewed is invalid!"
			]
		})
	
	# filtering_params = {
	# 	"filter_name"	:	request.get_json()["filter_by"]
	# 	, "filter_value":	request.get_json()["value"]
	# }
	# if "limit" in request.get_json() and request.get_json()["limit"] > 0:
	# 	filtering_params["limit"] = request.get_json()["limit"]
	# # if limit is not None and gt. than zero then apply it
	

	filtering_params = {
		"filter_name"	:	"name_like"
		, "filter_value":	""			# to get list of all
	}

	response_filtered = requests.get(
		request_url_for_filtering_masters + request_params_for_masters[master]
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
				, request_url_for_filtering_masters + request_params_for_masters[master]
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


@app.route("/lib/process/<master>/modify/<field>", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def process_modify_master_with_field(master, field, is_allowed: bool = False):

	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	if master not in request_params_for_masters:
		return jsonify({
			"status": "bad"
			, "msg": [
				"The master to be updated is invalid!"
			]
		})
	# ok correct master

	if field not in ("name", "bio", 'desc', "active", "delete"):
		return jsonify({
			"status": "bad"
			, "msg": [
				"The field to be updated is invalid!"
			]
		})
	# and so is the field
	
	params_to_update = {
		"action": "update"
		, "body": {
			"field_to_update"	:	""
			, "new_value"		:	""
		}
	}

	params_to_update["body"][master + "_id"]		=	request.get_json()[master + "_id"]
	# provided required ID to process further

	if field == "name":
		params_to_update["body"]["field_to_update"]	=	"name"
		params_to_update["body"]["new_value"]		=	request.get_json()["updated_name"]
	elif field == "bio":
		params_to_update["body"]["field_to_update"]	=	"bio"
		params_to_update["body"]["new_value"]		=	request.get_json()["updated_bio"]
	elif field == "desc":
		params_to_update["body"]["field_to_update"]	=	"desc"
		params_to_update["body"]["new_value"]		=	request.get_json()["updated_desc"]
	elif field == "active":
		params_to_update["body"]["field_to_update"]	=	"active"
		params_to_update["body"]["new_value"]		=	1 if ("updated_active_status" in request.get_json() and request.get_json()["updated_active_status"] == "on") else 0


	if field == "delete":
		params_to_update["action"]					=	"delete"


		response_updated = requests.delete(
			request_url_for_updating_masters + request_params_for_masters[master]
			, json	=	params_to_update
			, headers	=	{
				"Authorization" : "Bearer {}".format(
					session["app_user"]["access_token"]
				)
			}
		)
	else:
		response_updated = requests.post(
			request_url_for_updating_masters + request_params_for_masters[master]
			, json	=	params_to_update
			, headers	=	{
				"Authorization" : "Bearer {}".format(
					session["app_user"]["access_token"]
				)
			}
		)

	if response_updated.status_code == 204:
		# response - without content

		return jsonify({
			"status":	"ok"
			, "msg"	:	[
				"Provided details has been updated successfully!"
			]
			, 'last_master': master
		})
	elif response_updated.status_code == 404:
		# response - as required data not found

		return jsonify({
			"status":	"bad"
			, "msg"	:	response_updated.json()["error"]["errors"]
			, 'last_master': master
		})
	elif response_updated.status_code == 406:
		# invalid input

		return jsonify({
			"status":	"bad"
			, "msg"	:	response_updated.json()["error"]["errors"]
			, 'last_master': master
		})
	elif response_updated.status_code == 428:
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
				, request_url_for_updating_masters + request_params_for_masters[master]
				, params_to_update
				, response_updated.json() if response_updated.headers["Content-Type"] == "application/json" else response_updated.content
			)
		)
		# reported to the logger

		return jsonify({
			"status"	:	"bad"
			, "msg"		:	[
				"Something went wrong"
			]
			, 'last_master': master
	})
		# response given

@app.route("/lib/process/books/add", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def process_add_book(is_allowed: bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	date = request.form["pub_date"].split('-')

	put_data	= {
		"action": "add_details"
		, "body" : {
			"book_isbn"                 :	request.form["isbn"]
			, "book_title"              :   request.form["title"]
			, "book_edition"            :   request.form["edition"]
			, "book_publication_date"   :	date[2] + '-' + date[1] + '-' + date[0]
			, "book_desc"               :   request.form["book_description"]
			, "book_price"              :   request.form["price"]

			, "publisher_id"    		:   request.form["publisher_id"]
			, "author_id"       		:   request.form.getlist("author_ids")
			, "language_id"     		:   request.form["language_id"]
			, "category_id"     		:   request.form.getlist("category_ids")
			, "genre_id"        		:   request.form.getlist("genre_ids")
		}
	}

	# request_url_for_adding_book

	response_put_details = requests.put(
		request_url_for_adding_book
		, json		=	put_data
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)
	# adding details first... then moving to add the content


	if response_put_details.status_code == 206:
		resp_put_content = __process_add_content(
			"book_content"
			, response_put_details.json()["data"][0]["book_id"]
		)
		# now adding content
  
		if resp_put_content.status_code == 204:
			return jsonify({
				"status"	:	"ok"
				, "msg"		:	[
					"Book added successfully!"
				]
			})
		else:
			resp = resp_put_content
	else:
		resp = response_put_details

	if resp.status_code == 406:
		return jsonify({
			"status"	:	"bad"
			, "msg"		:	resp.json()["error"]["errors"]
		})
	elif resp.status_code == 428:
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
				, request_url_for_adding_book
				, put_data
				, resp.json() if resp.headers["Content-Type"] == "application/json" else resp.content
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

@app.route("/lib/process/book/modify/<field>", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def process_modify_book_with_field(field, is_allowed: bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	if field not in ("title", "desc", "price", "cimg", "active", "delete"):
		return jsonify({
			"status": "bad"
			, "msg": [
				"The field to be updated is invalid!"
			]
		})
	# and so is the field
	
	params_to_update = {
		"action": "update"
		, "body": {
			"field_to_update"	:	""
			, "new_value"		:	""
			, "book_id"			:	request.get_json()["book_id"] if request.is_json else ''
		}
	}

	if field == "title":
		params_to_update["body"]["field_to_update"]	=	"book_title"
		params_to_update["body"]["new_value"]		=	request.get_json()["updated_title"]
	elif field == "desc":
		params_to_update["body"]["field_to_update"]	=	"book_desc"
		params_to_update["body"]["new_value"]		=	request.get_json()["updated_desc"]
	elif field == "price":
		params_to_update["body"]["field_to_update"]	=	"book_price"
		params_to_update["body"]["new_value"]		=	request.get_json()["updated_price"]
	elif field == "active":
		params_to_update["body"]["field_to_update"]	=	"active"
		params_to_update["body"]["new_value"]		=	1 if ("updated_active_status" in request.get_json() and request.get_json()["updated_active_status"] == "on") else 0


	if field == "delete":
		params_to_update["action"]					=	"delete"

		response_updated = requests.delete(
			request_url_for_updating_book
			, json	=	params_to_update
			, headers	=	{
				"Authorization" : "Bearer {}".format(
					session["app_user"]["access_token"]
				)
			}
		)
	elif field == "cimg":
		params_to_update	=	{}
		params_to_update["action"]			=	"update"
		params_to_update["field_to_update"]	=	"cover_image"
		params_to_update["book_id"]			=	request.form["book_id"]

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
			, request.files["updated_cimg"].filename
		)


		# saving the uploaded file to custom temp.
		request.files["updated_cimg"].save(
			tmp
		)
		# we can change the filename here too..
  
		# opening the file
		uploadedFile = open(tmp, "rb")

		response_updated = requests.post(
			request_url_for_updating_book
			, data		=	params_to_update
			, files		=	{"new_value": uploadedFile}
			, headers	=	{
				"Authorization" : "Bearer {}".format(
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
	else:
		response_updated = requests.post(
			request_url_for_updating_book
			, json	=	params_to_update
			, headers	=	{
				"Authorization" : "Bearer {}".format(
					session["app_user"]["access_token"]
				)
			}
		)

	if response_updated.status_code == 204:
		# response - without content

		return jsonify({
			"status":	"ok"
			, "msg"	:	[
				"Provided details has been updated successfully!"
			]
		})
	elif response_updated.status_code == 404:
		# response - as required data not found

		return jsonify({
			"status":	"bad"
			, "msg"	:	response_updated.json()["error"]["errors"]
		})
	elif response_updated.status_code == 406:
		# invalid input

		return jsonify({
			"status":	"bad"
			, "msg"	:	response_updated.json()["error"]["errors"]
		})
	elif response_updated.status_code == 428:
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
				, request_url_for_updating_book
				, params_to_update
				, response_updated.json() if response_updated.headers["Content-Type"] == "application/json" else response_updated.content
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

@app.route("/lib/process/get/issue-requests", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def process_get_issue_requests(is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	data_fetched = requests.get(
		"http://127.0.0.1:5000/api/v2/interact/librarian"
		, json	=	{
			"action"	:	"list_book_requests"
		}
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if data_fetched.status_code == 206:
		# response - with data

		return jsonify({
			"status":	"ok"
			, "msg"	:	[
				"Loading data..."
			]
			, "data":	data_fetched.json()["data"]
		})
	elif data_fetched.status_code == 404:
		# response - as required data not found

		return jsonify({
			"status":	"bad"
			, "msg"	:	data_fetched.json()["error"]["errors"]
		})
	elif data_fetched.status_code == 406:
		# invalid input

		return jsonify({
			"status":	"bad"
			, "msg"	:	data_fetched.json()["error"]["errors"]
		})
	elif data_fetched.status_code == 428:
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
				, "http://127.0.0.1:5000/api/v2/interact/librarian"
				, "NA"
				, data_fetched.json() if data_fetched.headers["Content-Type"] == "application/json" else data_fetched.content
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

@app.route("/lib/process/issue-requests/issue", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def process_grant_issue_requests(is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")

	data_fetched = requests.post(
		request_url_for_book_issuing
		, json	=	{
			"action"	:	"accept_book_request"
			, "body"	:	{
				"user_id"	:	request.get_json()["book_requested_by"]
				, "book_id"	:	request.get_json()["requested_book_id"]
			}
		}
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if data_fetched.status_code == 200:
		# response
  
		return jsonify({
			"status":	"ok"
			, "msg"	:	[
				"Access granted for the time period."
			]
		})
	elif data_fetched.status_code == 404:
		# response - as required data not found

		return jsonify({
			"status":	"bad"
			, "msg"	:	data_fetched.json()["error"]["errors"]
		})
	elif data_fetched.status_code == 406:
		# invalid input

		return jsonify({
			"status":	"bad"
			, "msg"	:	data_fetched.json()["error"]["errors"]
		})
	elif data_fetched.status_code == 428:
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
				, request_url_for_book_issuing
				, "NA"
				, data_fetched.json() if data_fetched.headers["Content-Type"] == "application/json" else data_fetched.content
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

@app.route("/lib/process/issue-requests/purchase", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def process_grant_purchase_requests(is_allowed :bool = False):	
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	data_fetched = requests.post(
		request_url_for_book_issuing
		, json	=	{
			"action"	:	"book_purchase"
			, "body"	:	{
				"user_id"			:	request.get_json()["book_requested_by"]
				, "book_id"			:	request.get_json()["requested_book_id"]
				, "current_cost"	:	request.get_json()["written_cost"]
				, "transaction_id"	:	request.get_json()["transaction_id"]
			}
		}
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if data_fetched.status_code == 206:
		# response
  
		return jsonify({
			"status":	"ok"
			, "msg"	:	[
				"The provided book as been purchased by the user."
			]
			, "data" : data_fetched.json()["data"]
		})
		# returned the access token

	elif data_fetched.status_code == 404:
		# response - as required data not found

		return jsonify({
			"status":	"bad"
			, "msg"	:	data_fetched.json()["error"]["errors"]
		})
	elif data_fetched.status_code in (400, 406):
		# invalid input

		return jsonify({
			"status":	"bad"
			, "msg"	:	data_fetched.json()["error"]["errors"]
		})
	elif data_fetched.status_code == 428:
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
				, request_url_for_book_issuing
				, "NA"
				, (data_fetched.json()) if data_fetched.headers["Content-Type"] == "application/json" else data_fetched.content
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


@app.route("/lib/process/get/borrow-history", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def process_get_borrow_history(is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	data_fetched = requests.get(
		"http://127.0.0.1:5000/api/v2/interact/librarian"
		, json= {
			"action": "list_borrow_history"
		}
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if data_fetched.status_code == 206:
		# response - with data

		return jsonify({
			"status":	"ok"
			, "msg"	:	[
				"Loading data..."
			]
			, "data":	data_fetched.json()["data"]
		})
	elif data_fetched.status_code == 404:
		# response - as required data not found

		return jsonify({
			"status":	"bad"
			, "msg"	:	data_fetched.json()["error"]["errors"]
		})
	elif data_fetched.status_code == 406:
		# invalid input

		return jsonify({
			"status":	"bad"
			, "msg"	:	data_fetched.json()["error"]["errors"]
		})
	elif data_fetched.status_code == 428:
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
				, "http://127.0.0.1:5000/api/v2/interact/librarian"
				, "NA"
				, data_fetched.json() if data_fetched.headers["Content-Type"] == "application/json" else data_fetched.content
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


@app.route("/lib/process/borrow-history/revoke", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def process_revoke_issued_book(is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	data_fetched = requests.post(
		request_url_for_book_issuing
		, json	=	{
			"action"	:	"revoke_book_access"
			, "body"	:	{
				"user_id"	:	request.get_json()["issued_to_id"]
				, "book_id"	:	request.get_json()["issued_book_id"]
			}
		}
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if data_fetched.status_code == 204:
		# response
  
		return jsonify({
			"status":	"ok"
			, "msg"	:	[
				"Access revoked successfully!"
			]
		})
	elif data_fetched.status_code == 404:
		# response - as required data not found

		return jsonify({
			"status":	"bad"
			, "msg"	:	data_fetched.json()["error"]["errors"]
		})
	elif data_fetched.status_code == 406:
		# invalid input

		return jsonify({
			"status":	"bad"
			, "msg"	:	data_fetched.json()["error"]["errors"]
		})
	elif data_fetched.status_code == 428:
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
				, request_url_for_book_issuing
				, "NA"
				, data_fetched.json() if data_fetched.headers["Content-Type"] == "application/json" else data_fetched.content
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


@app.route("/lib/process/get-activity-report", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def request_activity_report(is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")

	data_fetched = requests.post(
		"http://127.0.0.1:5000/api/v2/interact/librarian"
		, json	=	{
			"action"	:	"send_graph_report"
			, "body"	:	{
				"requestee_id"	:	session["app_user"]["user_id"]
			}
		}
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)
	
	return jsonify({
		"status"	:	"ok"
		, "msg"		:	[
			"Request has been raised! You will get the report on your registered email"
		]
	})
	# response given

@app.route("/lib/process/get-borrowance-report", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def request_borrowance_report(is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")

	data_fetched = requests.post(
		"http://127.0.0.1:5000/api/v2/interact/librarian"
		, json	=	{
			"action"	:	"send_borrowance_report"
			, "body"	:	{
				"requestee_id"	:	session["app_user"]["user_id"]
			}
		}
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)
	
	return jsonify({
		"status"	:	"ok"
		, "msg"		:	[
			"Request has been raised! You will get the report on your registered email"
		]
	})
	# response given

@app.route("/lib/get/dash-graphs", methods = ["POST"])
@login_required()
@restrict_access({0, 1})
def get_dashboard_graphs(is_allowed :bool = False):
	if not is_allowed:
		session["is_access_denied"] = True
		return redirect("/access-denied")
	
	return jsonify({
		"status"	:	"ok"
		, "msg"		:	[
			"Loading..."
		]
		, "data": getDashboardGraphLinks()
	})
	# response given

