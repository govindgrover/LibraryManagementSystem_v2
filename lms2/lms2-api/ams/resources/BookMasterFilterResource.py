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


# importing required DB Models for current usage
from ..models.DB_Models import (
	Authors, Category, Genre
	, Language, Publisher
)

# importing APIResponse to make responses
from ..models.APIResponse import APIResponse 

# importing to validate user-inputs
from ..models.Validator import Validator

# importing logging mechanism
from ..functions.functions import api_logger

# importing decorator fn. to restrict the operations taken out by users based
# on their roles.
from ..functions.functions import role_restriction

from ..models.CacheConfig import api_cache

# ++++++++++++++++++++++++++++++++ END IMPORTS ++++++++++++++++++++++++++++++++

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# importing 'DB' object for querying
from ..models.DB_object import DB
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


# setting-up validator
validator = Validator()


# =============================================================================
# ======================== [ BookMasterFilterResource ] =======================
# =============================================================================

class BookMasterFilterResource(Resource):
	"""
	This resource class is used to handle the following:
		* Get response with filtered master's details produced by the provided
		filter.

		Direct Database Table(s) used:
			`authors`, `category`,`genre`, `language`, `publisher`
	"""

	"""
	This dictonary contains the keys which are as-it-is provided to the
	user/client to send as the GET-Param in the API Request to easily access
	their specific DB Models in the system and their corrosponding
	"<MASTER>_id".
	"""
	MASTER_NAMES_WITH_DB_MODEL :dict = {
		"publisher"		:	{
			"model"			:	Publisher
			, "id_attr_name":	"publisher_id"
		}
		, "author"		:	{
			"model"			:	Authors
			, "id_attr_name":	"author_id"
		}
		, "language"	:	{
			"model"			:	Language
			, "id_attr_name":	"lang_id"
		}
		, "genre"		:	{
			"model"			:	Genre
			, "id_attr_name":	"genre_id"
		}
		, "category"	:	{
			"model"			:	Category
			, "id_attr_name":	"category_id"
		}
	}


	"""
	This set contains all of the valid filter-names that the user/client
	can request and each one of them have their own defined format for the
	respective values that is needed in order to let the function perform
	the requiered search. 
	"""
	DEFINED_MASTER_FILTERS :set = {
		"since_date_between"

		, "name_like"

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
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_FETCH_MASTER_DETAILS"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def get(self, master_name :str):
		"""
		To process GET Method
		"""

		if master_name not in self.MASTER_NAMES_WITH_DB_MODEL:
			return self.__invalidActionError()

		if (not(("master_id" in self.get_body)
				^
			({"filter_name", "filter_value"}.issubset(set(self.get_body)))
		)):
			# raise this response if neither `master_id` nor `filter_name` &
			# `filter_value` is present in the GET params using "inverted XOR"
			return self.__invalidActionError()
		
		# checking for roles
		if "master_id" in self.get_body:
			masterData = self.__fetch_single_master(master_name, given_master_id = self.get_body["master_id"])

			if len(masterData) > 0:
				return APIResponse(
					status_code	=	302
					, data = masterData
				).get_response()
				# returned the data in the response
			else:
				return APIResponse(
					status_code	=	404
					, success	=	False
					, errors	=	[
						"The master(s) you are looking for does not exists!"
					]
				).get_response()
				# returned the response when master is not found

		elif self.get_body["filter_name"] is not None:
			masterData = self._fetch_masters_using_filter(master_name)

			if type(masterData) == Response:
				return masterData

			elif len(masterData) <= 0:
				return APIResponse(
					status_code	=	404
					, success	=	False
					, errors	=	[
						"The master(s) you are looking for does not exists!"
					]
				).get_response()
				# returned the response when master is not found
			else:
				return APIResponse(
					status_code	=	302
					, data = masterData
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
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_FETCH_MASTER_DETAILS"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def __getSingleRecordFromTheModels(self, MasterModel, attr_name, value_to_check):
		"""
		This Internal Function returns the records such that they belongs to
		the specified 'Master' (`MasterModel`) using its attribute name,
		`attr_name` with comparision to	`value_to_check` and further the
		resultant depends upon the role of user who requested the details.
		"""

		if get_jwt()["role"] == 0:
			# ADMIN
			return (
				DB.session.query(MasterModel).filter(
					getattr(MasterModel, attr_name) == value_to_check
				).one_or_none()
			)

		elif get_jwt()["role"] == 1:
			# LIBRARIAN
			return (
				DB.session.query(MasterModel).filter(
					getattr(MasterModel, attr_name) == value_to_check
					, getattr(MasterModel, "is_deleted") == 0
				).one_or_none()
			)

		elif get_jwt()["role"] == 2:
			# USER
			return (
				DB.session.query(MasterModel).filter(
					getattr(MasterModel, attr_name) == value_to_check
					, getattr(MasterModel, "is_deleted") == 0
					, getattr(MasterModel, "is_active") == 1
				).one_or_none()
			)
		
		else:
			return []


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_FETCH_MASTER_DETAILS"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def __fetch_single_master(self, master_name :str, given_master_id :str) -> dict:
		"""
		This Internal Function returns all required details of any 'master'
		given its `<MASTER>_id` and further we are assuming that the provided
		`<MASTER>_id` has already been exists in the database to avoid further
		checks and thus lowering the time consumption in camparisions.

		Also, this function returns the details specific to the user's role
		who requested the details. And in case of undesirable role caught,
		the system will log it in using the APILogger and return empty list.
		"""

		# okay... we have to provide details for only the given 'master_id'
		rdata = dict()

		record = self.__getSingleRecordFromTheModels(
			self.MASTER_NAMES_WITH_DB_MODEL[master_name]["model"]
			, self.MASTER_NAMES_WITH_DB_MODEL[master_name]["id_attr_name"]
			, given_master_id
		)

		if get_jwt()["role"] == 0:
			# ADMIN

			# we are using try-except here because we are checking weather the
			# book exists or not later... so if it is None then all is well...
			try:
				"""
				In future updates this section could be enabled after setting
				it up in the database and the associated SQLAlchemy Models.
				"""
				# rdata["added_by"]			=	record.added_by

				rdata["is_active"]			=	record.is_active
				rdata["is_deleted"]			=	record.is_deleted
				rdata["uploaded_on"]		=	record.current_timestamp
				rdata["last_updated_on"]	=	record.last_updated_timestamp
			except:
				pass

		elif get_jwt()["role"] == 1:
			# LIBRARIAN

			# we are using try-except here because we are checking weather the
			# book exists or not later... so if it is None then all is well...
			try:
				rdata["is_active"]		=	record.is_active
				rdata["uploaded_on"]	=	record.current_timestamp
			except:
				pass

		elif get_jwt()["role"] == 2:
			# USER

			pass
		
		else:
			# something went wrong
			api_logger.exception(
				"Something went wrong for the provided master = {} and master_id = {}\nThe role in jwt is {}".format(
					master_name
					, self.get_body.get("master_id")
					, get_jwt()["role"]
				)
			)
		# end check for roles

		if record is None:
			return []
		# end check for master existance

		# Now, here we can modify what attributes are to be given to user

		rdata[self.MASTER_NAMES_WITH_DB_MODEL[master_name]["id_attr_name"]] = getattr(record, self.MASTER_NAMES_WITH_DB_MODEL[master_name]["id_attr_name"])
		# basically has happened is the above line has created a key-value pair
		# in 'rdata' which will be the the '<master>_id' and will have the
		# respective value.

		rdata["name"]			=	record.name

		if master_name == "publisher":
			# only for Publisher
			rdata["desc"]			=	record.desc

		if master_name == "author":
			# only for Author
			rdata["bio"]			=	record.biography

		return rdata


	decorators = [
		role_restriction(app.config["AVAILABLE_USER_ROLES"] if app.config["DEBUG"] else [0, 1])
		, jwt_required(optional = app.config["TESTING"])
	]
	def __getMastersWithActiveStatues(self, Model, is_active :bool) -> tuple:
		"""
		This Internal Function returns the tuple of records of the requested
		master such that it satisfy the criterion,
			`<MASTER_MODEL_NAME>.is_active = is_active`.

		The aim to seprate this functionality is to restrict the access to a
		specified role
		"""

		return tuple(
			DB.session.query(Model).filter(
				getattr(Model, "is_active") == is_active
			).all()
		)


	decorators = [
		role_restriction(app.config["AVAILABLE_USER_ROLES"] if app.config["DEBUG"] else [0])
		, jwt_required(optional = app.config["TESTING"])
	]
	def __getMastersWithDeletedStatues(self, Model, is_deleted :bool) -> tuple:
		"""
		This Internal Function returns the tuple of records of the requested
		master such that it satisfy the criterion,
			`<MASTER_MODEL_NAME>.is_deleted = is_deleted`.

		The aim to seprate this functionality is to restrict the access to a
		specified role
		"""

		return tuple(
			DB.session.query(Model).filter(
				getattr(Model, "is_deleted") == is_deleted
			).all()
		)


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_FETCH_MASTER_DETAILS"])
		, jwt_required(optional = app.config["TESTING"])
		, api_cache.memoize(app.config['CACHE_DEFAULT_TIMEOUT'])
	]
	def _fetch_masters_using_filter(self, master_name: str) -> tuple:
		"""
		The Internal Function returns a tuple of data which contains the
		requested filtered records with-respect-to the provided `master_name`.
		"""

		if self.get_body["filter_name"] not in self.DEFINED_MASTER_FILTERS:
			return self.__response_invalid_given_value("Invalid `filter_name`")

		filteredRecords = []

		if self.get_body["filter_name"] == "name_like":
			filtered_master_ids = DB.session.query(
				self.MASTER_NAMES_WITH_DB_MODEL[master_name]["model"]
			).filter(
				getattr(self.MASTER_NAMES_WITH_DB_MODEL[master_name]["model"], "name").like("%{}%".format(
					self.get_body["filter_value"]
				))
			)

		elif self.get_body["filter_name"] == "since_date_between":
			tmp = self.get_body["filter_value"].split(',')

			after_date	=	datetime.strptime(tmp[0].strip()[1::], "%d-%m-%Y")
			before_date	=	datetime.strptime(tmp[1].strip()[0:-1], "%d-%m-%Y")

			filtered_master_ids = DB.session.query(
				self.MASTER_NAMES_WITH_DB_MODEL[master_name]["model"]
			).filter(
				getattr(
					self.MASTER_NAMES_WITH_DB_MODEL[master_name]["model"]
					, "current_timestamp"
				) >= after_date
				, getattr(
					self.MASTER_NAMES_WITH_DB_MODEL[master_name]["model"]
					, "current_timestamp"
				) <= before_date
			)

		elif self.get_body["filter_name"] == "active_status":
			filtered_master_ids = self.__getMastersWithActiveStatues(
				Model		=	self.MASTER_NAMES_WITH_DB_MODEL[master_name]["model"]
				, is_active =	self.get_body["filter_value"]
			)

		elif self.get_body["filter_name"] == "deleted_status":
			filtered_master_ids = self.__getMastersWithDeletedStatues(
				Model			=	self.MASTER_NAMES_WITH_DB_MODEL[master_name]["model"]
				, is_deleted	=	self.get_body["filter_value"]
			)


		for master in filtered_master_ids:
			tmp = self.__fetch_single_master(
					master_name
					, getattr(master, self.MASTER_NAMES_WITH_DB_MODEL[master_name]["id_attr_name"])
			)

			if tmp is not None and len(tmp):
				filteredRecords.append(tmp)

		return tuple(filteredRecords)
		# returned filtered records
