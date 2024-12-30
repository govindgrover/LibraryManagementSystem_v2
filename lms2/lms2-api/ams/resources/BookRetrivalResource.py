# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# importing flask' current app
from flask import current_app as app

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
	Books, BorrowHistory
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
# ========================= [ BookRetrivalResource ] ==========================
# =============================================================================

class BookRetrivalResource(Resource):
	"""
	This resource class is used to handle the following:
		* Retrive the book that has been requested after the acceptance
			such that the reading token is still active otherwise
			return appropriate response.

		Direct Database Table(s) used: `books`, `borrow_history`
	"""

	def __init__(self):
		pass

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
	def get(self, access_token: str):
		"""
		To process GET Method
		"""

		if access_token is not None and len(access_token) == 32:		# '32' since we are using UUID4()
			return self.process_book_retrival(access_token)
	
		return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_USER_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def process_book_retrival(self, access_id: str):
		"""
		This Function checks the access_token before giving the book so that
		after the success return of the book the user should not be able to get
		it untill and unless the same have been requested again through the
		process.
		"""

		fetchedBook = DB.session.query(BorrowHistory).filter(
			BorrowHistory.access_allowed	==	1
			, BorrowHistory.access_token	==	access_id
			, BorrowHistory.issued_to		==	get_jwt_identity()
			# , BorrowHistory.date_of_return	<=	datetime.date(datetime.now())
			, BorrowHistory.is_returned		==	0
			, BorrowHistory.date_returned	==	None
		).first()
		# fetched the book details

		if fetchedBook == None:
			return APIResponse(
				success			=	False
				, status_code	=	404
				, errors		=	[
					"Book not found!!"
				]
			).get_response()
		
		"""
		# This portion has been commented since in V2 of this project we have
		# to use only one feature, either auto-revoke (which this is) or manual
		# -revoke. So, we have removed the auto-revoke thing which means if the
		# Librarian did not revoke even after the due date, the user will be
		# able to view the ebook.

		if fetchedBook.date_of_return < datetime.date(datetime.now()):
			# due date passed... revoke access and hence give necessary response

			fetchedBook.is_returned		=	1
			fetchedBook.access_allowed	=	0
			fetchedBook.date_returned	=	datetime.date(datetime.now())
			# updated

			return self.__commit(
				APIResponse(
					success			=	False
					, status_code	=	400
					, errors		=	[
						"Due date passed! Kindly re-issue to read."
					]
				)
			)
			# commited and given adequate response
		"""

		requestedBook = self._get_book_to_read(book_id = fetchedBook.book_id)
		# got its content

		if requestedBook is None:
			return APIResponse(
				success			=	False
				, status_code	=	404
				, errors		=	[
					"Unable to find book content!"
				]
			).get_response()
			# oops..
		else:
			return requestedBook

	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_USER_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _get_book_to_read(self, book_id: str):
		"""
		This Internal Function retirves the existing book along with the needed
		content from the local drive storage and returns it.
		"""

		if not self.__check_existing_record(Books, "book_id", book_id):
			return self.__record_existance_response(hoping_to_exists = False, keyword = "book_id")
		# ok... book exists

		theBook = DB.session.query(Books).filter(
			Books.book_id		==	book_id
			, Books.is_active	==	1
			, Books.is_deleted	==	0
			, Books.content		is	not None
		).first()

		if theBook is not None:
			return fileManager.retrive(
				theBook.content
				, app.config["UPLOADED_BOOKS_DIRRECTORY"]
			)
		else:
			api_logger.exception(
				"Unable to locate the book with book_id = {} in the directory({}) given that the book content in DB is not None.".format(
					book_id
					, app.config["UPLOADED_BOOKS_DIRRECTORY"]
				)
			)

			return None
