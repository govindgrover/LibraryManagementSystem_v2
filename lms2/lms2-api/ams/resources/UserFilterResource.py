# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# importing flask' current app
from flask import current_app as app

# to handle requests
from flask import request

# to check
from flask import Response

# to abort the connection when needed
from flask import abort

# importing Flask Restful-API Resources
from flask_restful import Resource

# importing Flask-JWT methods
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt


# to handle date conversion from string to python' date-object
from datetime import datetime

# to join path for any OS
from os.path import join as path_join

# importing required DB Models for current usage
from ..models.DB_Models import (
	Users
)

# importing APIResponse to make responses
from ..models.APIResponse import APIResponse 

# importing to validate user-inputs
from ..models.Validator import Validator

# to handle file upload and retrival
from ..models.ExternalFileManager import ExternalFileManager

# importing logging mechanism
from ..functions.functions import api_logger

# importing decorator fn. to restrict the operations taken out by users based
# on their roles.
from ..functions.functions import role_restriction

# ++++++++++++++++++++++++++++++++ END IMPORTS ++++++++++++++++++++++++++++++++

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# importing 'DB' object for querying
from ..models.DB_object import DB
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


# setting-up validator
validator = Validator()

# setting-up FileManager
fileManager = ExternalFileManager()


# =============================================================================
# =========================== [ UserFilterResource ] ==========================
# =============================================================================

class UserFilterResource(Resource):
	"""
	This resource class is used to handle the following:
		* Get response with filtered user's details produced by the provided
		filter.

		Direct Database Table(s) used: `users`
	"""

	"""
	This set contains all of the valid filter-names that the user/client
	can request and each one of them have their own defined format for the
	respective values that is needed in order to let the function perform
	the requiered search. 
	"""
	DEFINED_MASTER_FILTERS :set = {
		"role"

		, "email_like"
		, "name_like"

		, "gender"

		, "dob_equals"
		, "dob_between_dates"
		, "registered_between_dates"

		, "active_status"
		, "deleted_status"
	}


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


	def __invalidActionError(self):
		"""
		Internal Function to return response with `code = 406` if the provided
		'action' in the	JSON Request Body is not avaiable in the system.
		"""

		return APIResponse(
			status_code	=	406		# not acceptable
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


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_FETCH_USERS_DETAILS"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def __fetch_single_user(self, given_user_id :str) -> dict:
		"""
		This Internal Function returns all required details of any user given
		its `user_id` and further we are assuming that the provided `user_id`
		has already been exists in the database to avoid further checks and
		thus lowering the time consumption in camparisions.

		Also, this function returns the details specific to the user's role
		who requested the details. And in case of undesirable role caught,
		the system will log it in using the APILogger and return empty dict.
		"""

		# okay... we have to provide details for only the given 'user_id'
		rdata = dict()

		if get_jwt()["role"] == 0:
			# ADMIN

			record = DB.session.query(Users).filter(
				Users.user_id == given_user_id
			).one_or_none()

			# we are using try-except here because we are checking weather the
			# book exists or not later... so if it is None then all is well...
			try:
				rdata["is_active"]			=	record.is_active
				rdata["is_deleted"]			=	record.is_deleted
				rdata["account_created_on"]	=	record.current_timestamp
				rdata["last_updated_on"]	=	record.last_updated_timestamp
			except:
				pass

		elif get_jwt()["role"] == 1:
			# LIBRARIAN

			record = DB.session.query(Users).filter(
				Users.user_id		==	given_user_id
				, Users.is_deleted	==	0
				, Users.role		==	2	#Lib' can only view 'role 2' users
			).one_or_none()

			# we are using try-except here because we are checking weather the
			# book exists or not later... so if it is None then all is well...
			try:
				rdata["is_active"]		=	record.is_active
			except:
				pass
		else:
			# something went wrong
			api_logger.exception(
				"Something went wrong, the user is not allowed to access this subsystem of the application;\nthe provided user_id = {}\nThe role in jwt is {}".format(
					self.get_body["user_id"]
					, get_jwt()["role"]
				)
			)
		# end check for roles

		if record is None:
			return dict()


		if record.profile_picture is not None:
			rdata["profile_picture"]	=	record.profile_picture
		else:
			# default image
			rdata["profile_picture"]	=	app.config["DEFAULT_PROFILE_PICTURE_FILENAME"]

		# Now, here we can modify what attributes are to be given to user
		rdata["user_id"]		=	record.user_id
		rdata["role"]			=	record.role
		rdata["name"]			=	record.name
		rdata["email"]			=	record.email
		rdata["gender"]			=	record.gender
		rdata["dob"]			=	record.dob

		return rdata


	decorators = [
		role_restriction(app.config["AVAILABLE_USER_ROLES"] if app.config["DEBUG"] else [0, 1])
		, jwt_required(optional = app.config["TESTING"])
	]
	def __getUsersWithActiveStatues(self, is_active :bool) -> tuple:
		"""
		This Internal Function returns the tuple of records of users such that
		they satisfy the criterion, `Users.is_active = is_active`.

		The aim to seprate this functionality is to restrict the access to a
		specified role
		"""

		return tuple(
			DB.session.query(Users).filter(
				Users.is_active == is_active
			).limit(
				self.__record_limit
			).all()
		)


	decorators = [
		role_restriction(app.config["AVAILABLE_USER_ROLES"] if app.config["DEBUG"] else [0])
		, jwt_required(optional = app.config["TESTING"])
	]
	def __getUsersWithDeletedStatues(self, is_deleted :bool) -> tuple:
		"""
		This Internal Function returns the tuple of records of users such that
		they satisfy the criterion, `Users.is_deleted = is_deleted`.

		The aim to seprate this functionality is to restrict the access to a
		specified role
		"""

		return tuple(
			DB.session.query(Users).filter(
				Users.is_deleted == is_deleted
			).limit(
				self.__record_limit
			).all()
		)


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_FETCH_USERS_DETAILS"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def get(self):
		"""
		To process GET Method
		"""
		if (not(("user_id" in self.get_body)
				^
			({"filter_name", "filter_value"}.issubset(set(self.get_body)))
		)):
			# raise this response if neither `user_id` nor `filter_name` &
			# `filter_value` is present in the GET params using "inverted XOR"
			return self.__invalidActionError()
		
		# checking for roles
		if "user_id" in self.get_body:
			userData = self.__fetch_single_user(given_user_id = self.get_body["user_id"])

			if len(userData) > 0:
				return APIResponse(
					status_code	=	302
					, data = userData
				).get_response()
				# returned the data in the response
			else:
				return APIResponse(
					status_code	=	404
					, success	=	False
					, errors	=	[
						"The user(s) you are looking for does not exists!"
					]
				).get_response()
				# returned the response when master is not found

		elif self.get_body["filter_name"] is not None:

			self.__record_limit = app.config["LIMIT_MAX_FETCH_RECORDS"]
			# default limiting the records to be fetched.. to avoid system-hand
			# and also bandwidth

			if "limit" in self.get_body:
				try:
					self.__record_limit = int(self.get_body["limit"])
					# overwriting the provided limit
				except ValueError:
					return self.__response_invalid_given_value("Invalid `limit` value")
			# ok.. the given limit have been set

			userData = self._fetch_users_using_filter()

			if type(userData) == Response:
				return userData

			elif len(userData) <= 0:
				return APIResponse(
					status_code	=	404
					, success	=	False
					, errors	=	[
						"The user(s) you are looking for does not exists!"
					]
				).get_response()
				# returned the response when master is not found
			else:
				return APIResponse(
					status_code	=	302
					, data = userData
				).get_response()
				# returned the data in the response
		else:
			api_logger.exception(
				"Something went wrong here. Given the `get_body` is: {}".format(
					self.get_body
				)
			)

			return APIResponse(
				status_code	=	400
				, success	=	False
				, errors	=	[
					"Something went wrong! Contact developer."
				]
			).get_response()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_FETCH_USERS_DETAILS"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _fetch_users_using_filter(self):
		if self.get_body["filter_name"] not in self.DEFINED_MASTER_FILTERS:
			return self.__response_invalid_given_value("Invalid `filter_name`")

		filteredRecords = []

		if self.get_body["filter_name"] == "name_like":
			filtered_user_ids = DB.session.query(
				Users
			).filter(
				Users.name.like("%{}%".format(
					self.get_body["filter_value"]
				))
			).limit(
				self.__record_limit
			).all()

		elif self.get_body["filter_name"] == "registered_between_dates":
			tmp = self.get_body["filter_value"].split(',')

			from_date	=	datetime.strptime(tmp[0].strip()[1::], "%d-%m-%Y")
			to_date		=	datetime.strptime(tmp[1].strip()[0:-1], "%d-%m-%Y")

			filtered_user_ids = DB.session.query(
				Users
			).filter(
				Users.current_timestamp >= from_date
				, Users.current_timestamp <= to_date
			).limit(
				self.__record_limit
			).all()

		elif self.get_body["filter_name"] == "dob_between_dates":
			tmp = self.get_body["filter_value"].split(',')

			from_date	=	datetime.strptime(tmp[0].strip()[1::], "%d-%m-%Y")
			to_date		=	datetime.strptime(tmp[1].strip()[0:-1], "%d-%m-%Y")

			filtered_user_ids = DB.session.query(
				Users
			).filter(
				Users.dob >= from_date
				, Users.dob <= to_date
			).limit(
				self.__record_limit
			).all()

		elif self.get_body["filter_name"] == "active_status":
			filtered_user_ids = self.__getUsersWithActiveStatues(
				is_active =	self.get_body["filter_value"]
			)

		elif self.get_body["filter_name"] == "deleted_status":
			filtered_user_ids = self.__getUsersWithDeletedStatues(
				is_deleted	=	self.get_body["filter_value"]
			)

		elif self.get_body["filter_name"] == "email_like":
			filtered_user_ids = DB.session.query(
				Users
			).filter(
				Users.email.like("%{}%".format(
					self.get_body["filter_value"]
				))
			).limit(
				self.__record_limit
			).all()

		elif self.get_body["filter_name"] == "gender":
			filtered_user_ids = DB.session.query(
				Users
			).filter(
				Users.gender == self.get_body["filter_value"]
			).limit(
				self.__record_limit
			).all()

		elif self.get_body["filter_name"] == "role":
			filtered_user_ids = DB.session.query(
				Users
			).filter(
				Users.role == self.get_body["filter_value"]
			).limit(
				self.__record_limit
			).all()


		for user in filtered_user_ids:
			filteredRecords.append(
				self.__fetch_single_user(
					user.user_id
				)
			)

		return tuple(filteredRecords)
		# returned filtered records
