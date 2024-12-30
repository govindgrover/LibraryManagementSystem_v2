# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# importing flask' current app
from flask import current_app as app

# to handle requests
from flask import request

# to abort the connection when needed
from flask import abort

# importing SQLAlchemy's Error class to handle errors
from sqlalchemy.exc import SQLAlchemyError

# importing Flask Restful-API Resources
from flask_restful import Resource

# importing Flask-JWT methods
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt, get_jwt_identity

# importing Flask-Bcrypt for password hashing
from flask_bcrypt import Bcrypt


# importing UUID4 method to generate random uuids
from uuid import uuid4

# to handle date conversion from string to python' date-object
from datetime import datetime

# to manuplate paths
from os.path import join as path_join
from os import remove as path_remove


# importing required DB Models for current usage
from ..models.DB_Models import (
	Users
)

# importing tracer to trace logins
from ..models.Tracer import Tracer

# importing APIResponse to make responses
from ..models.APIResponse import APIResponse 

# importing to validate user-inputs
from ..models.Validator import Validator

# to handle file upload and retrival
from ..models.ExternalFileManager import ExternalFileManager

# importing logging mechanism
from ..functions.functions import api_logger

from ..models.CacheConfig import api_cache

# ++++++++++++++++++++++++++++++++ END IMPORTS ++++++++++++++++++++++++++++++++

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# importing 'DB' object for querying
from ..models.DB_object import DB
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


# setting-up Bcrypt
bcrypt = Bcrypt(app)

# setting-up tracer
trace_login = Tracer().trace_login

# setting-up validator
validator = Validator()

# setting-up FileManager
fileManager = ExternalFileManager()

# =============================================================================
# ============================ [ AccountResource ] ============================
# =============================================================================

class AccountResource(Resource):
	"""
	This resource class is used to handle the following:
		* Register new user account for the given role
		* Login process
		* Logout process
		* Account deletion 
		* Updating fields; 'name', 'password' & 'profile picture'
		* Getting account details in response
		* Getting profile picture in response

		Direct Database Table(s) used: `users`
	"""

	def __init__(self):
		# getting request JSON
		if request.is_json:
			self.request_action	=	request.get_json()["action"]

			# since sometimes we dont need the key 'body' to be present.
			if "body" in request.get_json():
				self.json_body		=	request.get_json()["body"]

			return
		
		# getting request POST-Form
		elif len(request.form):
			self.request_action	=	request.form.get("action")
			self.request_form	=	request.form

			# since there is possibilty of having file when POST-Form is sent
			self.request_files	=	request.files

			return

		# getting request GET-Parameters
		elif len(request.args) > 0:
			self.get_body		=	request.args

			return

		api_logger.critical(
			"Invalid Request-Data has been sent; ie, neither JSON nor POST-Form nor GET-Parameters. Hence aborted the connection!"
		)
		abort(code = 404)


	def __commit(self):
		"""
		Internal Function to perform 'DB.session.commit()' for any updated
		or inserted records in the database. Mainly, it will also handle
		SQLAlchemyError or any other exception raised during the same followed
		by rollback and log it using the APILogger. Finally, It will return the
		APIResponse as required.
		"""

		try:
			DB.session.commit()
		except SQLAlchemyError or Exception as e:
			api_logger.error(e)
			DB.session.rollback()

			return APIResponse(
				status_code	=	400
				, success	=	False
				, errors	=	[
					"Action could not be performed"
				]
			).get_response()

		return APIResponse(
			status_code	=	204
		).get_response()


	def __invalidActionError(self):
		"""
		Internal Function to return response with `code = 406` if the provided
		'action' in the	JSON Request Body is not avaiable in the system.
		"""

		return APIResponse(
			status_code	=	404		# bad request
			, success	=	False
			, errors	=	[
				"API Request body for the given endpoint does not found!"
			]
		).get_response()


	def __response_invalid_given_value(self, err = "Unknown"):
		"""
		Internal Function to return response with `status code 406` and `err`
		whenever the user provided some invalid input values.
		"""

		return APIResponse(
			status_code	=	406
			, success	=	False
			, errors	= [
				err
			]	
		).get_response()


	def get(self):
		"""
		To process GET Method
		"""

		if self.request_action == "account_details":
			return self._return_account_details()
	
		return self.__invalidActionError()


	def post(self):
		"""
		To process POST Method
		"""

		if self.request_action == "update":
			return self._update()

		elif self.request_action == "update_report_preference":
			return self._update_report_preference()

		elif self.request_action == "login":
			return self._login()
		
		elif self.request_action == "logout":
			return self._logout()

		return self.__invalidActionError()


	def put(self):
		"""
		To process PUT Method
		"""

		if self.request_action == "register":
			return self._register()

		return self.__invalidActionError()


	def delete(self):
		"""
		To process DELETE Method
		"""

		if self.request_action == "delete":
			return self._delete()

		return self.__invalidActionError()


	def _register(self):
		"""
		Internal Function to create a new user account provided the following
		details in the JSON Request Body:
			<role, name, email, password, gender, dob>;
		"""

		if not validator.is_email(self.json_body["email"]):
			return self.__response_invalid_given_value(err = "Given E-Mail ID is not ok")
		# check done

		if not validator.is_name(self.json_body["name"]):
			return self.__response_invalid_given_value(err = "Given Name is not ok")
		# check done

		if not validator.is_password(self.json_body["password"]):
			return self.__response_invalid_given_value(err = "Given Password is not ok")
		# check done

		if not validator.is_gender(self.json_body["gender"]):
			return self.__response_invalid_given_value(err = "Given Gender is not ok")
		# check done

		check_email = DB.session.query(Users).filter_by(
			email = self.json_body["email"]
		).all()

		if len(check_email) > 0:
			return APIResponse(
				status_code	=	406
				, success	=	False
				, errors	=	[
					"E-Mail ID already registered"
				]
			).get_response()
		# thus the given email is not yet registered... Good! 

		create_acc = Users(
			user_id				=	str(uuid4())
			, role				=	self.json_body["role"]
			, name				=	self.json_body["name"]
			, email				=	self.json_body["email"]
			, password			=	bcrypt.generate_password_hash(self.json_body["password"])
			, gender			=	self.json_body["gender"]
			, dob				=	datetime.strptime(self.json_body["dob"], "%d-%m-%Y")
			, profile_picture	=	app.config["DEFAULT_PROFILE_PICTURE_FILENAME"]
		)

		DB.session.add(create_acc)

		return self.__commit()
	

	def _login(self):
		"""
		Internal Function to login a existing user account provided details
		in the JSON Request Body:
			<role, email, password>;

		It will then, create a JWT Access Token and send it in the response.
		"""

		# if self.json_body["role"] not in app.config["AVAILABLE_USER_ROLES"]:
		# 	return self.__response_invalid_given_value(err = "Given `role` is not ok")
		# # check done

		if not validator.is_email(self.json_body["email"]):
			return self.__response_invalid_given_value(err = "Given E-Mail ID is not ok")
		# check done

		if not validator.is_password(self.json_body["password"]):
			return self.__response_invalid_given_value(err = "Given Password is not ok")
		# check done

		trace_params = {
			"email"			:	self.json_body["email"]
			# , "role"			:	self.json_body["role"]
			, "ip"			:	request.remote_addr
			, "browser"		:	request.user_agent.browser
			, "user_agent"	:	request.user_agent.platform
			, "user_id"		:	""
			, "jwt"			:	""
			, "process"		:	"login"
		}

		found = DB.session.query(Users).filter_by(
			email			=	self.json_body["email"]
			# , role			=	self.json_body["role"]
			, is_active 	=	1
			, is_deleted	=	0
		).all()

		response_success = None

		if len(found) == 1:
			found = found[0]

			if (
				bcrypt.check_password_hash(
					found.password
					, self.json_body["password"]
				)
			):
				# password verified... ok

				jwt_access_token = create_access_token(
					identity			=	found.user_id
					, additional_claims	=	{
						"role"		:	found.role
						, "name"	:	found.name
						, "email"	:	found.email
					}
				)
				# token created

				# setting up trace params
				trace_params["user_id"]	=	found.user_id
				trace_params["role"]	=	found.role
				trace_params["jwt"]		=	jwt_access_token

				# making response
				response_success = APIResponse(
					status_code =	206
					, success	=	True
					, data		=	{
						"token": jwt_access_token
					}
				)
			else:
				response_failure = APIResponse(
					status_code =	401
					, success	=	False
					, errors	=	[
						"Invalid Credentials!"
					]
				)
		else:
			response_failure = APIResponse(
				status_code =	404
				, success	=	False
				, errors	=	[
					"User not found!"
				]
			)

		# tracing
		trace_login(trace_params)

		# sending response
		if response_success != None:
			return response_success.get_response()
		else:
			return response_failure.get_response()


	@jwt_required()
	def _logout(self):
		"""
		Internal Function to logout user
		"""

		# tracing logout
		traced = trace_login({
			"process"		:	"logout"
			, "role"		:	get_jwt()["role"]
			, "email"		:	""
			, "password"	:	""
			, "ip"			:	request.remote_addr
			, "browser"		:	request.user_agent.browser
			, "user_agent"	:	request.user_agent.platform
			, "user_id"		:	get_jwt_identity()
			, "jwt"			:	""
		})
		
		# making response
		return APIResponse(
			status_code =	204 if traced else 400
		).get_response()


	@jwt_required()
	def _update(self):
		"""
		Internal Function to update given user's specific details
		"""

		# fetching current user into system
		current_user = DB.session.query(Users).filter_by(
			user_id	=	get_jwt_identity()
		).first()
		# this could not be empty or null; since the user has logged-in
		# but given a special case, when the admin has taken a certain action
		# after the given user logged-in, then in that, the action will only
		# force after/on the re-login by the user.

		if hasattr(self, "json_body") and len(self.json_body):
			if self.json_body["field_to_update"] == "name":
				if not validator.is_name(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given Name is not ok")
				# check done

				# performing the change
				current_user.name =	self.json_body["new_value"]

			elif self.json_body["field_to_update"] == "password":
				if not validator.is_password(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given Password is not ok")
				# check done

				# performing the change
				current_user.password =	bcrypt.generate_password_hash(self.json_body["new_value"])

		elif hasattr(self, "request_form") and self.request_form["field_to_update"] == "pic":
			# performing the change
			uploadedFile = self.request_files.get("new_value")

			u = fileManager.upload(
				uploadedFile
				, app.config["UPLOADED_PICTURES_DIRRECTORY"]
			)

			if not u["success"]:
				return APIResponse(
					success			=	False
					, status_code	=	400
					, errors		=	[
						u["error"]
					]
				).get_response()


			# deleting old file
			if current_user.profile_picture is not None and current_user.profile_picture != app.config["DEFAULT_PROFILE_PICTURE_FILENAME"]:
				path_remove(
					path_join(
						app.config["UPLOAD_FOLDER"]
						, app.config["UPLOADED_PICTURES_DIRRECTORY"]
						, current_user.profile_picture
					)
				)

			# file placed onto the disk
			current_user.profile_picture =	u["filename"]
		else:
			return self.__invalidActionError()
		
		return self.__commit()


	@jwt_required()
	def _delete(self):
		"""
		Internal Function to set delete = 1 for the given user by the
		supplied JWT.
		"""

		# fetching current user into system
		theUser = DB.session.query(Users).filter_by(
			user_id			=	get_jwt_identity()
			, is_active		=	1
			, is_deleted	=	0
		).first()

		# performing change
		theUser.is_deleted = 1

		return self.__commit()


	@jwt_required()
	@api_cache.cached(key_prefix='ch_return_account_details')
	def _return_account_details(self):
		"""
		Internal Function to return a `dict` in response's data containing the
		account's information where `user_id` is taken from the JWT.
		"""

		accDetails = dict()

		acc = DB.session.query(Users).filter(
			Users.user_id		==	get_jwt_identity()
			, Users.is_active	==	1
			, Users.is_deleted	==	0
		).one_or_none()

		if acc is not None:
			accDetails["user_id"]			=	acc.user_id
			accDetails["role"]				=	acc.role
			accDetails["name"]				=	acc.name
			accDetails["email"]				=	acc.email
			accDetails["gender"]			=	acc.gender
			accDetails["dob"]				=	datetime.strftime(acc.dob, "%d-%m-%Y")
			accDetails["profile_picture"]	=	acc.profile_picture
			accDetails['pdf_report_setting']=	acc.prefer_pdf_monthly_report
		else:
			return APIResponse(
				status_code	=	404
				, success	=	False
				, errors	=	[
					"The details you are looking for does not exists!"
				]
			).get_response()


		return APIResponse(
			status_code	=	206
			, data = accDetails
		).get_response()
	
	@jwt_required()
	def _update_report_preference(self):
		setting = DB.session.query(
			Users
		).filter(
			Users.user_id == get_jwt_identity()
		).one()

		if hasattr(self, "json_body") and len(self.json_body):
			if self.json_body["field_to_update"] == "monthly_report_format":
				setting.prefer_pdf_monthly_report = self.json_body['new_value']
		else:
			return self.__invalidActionError()

		return self.__commit()
