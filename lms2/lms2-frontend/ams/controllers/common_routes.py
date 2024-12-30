# ============================= [ START IMPORTS ] =============================

# flask functionalities
from flask import current_app as app
from flask import session

# to handle requests
import requests
from flask import make_response, redirect, send_file, jsonify, request

# to handle file operations
from os.path import join as path_join

# to log internal error responses from the API
from ..functions.functions import app_logger

# to restrict with a login
from ..functions.functions import login_required, restrict_access

# ============================== [ END IMPORTS ] ==============================

request_url_for_filtering_books		=	"http://127.0.0.1:5000/api/v2/fetch/details/books"

# ============================== [ START ROUTES ] =============================

@app.route('/manifest.json', methods = ["GET"])
def get_manifest():
	import json

	with open(path_join(app.root_path, "ams", "manifest.json")) as manifest:
		return jsonify(json.load(manifest))

@app.route('/pwa/icons/<icon_name>', methods = ['GET'])
def get_pwa_requirements(icon_name: str):
	from flask import send_from_directory

	return send_from_directory(
		path_join(
			app.root_path
			, 'static'
			, 'icons'
		)
		, icon_name
		, as_attachment = True
	)

@app.route("/static/pp/<pname>", methods = ["GET"])
# @login_required()
def fetchProfilePicture(pname :str):
	img = requests.get(
		"http://127.0.0.1:5000/api/v2/fetch/static/profile_pictures/{}".format(
			pname
		)
	)

	resp = make_response(img.content)
	resp.headers.set('Content-Type', img.headers["Content-Type"])

	return resp

@app.route("/static/ci/<cimg>", methods = ["GET"])
# @login_required()
def fetchBookCoverImage(cimg :str):
	img = requests.get(
		"http://127.0.0.1:5000/api/v2/fetch/static/books_cover_img/{}".format(
			cimg
		)
	)

	resp = make_response(img.content)
	resp.headers.set('Content-Type', img.headers["Content-Type"])

	return resp

@login_required()
@app.route("/book/read/<book_id>", methods = ["GET"])
def getBookContent(book_id :str):
	book_content = requests.get(
		"http://127.0.0.1:5000/api/v2/book/retrive/{}".format(book_id)
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if book_content.status_code == 200:
		resp = make_response(book_content.content)
		resp.headers.set('Content-Type', book_content.headers["Content-Type"])

		return resp
	else:
		# something went wrong
		app_logger.critical(
			"A {} request has been made to {} with the data, {} and the response JSON is: {}".format(
				"get"
				, "http://127.0.0.1:5000/api/v2/book/retrive/" + book_id
				, None
				, (book_content.json()) if book_content.headers["Content-Type"] == "application/json" else book_content.content
			)
		)
		# reported to the logger

		return redirect("/404")

@app.route("/get-graphs/<gname>", methods = ["GET"])
# @login_required()
def fetchGraphPlots(gname :str = ""):
	return send_file(
		path_join(
			app.root_path
			, app.config["TEMP_GRAPH_IMAGES_FOLDER"]
			, gname
		)
	)

@app.route("/lib/process/get/books", methods = ["POST"])
@login_required()
def process_get_books():	
	# filtering_params = {
	# 	"filter_name"	:	request.get_json()["filter_by"]
	# 	, "filter_value":	request.get_json()["value"]
	# }
	# if "limit" in request.get_json() and request.get_json()["limit"] > 0:
	# 	filtering_params["limit"] = request.get_json()["limit"]
	# # if limit is not None and gt. than zero then apply it
	

	filtering_params = {
		"filter_name"	:	"title_like"
		, "filter_value":	""			# to get list of all
	}

	response_filtered = requests.get(
		request_url_for_filtering_books
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
				, request_url_for_filtering_books
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


# =============================== [ END ROUTES ] ==============================
