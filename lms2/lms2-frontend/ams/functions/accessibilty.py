# ============================= [ START IMPORTS ] =============================

# flask functionalities
from flask import current_app as app
from flask import session

# to handle requests
import requests

# to handle file operations
from os.path import join as path_join
from os import makedirs, removedirs

# to restrict with a login
from .functions import app_logger, login_required, restrict_access

# ============================== [ END IMPORTS ] ==============================


@login_required()
def getAccountDetailsToSession(return_details: bool = False) -> bool:
	tmp = session["app_user"]["access_token"]

	response_acc_details = requests.get(
		"http://127.0.0.1:5000/api/v2/user/account"
		, json = {
			"action"	:	"account_details"
		}
		, headers	=	{
			"Authorization": "Bearer {}".format(
				tmp
			)
		}
	)

	if response_acc_details.status_code == 206:
		# success
		del session["app_user"]

		session["app_user"]						=	dict()
		session["app_user"]["access_token"]		=	tmp

		response_data = response_acc_details.json()["data"]

		session["app_user"]["user_id"]			=	response_data["user_id"]
		session["app_user"]["role"]				=	response_data["role"]
		session["app_user"]["name"]				=	response_data["name"]
		session["app_user"]["email"]			=	response_data["email"]
		session["app_user"]["gender"]			=	response_data["gender"]
		session["app_user"]["dob"]				=	response_data["dob"]
		session["app_user"]["profile_picture"]	=	"{}/{}".format(
			app.config['ROUTE_TO_GET_PROFILE_PICTURES'], response_data["profile_picture"]
		)
		session['app_user']['pdf_report_setting']=	response_data['pdf_report_setting']

		# details saved.. now back the control
		if return_details:
			return session['app_user']
		else:
			return True
	else:
		return False

@login_required()
@restrict_access({0, 1})
def getDashboardGraphLinks(is_allowed :bool = False):
	if not is_allowed:
		return {}

	data_fetched	=	None

	data_fetched = requests.get(
		"http://127.0.0.1:5000/api/v2/analyze"
		, json = {
			"action": "get_dashboard_graphs"
		}
		, headers	=	{
			"Authorization" : "Bearer {}".format(
				session["app_user"]["access_token"]
			)
		}
	)

	if data_fetched.status_code == 300:
		data = data_fetched.json()["data"]
		file_paths = []

		for d in data:
			try:
				removedirs(
					path_join(
						app.root_path
						, app.config["TEMP_GRAPH_IMAGES_FOLDER"]
					)
				)
			except Exception as e:
				pass
			# removed old graphs

			makedirs(
				path_join(
					app.root_path
					, app.config["TEMP_GRAPH_IMAGES_FOLDER"]
				)
				, exist_ok = True
			)
			# okay.. now
   
			file_paths.append(d)

			with open(path_join(app.root_path, app.config["TEMP_GRAPH_IMAGES_FOLDER"], d), 'wb') as f:
				f.write(eval(data[d]))
   
   		# Now, the images has been saved in the decided temp-graph folder

		if len(file_paths):
			return file_paths

	# something went wrong
	app_logger.critical(
		"A {} request has been made to {} with the data, {} and the response JSON is: {}".format(
			"GET"
			, "http://127.0.0.1:5000/api/v2/analyze"
			, str({"action": "get_dashboard_graphs"})
			, data_fetched.json() if data_fetched.headers["Content-Type"] == "application/json" else data_fetched.content
		)
	)
	# reported to the logger

	return {}
