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
from flask_jwt_extended import get_jwt


# importing UUID4 method to generate random uuids
from uuid import uuid4


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

# ++++++++++++++++++++++++++++++++ END IMPORTS ++++++++++++++++++++++++++++++++

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# importing 'DB' object for querying
from ..models.DB_object import DB
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


# setting-up validator
validator = Validator()


# =============================================================================
# ====================== [ BookMasterOperationalResource ] ====================
# =============================================================================

class BookMasterOperationalResource(Resource):
	"""
	This resource class is used to handle the following:
		* Add a new record to any book master table
		* updating its fields
		* deleteting it by setting, `is_deleted` to `1`

		Direct Database Table(s) used: 
		`authors`, `category`,`genre`, `language`, `publisher`
	"""

	"""
	This dictonary contains the keys which are as-it-is provided to the
	user/client to send as the GET-Param in the API Request to easily access
	their specific DB Models in the system and their corrosponding
	"<MASTER>_id".

	Further, the value corrosponding the the respective key is a tuple with
	0-th index value as same the key (this is because it makes it possible to
	change the GET-Params without affecting the table name). While the value at
	1-th index is the name of the function in this (self) Resource Class that
	handles the process of the specified master.
	"""
	MASTER_COMPONENTS : dict = {
		"publisher"		:	("publisher", "_add_publisher")
		, "language"	:	("language", "_add_language")
		, "category"	:	("category", "_add_category")
		, "genre"		:	("genre", "_add_genre")
		, "author"		:	("author", "_add_author")
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

	
	def __check_existing_record(self, Model, attr, attr_val) -> bool:
		"""
		This Internal Funciton checks weather there exists any record such that
		, it satisfy the following criteria,
			the requested `attr` of the `Model` have the value as `attr_val`
			or not.
		"""

		like = getattr(Model, attr).like(
			"{}".format(
					attr_val
				)
			)
		
		result = DB.session.query(Model).filter(like).count()

		return True if result > 0 else False


	def __record_existance_response(self, should_not_exists : bool = True):
		"""
		This Internal Function gives two distinctive responses in two different
		situations that is when `should_not_exists = 1` then it means
		"""

		return APIResponse(
			status_code	=	406
			, success	=	False
			, errors	=	[
				"Provided name already exists !" if (should_not_exists) else "Provided name does not exists !"
			]
		).get_response()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_MASTER"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def put(self, component_name):
		"""
		To process PUT Method
		"""

		if component_name not in self.MASTER_COMPONENTS.keys():
			response_invalid_data = APIResponse(
				status_code	=	406
				, success	=	False
				, errors	=	[
					"Invalid component_name"
				]
			)

			return response_invalid_data.get_response()
		# hence, the provided Master component_name is ok...

		if self.request_action == "add":
			return self._add_new(component_name)

		return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_MASTER"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def post(self, component_name):
		"""
		To process POST Method
		"""

		if component_name not in self.MASTER_COMPONENTS.keys():
			response_invalid_data = APIResponse(
				status_code	=	406
				, success	=	False
				, errors	=	[
					"Invalid component_name"
				]
			)

			return response_invalid_data.get_response()
		# hence, the provided Master component_name is ok...

		if self.request_action == "update":
			return self._update(component_name)


		return self.__invalidActionError()
	
	
	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_MASTER"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def delete(self, component_name):
		"""
		To process DELETE Method
		"""

		if self.request_action == "delete":
			return self._delete(component_name)

		return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_MASTER"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _add_new(self, compo):
		"""
		Internal Function to create a new record for the given 'master' and its
		data in the `self.json_body`.
		"""

		if compo == "publisher" and "publisher_desc" in self.json_body and "publisher_name" in self.json_body:

			# checking if the provided name exists in the `Publisher` or not
			if self.__check_existing_record(Publisher, "name", self.json_body["publisher_name"]):
				return self.__record_existance_response()

			if not validator.is_name(self.json_body["publisher_name"]):
				return self.__response_invalid_given_value(err = "Given publisher name is not ok")

			if not validator.is_long_text(self.json_body["publisher_desc"]):
				return self.__response_invalid_given_value(err = "Given publisher description is not ok")


			new = Publisher(
				publisher_id	=	str(uuid4())
				, name			=	self.json_body["publisher_name"]
				, desc			=	self.json_body["publisher_desc"]
				, is_active		=	1 if (app.config["TESTING"] or get_jwt()["role"] == 0) else 0
			)
			# creating new publisher
		
		elif compo == "author" and "author_name" in self.json_body and "author_bio" in self.json_body:

			# checking if the provided name exists in the `Authors` or not
			if self.__check_existing_record(Authors, "name", self.json_body["author_name"]):
				return self.__record_existance_response()

			if not validator.is_name(self.json_body["author_name"]):
				return self.__response_invalid_given_value(err = "Given author name is not ok")

			if not validator.is_long_text(self.json_body["author_bio"]):
				return self.__response_invalid_given_value(err = "Given author biography is not ok")


			new = Authors(
				author_id	=	str(uuid4())
				, name		=	self.json_body["author_name"]
				, biography	=	self.json_body["author_bio"]
			)
			# creating new author

		elif compo == "language" and "language_name" in self.json_body:

			# checking if the provided name exists in the `Language` or not
			if self.__check_existing_record(Language, "name", self.json_body["language_name"]):
				return self.__record_existance_response()

			if not validator.is_name(self.json_body["language_name"]):
				return self.__response_invalid_given_value(err = "Given language name is not ok")


			new = Language(
				lang_id		=	str(uuid4())
				, name		=	self.json_body["language_name"]
				, is_active	=	1 if (app.config["TESTING"] or get_jwt()["role"] == 0) else 0
			)
			# creating new language

		elif compo == "category" and "category_name" in self.json_body:

			# checking if the provided name exists in the `Language` or not
			if self.__check_existing_record(Category, "name", self.json_body["category_name"]):
				return self.__record_existance_response()

			if not validator.is_name(self.json_body["category_name"]):
				return self.__response_invalid_given_value(err = "Given category name is not ok")

			new = Category(
				category_id		=	str(uuid4())
				, name			=	self.json_body["category_name"]
				, is_active		=	1 if (app.config["TESTING"] or get_jwt()["role"] == 0) else 0
			)
			# creating new category

		elif compo == "genre" and "genre_name" in self.json_body:

			# checking if the provided name exists in the `Genre` or not
			if self.__check_existing_record(Genre, "name", self.json_body["genre_name"]):
				return self.__record_existance_response()

			if not validator.is_name(self.json_body["genre_name"]):
				return self.__response_invalid_given_value(err = "Given genre name is not ok")

			new = Genre(
				genre_id		=	str(uuid4())
				, name			=	self.json_body["genre_name"]
				, is_active		=	1 if (app.config["TESTING"] or get_jwt()["role"] == 0) else 0
			)
			# creating new genre
		
		else:
			return self.__invalidActionError()

		# endif

		DB.session.add(new)
		# provided the same to DB session for creating 'new' record

		return self.__commit()
		# commited

	
	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_MASTER"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _update(self, compo):
		"""
		Internal Function to update a existing record for the given 'master'
		and its	data in the `self.json_body`.
		"""

		if compo == "publisher" and "publisher_id" in self.json_body:

			to_update = DB.session.query(Publisher).filter_by(
				publisher_id = self.json_body["publisher_id"]
				, is_deleted = 0
			).first()
			# got the record to be update

			if self.json_body["field_to_update"] == "name":
				if not validator.is_name(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given name is not ok")
				# check done
				
				to_update.name = self.json_body["new_value"]
			elif self.json_body["field_to_update"] == "desc":
				if not validator.is_long_text(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given desc is not ok")
				# check done

				to_update.desc = self.json_body["new_value"]
			elif self.json_body["field_to_update"] == "active":
				if not validator.is_single_digit(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given active status is not ok")
				# check done

				to_update.is_active = self.json_body["new_value"]
			else:
				return self.__invalidActionError()
			# updating done... going to commit it
		
		elif compo == "author" and "author_id" in self.json_body:
			
			to_update = DB.session.query(Authors).filter_by(
				author_id = self.json_body["author_id"]
				, is_deleted = 0
			).first()
			# got the record to be update

			if to_update == None:
				return APIResponse(
					success			=	False
					, status_code	=	208
					, errors		=	[
						"Provided author does not found"
					]

				).get_response()

			if self.json_body["field_to_update"] == "name":
				if not validator.is_name(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given name is not ok")
				# check done

				to_update.name = self.json_body["new_value"]
			elif self.json_body["field_to_update"] == "bio":
				if not validator.is_long_text(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given bio is not ok")
				# check done

				to_update.biography = self.json_body["new_value"]
			elif self.json_body["field_to_update"] == "active":
				if not validator.is_single_digit(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given active status is not ok")
				# check done

				to_update.is_active = self.json_body["new_value"]
			else:
				return self.__invalidActionError()
			# updating done... going to commit it

		elif compo == "language" and "language_id" in self.json_body:
			
			to_update = DB.session.query(Language).filter_by(
				lang_id = self.json_body["language_id"]
				, is_deleted = 0
			).first()
			# got the record to be update


			if self.json_body["field_to_update"] == "name":
				if not validator.is_name(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given name is not ok")
				# check done

				to_update.name = self.json_body["new_value"]
			elif self.json_body["field_to_update"] == "active":
				if not validator.is_single_digit(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given active status is not ok")
				# check done

				to_update.is_active = self.json_body["new_value"]
			else:
				return self.__invalidActionError()
			# updating done... going to commit it

		elif compo == "category" and "category_id" in self.json_body:

			to_update = DB.session.query(Category).filter_by(
				category_id		=	self.json_body["category_id"]
				, is_deleted	=	0
			).first()
			# got the record to be update


			if self.json_body["field_to_update"] == "name":
				if not validator.is_name(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given name is not ok")
				# check done

				to_update.name = self.json_body["new_value"]
			elif self.json_body["field_to_update"] == "active":
				if not validator.is_single_digit(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given active status is not ok")
				# check done

				to_update.is_active = self.json_body["new_value"]
			else:
				return self.__invalidActionError()
			# updating done... going to commit it

		elif compo == "genre"  and "genre_id" in self.json_body:

			to_update = DB.session.query(Genre).filter_by(
				genre_id = self.json_body["genre_id"]
				, is_deleted = 0
			).first()
			# got the record to be update


			if self.json_body["field_to_update"] == "name":
				if not validator.is_name(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given name is not ok")
				# check done

				to_update.name = self.json_body["new_value"]
			elif self.json_body["field_to_update"] == "active":
				if not validator.is_single_digit(self.json_body["new_value"]):
					return self.__response_invalid_given_value(err = "Given active status is not ok")
				# check done

				to_update.is_active = self.json_body["new_value"]
			else:
				return self.__invalidActionError()
			# updating done... going to commit it
	
		else:
			return self.__invalidActionError()

		# endif

		return self.__commit()
		# commited the changes to `to_update` variable


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_MASTER"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _delete(self, compo):
		"""
		Internal Function to delete a existing record for the given 'master'
		and its	data in the `self.json_body`.
		"""

		if compo == "publisher" and "publisher_id" in self.json_body:

			to_update = Publisher.query.filter_by(
				publisher_id = self.json_body["publisher_id"]
				, is_deleted = 0
			).first()
			# got the record to be update

			if to_update != None:
				to_update.is_deleted	=	1
				to_update.is_active		=	0
				# updating done... going to commit it
			else:
				return self.__record_existance_response(should_not_exists = False)
		
		elif compo == "author" and "author_id" in self.json_body:
			
			to_update = DB.session.query(Authors).filter_by(
				author_id = self.json_body["author_id"]
				, is_deleted = 0
			).first()
			# got the record to be update

			if to_update != None:
				to_update.is_deleted	=	1
				to_update.is_active		=	0
				# updating done... going to commit it
			else:
				return self.__record_existance_response(should_not_exists = False)

		elif compo == "language" and "lang_id" in self.json_body:
			
			to_update = DB.session.query(Language).filter_by(
				lang_id = self.json_body["lang_id"]
				, is_deleted = 0
			).first()
			# got the record to be update

			if to_update != None:
				to_update.is_deleted	=	1
				to_update.is_active		=	0
				# updating done... going to commit it
			else:
				return self.__record_existance_response(should_not_exists = False)

		elif compo == "category" and "category_id" in self.json_body:

			to_update = DB.session.query(Category).filter_by(
				category_id = self.json_body["category_id"]
				, is_deleted = 0
			).first()
			# got the record to be update

			if to_update != None:
				to_update.is_deleted	=	1
				to_update.is_active		=	0
				# updating done... going to commit it
			else:
				return self.__record_existance_response(should_not_exists = False)

		elif compo == "genre" and "genre_id" in self.json_body:

			to_update = DB.session.query(Genre).filter_by(
				lang_id = self.json_body["genre_id"]
				, is_deleted = 0
			).first()
			# got the record to be update

			if to_update != None:
				to_update.is_deleted	=	1
				to_update.is_active		=	0
				# updating done... going to commit it
			else:
				return self.__record_existance_response(should_not_exists = False)

		else:
			return self.__invalidActionError()

		# endif

		return self.__commit()
		# commited the changes to `to_update` variable
