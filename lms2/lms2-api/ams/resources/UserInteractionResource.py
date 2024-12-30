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


# to handle date conversion from string to python' date-object
from datetime import datetime


# importing required DB Models for current usage
from ..models.DB_Models import (
	Books, Review
	, BookPurchase, BorrowRequest
	, BorrowHistory
)

from ..models.DB_Models import (
	Authors, Category, Genre
	, Publisher, Language
	, RelBooksAuthors, RelBooksCategory
	, RelBooksGenre, RelBooksLanguage
	, RelBooksPublisher
)

# for order ordering records in descending
from sqlalchemy import desc, or_

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
# ======================== [ UserInteractionResource ] ========================
# =============================================================================

class UserInteractionResource(Resource):
	"""
	This resource class is used to handle the following:
		* Raise a request to read a given book
		* Provide feedback on the books that have already been read
		* Return the book by user before its due has been passed

		Direct Database Table(s) used: 
			`books`, `review`, `book_purchase`
			, `borrow_request`, `borrow_history`
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
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_USER_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def post(self):
		"""
		To process POST Method
		"""

		if self.request_action == "book_borrow_request":
			return self._request_book()
		elif self.request_action == "book_feedback":
			return self._give_feedback()
		elif self.request_action == "book_return":
			return self._return_book()

		return self.__invalidActionError()

	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_USER_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def get(self):
		"""
		To process GET Method
		"""

		if self.request_action == "get_my_active_records":
			return self._get_active_records()

		return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_USER_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _request_book(self):
		"""
		This Internal Function processes the request with the provided
		`book_id` to raise/create a 'requesting' record by the user which will
		be used to show librarians and admin that which user has raised the
		query and for which book it is.
		"""

		if "book_id" in self.json_body:
			if not validator.is_uuid(self.json_body["book_id"]):
				return self.__response_invalid_given_value(err = "Invalid book_id")			
			# valid book_id

			if not self.__check_existing_record(Books, "book_id", self.json_body["book_id"]):
				return self.__record_existance_response(should_not_exists = False)
			# ok... book exists

			check_if_already_requested = DB.session.query(BorrowRequest).filter_by(
				requested_by		=	get_jwt_identity()
				, book_id			=	self.json_body["book_id"]
				, request_processed	=	0
			).count()

			if check_if_already_requested > 0:
				return APIResponse(
					success			=	False
					, status_code	=	400
					, errors		=	[
						"Request already raised! Please wait for librarian to respond."
					]
				).get_response()
			# check passed... all ok

			count_active_books = DB.session.query(BorrowHistory).filter_by(
				issued_to		=	get_jwt_identity()
				, is_returned	=	0
				, is_purchased	=	0
			).count()
			# getting the count for max limit check

			if count_active_books > app.config["LIMIT_MAX_BOOKS_ISSUE"]:
				return APIResponse(
					success			=	False
					, status_code	=	400
					, errors		=	[
						"Limit to borrow books reached! return any one to proceed."
					]
				).get_response()
			# check passed... all ok

			raise_borrow_request = BorrowRequest(
				book_id				=	self.json_body["book_id"]
				, requested_by		=	get_jwt_identity()
				, date_requested	=	datetime.date(datetime.now())
				, request_processed	=	False
			)
			# raised a request... which will be processed by the librarians later

			insert_request_into_history = BorrowHistory(
				book_id				=	self.json_body["book_id"]
				, issued_to			=	get_jwt_identity()
				, access_allowed	=	0
				, is_returned		=	0
			)

			DB.session.add_all([
				raise_borrow_request
				, insert_request_into_history
			])
			# added to DB session

			return self.__commit()
			# comitted

		else:
			return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_USER_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _give_feedback(self):
		"""
		This Internal Function is used to create a feedback record by any user
		for a given book.
		"""

		if set(["book_id", "rating", "feedback"]).issubset(set(self.json_body)):

			if not validator.is_uuid(self.json_body["book_id"]):
				return self.__response_invalid_given_value(err = "Invalid book_id")			
			# valid book_id

			if not validator.is_single_digit(self.json_body["rating"]):
				return self.__response_invalid_given_value(err = "Invalid rating")			
			# valid rating

			if not validator.is_long_text(self.json_body["feedback"]):
				return self.__response_invalid_given_value(err = "Invalid feedback text")			
			# valid feedback

			if not self.__check_existing_record(Books, "book_id", self.json_body["book_id"]):
				return self.__record_existance_response(should_not_exists = False)
			# ok... book exists

			feedbackExistance = DB.session.query(BorrowHistory).filter(
				BorrowHistory.book_id		==	self.json_body["book_id"]
				, BorrowHistory.issued_to	==	get_jwt_identity()
			).order_by(
				desc(BorrowHistory.date_returned)
			).first()

			if feedbackExistance != None and feedbackExistance.is_returned == 0:
				return APIResponse(
					status_code	=	400
					, success	=	False
					, errors	=	[
						"You can not provide feedback to the book. Please issue/return the book first."
					]
				).get_response()

			new_fdb = Review(
				book_id		=	self.json_body["book_id"]
				, user_id	=	get_jwt_identity()
				, rating	=	self.json_body["rating"]
				, feedback	=	self.json_body["feedback"]
			)

			DB.session.add(new_fdb)
			# added to DB session

			return self.__commit()
			# commited

		else:
			return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_USER_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _return_book(self):
		"""
		This Internal Function processes the book return procedure.
		"""

		if "book_id" in self.json_body:

			if not validator.is_uuid(self.json_body["book_id"]):
				return self.__response_invalid_given_value(err = "Invalid book_id")			
			# valid book_id

			if not self.__check_existing_record(Books, "book_id", self.json_body["book_id"]):
				return self.__record_existance_response(should_not_exists = False)
			# ok... book exists

			update_borrow_history = DB.session.query(BorrowHistory).filter_by(
				book_id			=	self.json_body["book_id"]
				, issued_to		=	get_jwt_identity()
				, is_returned	=	0
				, access_allowed=	1
			).first()

			if update_borrow_history != None:
				update_borrow_history.date_returned		=	datetime.date(datetime.now())
				update_borrow_history.is_returned		=	1
				update_borrow_history.access_allowed	=	0

				return self.__commit()
				# commited
			else:
				return APIResponse(
					success			=	False
					, status_code	=	400
					, errors		=	[
						"There does not exists any borrow-history with us for the current book."
					]
				).get_response()

		else:
			return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_USER_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _get_active_records(self):
		
		records = DB.session.query(BorrowHistory).filter(
			BorrowHistory.issued_to == get_jwt_identity()
			, or_(
				BorrowHistory.is_returned		==	0
				, BorrowHistory.is_purchased	==	1
			)
			, BorrowHistory.access_allowed	==	1
		).all()

		if not len(records):
			return APIResponse(
				success			=	False
				, status_code	=	400
				, errors		=	[
					"No records found!"
				]
			).get_response()
		
		required_data :list = []

		for record in records:
			_data :dict = {}

			_data["book_id"]				=	record.book_id
			_data["book_title"]				=	record.relation_book_id.title
			_data["isbn"]					=	record.relation_book_id.isbn
			_data["edition"]				=	record.relation_book_id.edition
			_data["publication_date"]		=	record.relation_book_id.publication_date

			_data["date_of_issue"]			=	record.date_of_issue
			_data["date_of_return"]			=	record.date_of_return
			_data["issued_by_id"]			=	record.issued_by
			_data["content_access_token"]	=	record.access_token

			_data["issued_by_name"]			=	record.relation_issued_by.name
			# basic details

			if record.relation_book_id.cover_image is not None:
				_data["cover_image"]	=	record.relation_book_id.cover_image
			else:
				# default image
				_data["cover_image"]	=	app.config["DEFAULT_BOOK_COVER_IMAGE_FILENAME"]
			# got cover image

			if record.is_purchased == 1:
				_data["is_purchased"]		=	True
			else:
				_data["is_purchased"]		=	False
			# okay...

			# start - getting publisher
			publisher = DB.session.query(
				Publisher
			).join(
				RelBooksPublisher
			).filter(
				RelBooksPublisher.book_id		==	record.book_id
			).first()

			_data["publisher"] = publisher.name
			# end - getting publisher

			# start - getting language
			language = DB.session.query(
				Language
			).join(
				RelBooksLanguage
			).filter(
				RelBooksLanguage.book_id		==	record.book_id
			).first()

			_data["language"] = language.name
			# end - getting publisher

			# start - getting all authors
			authors = DB.session.query(
				Authors
			).join(
				RelBooksAuthors
			).filter(
				RelBooksAuthors.book_id		==	record.book_id
			).all()

			_data["authors"] = []
			for author in authors:
				_data["authors"].append(author.name)
			# end - getting authors

			# start - getting all categories
			categories = DB.session.query(
				Category
			).join(
				RelBooksCategory
			).filter(
				RelBooksCategory.book_id		==	record.book_id
			).all()

			_data["category"] = []
			for category in categories:
				_data["category"].append(category.name)
			# end - getting categories

			# start - getting all genre
			genre = DB.session.query(
				Genre
			).join(
				RelBooksGenre
			).filter(
				RelBooksGenre.book_id		==	record.book_id
			).all()

			_data["genre"] = []
			for g in genre:
				_data["genre"].append(g.name)
			# end - getting genre
							
			required_data.append(_data)

		return APIResponse(
			success			=	True
			, status_code	=	300
			, data			=	required_data
		).get_response()
