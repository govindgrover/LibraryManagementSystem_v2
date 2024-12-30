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

# importing to make MD5 hash of the book-access-token 
from hashlib import md5

# to handle date conversion from string to python' date-object
from datetime import datetime, timedelta


# importing required DB Models for current usage
from ..models.DB_Models import (
	Users, Books
	, BorrowHistory, BorrowRequest
	, BookPurchase
)

# for order ordering records in ascending
from sqlalchemy import asc

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
# ====================== [ LibrarianInteractionResource ] =====================
# =============================================================================

class LibrarianInteractionResource(Resource):
	"""
	This resource class is used to handle the following:
		* To revoke book access
		* to accept the issuing request
		* to issue a book directly, only by librarian or admin

		Direct Database Table(s) used:
			`users`, `books`, 'borrow_history`, `borrow_request`, `book_purchase`
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
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_LIBRARIAN_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def post(self):
		"""
		To process POST Method
		"""

		if self.request_action == "revoke_book_access":
			return self._revoke_book_access()
		elif self.request_action == "accept_book_request":
			return self._accept_book_request()
		elif self.request_action == "issue_book":
			return self._issue_book()
		elif self.request_action == "book_purchase":
			return self._purchase_book()
		elif self.request_action == 'send_graph_report':
			return self._send_graph_report()
		elif self.request_action == 'send_borrowance_report':
			return self._send_borrowance_report()

		return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_LIBRARIAN_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def get(self):
		"""
		To process GET Method
		"""

		if self.request_action == "list_book_requests":
			return self._list_book_requests()
		elif self.request_action == "list_borrow_history":
			return self._list_borrow_history()

		return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_LIBRARIAN_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _revoke_book_access(self):
		"""
		This Internal Function revokes the access of the given book from a user.
		"""

		if set(["user_id", "book_id"]).issubset(self.json_body):
			if not validator.is_uuid(self.json_body["book_id"]):
				return self.__response_invalid_given_value(err = "Invalid book_id")			
			# valid book_id

			if not validator.is_uuid(self.json_body["user_id"]):
				return self.__response_invalid_given_value(err = "Invalid user_id")			
			# valid user_id

			if not self.__check_existing_record(Books, "book_id", self.json_body["book_id"]):
				return self.__record_existance_response(hoping_to_exists = False, keyword = "book_id")
			# ok... book exists

			if not self.__check_existing_record(Users, "user_id", self.json_body["user_id"]):
				return self.__record_existance_response(hoping_to_exists = False, keyword = "user_id")
			# ok... user exists


			lookup_borrow = DB.session.query(BorrowHistory).filter_by(
				issued_to			=	self.json_body["user_id"]
				, book_id			=	self.json_body["book_id"]
				, access_allowed	=	1
				, is_returned		=	0
			).first()

			if lookup_borrow == None:
				return APIResponse(
					success			=	False
					, status_code	=	400
					, errors		=	[
						"Provided record does not exists!"
					]
				).get_response()
			# check passed... all ok

			lookup_borrow.date_returned		=	datetime.date(datetime.now())
			lookup_borrow.is_returned		=	1
			lookup_borrow.access_allowed	=	0
			# done with needed updation

			return self.__commit()
			# comitted

		else:
			return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_LIBRARIAN_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _accept_book_request(self):
		"""
		This Internal Function grants the access of a book to a user who
		requested the same through `UserInteractionResource._request_book()`.
		"""

		if set(["user_id", "book_id"]).issubset(self.json_body):
			if not validator.is_uuid(self.json_body["book_id"]):
				return self.__response_invalid_given_value(err = "Invalid book_id")			
			# valid book_id

			if not validator.is_uuid(self.json_body["user_id"]):
				return self.__response_invalid_given_value(err = "Invalid user_id")			
			# valid user_id

			if not self.__check_existing_record(Books, "book_id", self.json_body["book_id"]):
				return self.__record_existance_response(hoping_to_exists = False, keyword = "book_id")
			# ok... book exists

			if not self.__check_existing_record(Users, "user_id", self.json_body["user_id"]):
				return self.__record_existance_response(hoping_to_exists = False, keyword = "user_id")
			# ok... user exists


			lookup_request = DB.session.query(BorrowRequest).filter_by(
				requested_by		=	self.json_body["user_id"]
				, book_id			=	self.json_body["book_id"]
				, request_processed	=	0
			).first()

			if lookup_request == None:
				return APIResponse(
					success			=	False
					, status_code	=	400
					, errors		=	[
						"Provided record does not exists!"
					]
				).get_response()
			# check passed... all ok

			lookup_request.date_issued		=	datetime.date(datetime.now())
			lookup_request.issued_by		=	get_jwt_identity()
			lookup_request.request_processed=	1
			# done with needed updation

			update_history = DB.session.query(BorrowHistory).filter_by(
				book_id				=	self.json_body["book_id"]
				, issued_to			=	self.json_body["user_id"]
				, access_allowed	=	0
				, is_returned		=	0
				, issued_by			=	None
				, date_of_issue		=	None
			).first()

			_token = md5(
				(
					"{}{}".format(
						app.config["BOOK_ACCESS_TOKEN_PREFIX"]
						, str(uuid4())
					)
				).encode()
			).hexdigest()
			# 32-char md5 string


			update_history.issued_by		=	get_jwt_identity()
			update_history.date_of_issue	=	datetime.date(datetime.now())
			update_history.date_of_return	=	datetime.date(datetime.now()) + timedelta(days = app.config["NUMBER_OF_DAYS_TO_ISSUE_BOOK"])
			update_history.access_allowed	=	1
			update_history.access_token		=	_token
			
			return self.__commit(
				APIResponse(
					success			=	True
					, status_code	=	200
					, data			=	[
						{
							"access_token": _token
						}
					]
				)
			)
			# commited

		else:
			return self.__invalidActionError()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_LIBRARIAN_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _issue_book(self):
		"""
		This Internal Function is used to issue a book to a given `user_id`
		directly that is, with raising a request in `borrow_request` but also
		which gets processed instantenously here only without delay.
		"""

		if set(["user_id", "book_id"]).issubset(self.json_body):
			if not validator.is_uuid(self.json_body["book_id"]):
				return self.__response_invalid_given_value(err = "Invalid book_id")			
			# valid book_id

			if not validator.is_uuid(self.json_body["user_id"]):
				return self.__response_invalid_given_value(err = "Invalid user_id")			
			# valid user_id

			if not self.__check_existing_record(Books, "book_id", self.json_body["book_id"]):
				return self.__record_existance_response(hoping_to_exists = False, keyword = "book_id")
			# ok... book exists

			if not self.__check_existing_record(Users, "user_id", self.json_body["user_id"]):
				return self.__record_existance_response(hoping_to_exists = False, keyword = "user_id")
			# ok... user exists


			check_if_already_requested = DB.session.query(BorrowRequest).filter_by(
				requested_by		=	self.json_body["user_id"]
				, book_id			=	self.json_body["book_id"]
				, request_processed	=	0
			).count()

			if check_if_already_requested > 0:
				return APIResponse(
					success			=	False
					, status_code	=	400
					, errors		=	[
						"Request already raised by the user itself! Please continue with that."
					]
				).get_response()
			# check passed... all ok

			count_active_books = DB.session.query(BorrowHistory).filter_by(
				issued_to		=	self.json_body["user_id"]
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
				, requested_by		=	self.json_body["user_id"]
				, issued_by			=	get_jwt_identity()
				, date_requested	=	datetime.date(datetime.now())
				, date_issued		=	datetime.date(datetime.now())
				, request_processed	=	1
			)
			# raised a request... which will be processed just now

			insert_request_into_history = BorrowHistory(
				book_id				=	self.json_body["book_id"]
				, issued_to			=	self.json_body["user_id"]
				, issued_by			=	get_jwt_identity()
				, date_of_issue		=	datetime.date(datetime.now())
				, access_allowed	=	1
				, is_returned		=	0
				, date_of_return	=	datetime.date(datetime.now()) + timedelta(days = app.config["NUMBER_OF_DAYS_TO_ISSUE_BOOK"])
				, access_token		=	"{}{}".format(
					app.config["BOOK_ACCESS_TOKEN_PREFIX"]
					, str(uuid4())
				)
			)
			# done with creating borrow history

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
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_LIBRARIAN_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _list_book_requests(self):
		list_all_request = DB.session.query(BorrowRequest).filter_by(
			request_processed	=	0
		).order_by(
			asc(BorrowRequest.current_timestamp)
		).all()

		records_data = []

		if len(list_all_request) > 0:
			for tup in list_all_request:
				tmp = dict()

				theBook = DB.session.query(Books).filter_by(
					book_id = tup.book_id
				).one()
				tmp["max_price"]		=	theBook.price

				tmp["book_id"]			=	tup.book_id
				tmp["book_isbn"]		=	tup.relation_book_id.isbn
				tmp["book_title"]		=	tup.relation_book_id.title
				tmp["requested_by_id"]	=	tup.requested_by
				tmp["requested_by_name"]=	tup.relation_requested_by_id.name
				tmp["date_of_request"]	=	tup.date_requested

				records_data.append(tmp)

			return APIResponse(
				success			=	True
				, status_code	=	206
				, data			=	records_data
			).get_response()
		else:
			return APIResponse(
				success			=	False
				, status_code	=	404
				, errors		=	[
					"No records found!"
				]
			).get_response()


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_LIBRARIAN_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _list_borrow_history(self):
		list_all = DB.session.query(BorrowHistory).filter_by(
			is_returned			=	0
			, access_allowed	=	1
			, is_purchased		=	0
		).order_by(
			asc(BorrowHistory.date_of_return)
		).all()

		records_data = []

		if len(list_all) > 0:
			for tup in list_all:
				tmp = dict()

				tmp["book_id"]			=	tup.book_id
				tmp["book_isbn"]		=	tup.relation_book_id.isbn
				tmp["book_title"]		=	tup.relation_book_id.title
				tmp["issued_to_id"]		=	tup.issued_to
				tmp["issued_to_name"]	=	tup.relation_issued_to.name
				tmp["date_of_issue"]	=	tup.date_of_issue
				tmp["date_of_return"]	=	tup.date_of_return
				# tmp["date_returned"]	=	tup.date_returned

				records_data.append(tmp)

			return APIResponse(
				success			=	True
				, status_code	=	206
				, data			=	records_data
			).get_response()
		else:
			return APIResponse(
				success			=	False
				, status_code	=	404
				, errors		=	[
					"No records found!"
				]
			).get_response()

	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_LIBRARIAN_INTERACTION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _purchase_book(self):
		"""
		This Internal Function stores the book purchase information.

		PS: This method do not perform the transaction but only stores the
		required details.
		"""

		if set(["book_id", "current_cost", "transaction_id"]).issubset(self.json_body):

			if not validator.is_uuid(self.json_body["book_id"]):
				return self.__response_invalid_given_value(err = "Invalid book_id")			
			# valid book_id

			if not validator.is_float(self.json_body["current_cost"]):
				return self.__response_invalid_given_value(err = "Invalid current_cost")			
			# valid current_cost

			if not self.__check_existing_record(Books, "book_id", self.json_body["book_id"]):
				return self.__record_existance_response(should_not_exists = False)
			# ok... book exists

			purchase_book = BookPurchase(
				book_id				=	self.json_body["book_id"]
				, user_id			=	self.json_body["user_id"]
				, cost				=	self.json_body["current_cost"]
				, transaction_id	=	self.json_body["transaction_id"]
			)
			# created a record

			DB.session.add(purchase_book)
			# added to db session

			lookup_request = DB.session.query(BorrowRequest).filter_by(
				requested_by		=	self.json_body["user_id"]
				, book_id			=	self.json_body["book_id"]
				, request_processed	=	0
			).first()

			if lookup_request == None:
				return APIResponse(
					success			=	False
					, status_code	=	400
					, errors		=	[
						"Provided record does not exists!"
					]
				).get_response()
			# check passed... all ok

			lookup_request.date_issued		=	datetime.date(datetime.now())
			lookup_request.issued_by		=	get_jwt_identity()
			lookup_request.request_processed=	1
			# done with needed updation

			update_history = DB.session.query(BorrowHistory).filter_by(
				book_id				=	self.json_body["book_id"]
				, issued_to			=	self.json_body["user_id"]
				, access_allowed	=	0
				, is_returned		=	0
				, issued_by			=	None
				, date_of_issue		=	None
			).first()

			_token = md5(
				(
					"{}{}".format(
						app.config["BOOK_ACCESS_TOKEN_PREFIX"]
						, str(uuid4())
					)
				).encode()
			).hexdigest()
			# 32-char md5 string


			update_history.issued_by		=	get_jwt_identity()
			update_history.date_of_issue	=	datetime.date(datetime.now())
			update_history.date_of_return	=	datetime.date(datetime.now()) + timedelta(days = app.config["NUMBER_OF_DAYS_TO_PURCHASE_BOOK"])
			update_history.access_allowed	=	1
			update_history.access_token		=	_token
			update_history.is_purchased		=	1
			
			return self.__commit(
				custom_success_response = APIResponse(
					success			=	True
					, status_code	=	206
					, data			=	[
						{
							"access_token": _token
						}
					]
				)
			)
			# commited

		else:
			return self.__invalidActionError()
	
	def _send_graph_report(self):
		from ..CelerySystem.tasks.lib_tasks import lib_activity_report

		lib_activity_report.apply_async([self.json_body['requestee_id']])

		# return APIResponse(
		# 	status_code = 200
		# 	, success	=	True
		# )

	def _send_borrowance_report(self):
		from ..CelerySystem.tasks.lib_tasks import download_all_borrow_history

		download_all_borrow_history.apply_async([self.json_body['requestee_id']])

		# return APIResponse(
		# 	status_code = 200
		# 	, success	=	True
		# )
