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
from flask_jwt_extended import get_jwt_identity


# importing UUID4 method to generate random uuids
from uuid import uuid4

# to handle date conversion from string to python' date-object
from datetime import datetime

# to manuplate paths
from os.path import join as path_join
from os import remove as path_remove


# importing required DB Models for current usage
from ..models.DB_Models import (
	Books
	, Authors, Category, Genre
	, Language, Publisher
)
from ..models.DB_Models import (
	RelBooksAuthors, RelBooksCategory
	, RelBooksGenre, RelBooksLanguage
	, RelBooksPublisher
)

# importing APIResponse to make responses
from ..models.APIResponse import APIResponse 

# importing to validate user-inputs
from ..models.Validator import Validator

# importing to handle file uploding and retrival processes
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

# setting-up file manager
fileManager = ExternalFileManager()

# =============================================================================
# =========================== [ BookMasterResource ] ==========================
# =============================================================================

class BookOperationResource(Resource):
	"""
	This resource class is used to handle the following:
		* Add a new book record
		* to assign the content to it
		* updating its fields
		* deleteting it by setting, `is_deleted` to `1`

		Direct Database Table(s) used: 
		`books`, `authors`, `category`,`genre`, `language`, `publisher`
		
		, `rel_books_authors`, `rel_books_category`, `rel_books_genre`
		, `rel_books_language`, `rel_books_publisher`
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


	def __commit(self, custom_success_response: APIResponse = None):
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

		if custom_success_response is not None:
			return custom_success_response.get_response()
		else:
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
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_OPERATION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def put(self):
		"""
		To process PUT Method
		"""

		if self.request_action == "add_details":
			return self._add_new_details()
		elif self.request_action == "add_content":
			return self._add_new_contents()

		return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_OPERATION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def post(self):
		"""
		To process POST Method
		"""

		if self.request_action == "update":
			return self._update()

		return self.__invalidActionError()
	
	
	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_OPERATION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def delete(self):
		"""
		To process DELETE Method
		"""

		if self.request_action == "delete":
			return self._delete()

		return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_OPERATION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _add_new_details(self):
		"""
		Internal Function to add new Book's details but not contents for it, we
		have different function and request funcionality.
		"""

		if not validator.is_isbn(self.json_body["book_isbn"]):
			return self.__response_invalid_given_value(err = "Invalid ISBN")
		# valid ISBN

		if self.__check_existing_record(Books, "isbn", self.json_body["book_isbn"]):
			return self.__record_existance_response()
		# ok... this is a new ISBN

		if not validator.is_name(self.json_body["book_title"]):
			return self.__response_invalid_given_value(err = "Invalid Book Title")
		# ok... valid title

		if validator.is_null(self.json_body["book_edition"]):
			return self.__response_invalid_given_value(err = "Invalid Book Edition")
		# ok... valid edition

		if not validator.is_date(self.json_body["book_publication_date"]):
			return self.__response_invalid_given_value(err = "Invalid Publication Date")
		# ok... valid publication date
		
		if not validator.is_long_text(self.json_body["book_desc"]):
			return self.__response_invalid_given_value(err = "Invalid Book Description")
		# ok... valid description

		if not validator.is_float(self.json_body["book_price"]):
			return self.__response_invalid_given_value(err = "Invalid Book Price")
		# ok... valid price

		new = []
		# created empty variable to commit objects to DB

		new_book_id = str(uuid4())
		# book_id

		newBook = Books(
			book_id				=	new_book_id
			, title				=	self.json_body["book_title"]
			, isbn				=	self.json_body["book_isbn"]
			, publication_date	=	datetime.strptime(self.json_body["book_publication_date"], "%d-%m-%Y")
			, edition			=	self.json_body["book_edition"]
			, description		=	self.json_body["book_desc"]
			# , cover_image		=	self.json_body["book_cover_image"]
			# , content			=	self.json_body["book_content"]
			, price				=	self.json_body["book_price"]
			, added_by			=	get_jwt_identity()
			, is_active			=	0	# since the book content is not yet uploaded
		)
		new.append(newBook)
		# appended new book


		if not self.__check_existing_record(Publisher, "publisher_id", self.json_body["publisher_id"]):
			return self.__response_invalid_given_value(err = "Provided 'publisher_id' does not exists")
		# ok... provided details exists in master table

		newRel_pub = RelBooksPublisher(
			publisher_id	=	self.json_body["publisher_id"]
			, book_id		=	new_book_id
		)
		new.append(newRel_pub)
		# appended publisher for the new book


		if not self.__check_existing_record(Language, "lang_id", self.json_body["language_id"]):
			return self.__response_invalid_given_value(err = "Provided 'language_id' does not exists")
		# ok... provided details exists in master table

		newRel_lang = RelBooksLanguage(
			lang_id			=	self.json_body["language_id"]
			, book_id		=	new_book_id
		)
		new.append(newRel_lang)
		# appended language for the new book


		newRel_ctgry = []		# tmp var
		for c in self.json_body["category_id"]:
			if not self.__check_existing_record(Category, "category_id", c):
				return self.__response_invalid_given_value(err = "Provided 'category_id' does not exists")
			# ok... provided details exists in master table

			newRel_ctgry.append(RelBooksCategory(
				category_id		=	c
				, book_id		=	new_book_id
			))
		new.extend(newRel_ctgry)
		# appended categories for the new book


		newRel_genre = []		# tmp var
		for g in self.json_body["genre_id"]:
			if not self.__check_existing_record(Genre, "genre_id", g):
				return self.__response_invalid_given_value(err = "Provided 'genre_id' does not exists")
			# ok... provided details exists in master table

			newRel_genre.append(RelBooksGenre(
				genre_id		=	g
				, book_id		=	new_book_id
			))			
		new.extend(newRel_genre)
		# appended genre for the new book


		newRel_author = []		# tmp var
		for a in self.json_body["author_id"]:
			if not self.__check_existing_record(Authors, "author_id", a):
				return self.__response_invalid_given_value(err = "Provided 'author_id' does not exists")
			# ok... provided details exists in master table

			newRel_author.append(RelBooksAuthors(
				author_id		=	a
				, book_id		=	new_book_id
			))
		new.extend(newRel_author)
		# appended authors for the new book


		DB.session.add_all(new)
		# provided the same to DB session for creating 'new' record

		return self.__commit(
			APIResponse(
				success			=	True
				, status_code	=	206
				, data			=	[
					{
						"book_id":	new_book_id
					}
				]
			)

			# returning response with `book_id` so that the controller could
			# send the book's content with it.
		)
		# commited


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_OPERATION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _add_new_contents(self):
		"""
		Internal Function to add new Book's content only.
		"""

		if set(["book_id"]).issubset(set(self.request_form)):
			if not validator.is_uuid(self.request_form["book_id"]):
				return self.__response_invalid_given_value(err = "Invalid body fields!")
			# ok... valid book_id

			if not self.__check_existing_record(Books, "book_id", self.request_form["book_id"]):
				return self.__record_existance_response()
			# ok... book_id do exists

			# checks done... proceeding to upload book

			theBook = DB.session.query(Books).filter_by(
				book_id		=	self.request_form["book_id"]
				, content	=	None
			).first()

			if theBook is not None:
			
				done = fileManager.upload(
					request.files["book_content"]
					, app.config["UPLOADED_BOOKS_DIRRECTORY"]
				)

				if done["success"]:
					theBook = DB.session.query(Books).filter_by(
						book_id		=	self.request_form["book_id"]
						, content	=	None
					).first()

					theBook.content		=	done["filename"]
					theBook.is_active	=	1

					return self.__commit()
					# commited
				else:
					return APIResponse(
						success			=	False
						, status_code	=	400
						, errors		=	[
							done["error"]
						]
					).get_response()
			else:
				return APIResponse(
						success			=	False
						, status_code	=	400
						, errors		=	[
							"Content for the given book_id already exists and thus could not be changed!"
						]
				).get_response()
		else:
			return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_OPERATION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _delete(self):
		"""
		Internal Function to set delete = 1 for the given book with `book_id`
		in the `self.json_body`.
		"""

		if "book_id" in self.json_body:
			if not validator.is_uuid(self.json_body["book_id"]):
				return self.__response_invalid_given_value(err = "Invalid book_id")
			# ok... valid book_id
			
			if not self.__check_existing_record(Books, "book_id", self.json_body["book_id"]):
				return self.__record_existance_response()
			# ok... book_id do exists

		else:
			return self.__invalidActionError()
		# ok... valid body-attribute provided


		# fetching the book into system
		deleteRecord = DB.session.query(Books).filter_by(
			book_id			=	self.json_body["book_id"]
			, is_deleted	=	0
		).first()

		if deleteRecord != None:
			# the book is not deleted yet!

			# performing deletion
			deleteRecord.is_deleted = 1

			return self.__commit()
			# commited
		
		# since the book has been deleted already... give response
		return APIResponse(
			success			=	False
			, status_code	=	208
			, errors		=	[
				"Provided book has been deleted already!"
			]
		).get_response()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_OPERATION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _update(self):
		"""
		Internal Function to update the book's details given the `book_id`.
		"""

		if (
			(
				hasattr(self, "json_body")
				and set(["book_id", "field_to_update", "new_value"]).issubset(set(self.json_body))
			)
			or
			(
				hasattr(self, "request_form")
				and set(["book_id", "field_to_update"]).issubset(set(self.request_form))
				and "new_value" in self.request_files.keys()
			)
		):
			
			book_id = self.json_body["book_id"] if hasattr(self, "json_body") else self.request_form["book_id"]

			if not validator.is_uuid(book_id):
				return self.__response_invalid_given_value(err = "Invalid `book_id` !")
			# ok... valid book_id

			if not self.__check_existing_record(Books, "book_id", book_id):
				return self.__record_existance_response()
			# ok... book_id do exists

		else:
			return self.__invalidActionError()
		# ok... valid body-attribues provided

		# fetching the book into system
		updateRecord = DB.session.query(Books).filter_by(
			book_id			=	book_id
			, is_deleted	=	0
		).first()

		if updateRecord != None:
			# the book is not deleted so... performing changes

			if hasattr(self, "json_body"):
				if self.json_body["field_to_update"] == "book_title":
					if not validator.is_name(self.json_body["new_value"]):
						return self.__response_invalid_given_value(err = "Invalid Book Title")
					# ok... valid title

					updateRecord.title = self.json_body["new_value"]

				elif self.json_body["field_to_update"] == "book_desc":
					if not validator.is_long_text(self.json_body["new_value"]):
						return self.__response_invalid_given_value(err = "Invalid Book Description")
					# ok... valid description
	 
					updateRecord.description = self.json_body["new_value"]

				elif self.json_body["field_to_update"] == "book_price":
					if not validator.is_float(self.json_body["new_value"]):
						return self.__response_invalid_given_value(err = "Invalid Book Title")
					# ok... valid price

					updateRecord.price = self.json_body["new_value"]

				elif self.json_body["field_to_update"] == "active":
					if not validator.is_single_digit(self.json_body["new_value"]):
						return self.__response_invalid_given_value(err = "Given active status is not ok")
					# ok... valid active status

					updateRecord.is_active = self.json_body["new_value"]
				else:
					# if the provided 'field_to_update' is invalid
					return self.__response_invalid_given_value(err = "Invalid body fields!")

			elif hasattr(self, "request_form") and self.request_form["field_to_update"] == "cover_image":
					# performing the change
					uploadedFile = self.request_files.get("new_value")

					u = fileManager.upload(
						uploadedFile
						, app.config["UPLOADED_BOOK_COVER_IMAGE_DIRRECTORY"]
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
					if updateRecord.cover_image is not None and updateRecord.cover_image != app.config["DEFAULT_BOOK_COVER_IMAGE_FILENAME"]:
						try:
							path_remove(
								path_join(
									app.config["UPLOAD_FOLDER"]
									, app.config["UPLOADED_BOOK_COVER_IMAGE_DIRRECTORY"]
									, updateRecord.cover_image
								)
							)
						except Exception as e:
							pass

					# file placed onto the disk
					updateRecord.cover_image =	u["filename"]
			else:
				# if the provided 'field_to_update' is invalid
				return self.__response_invalid_given_value(err = "Invalid body fields!")

			return self.__commit()
			# commited
		else:
			# unho.. the book has been deleted... could not perform any action
			return APIResponse(
				success			=	False
				, status_code	=	400
				, errors		=	[
					"Provided book has been deleted!"
				]
			).get_response()

