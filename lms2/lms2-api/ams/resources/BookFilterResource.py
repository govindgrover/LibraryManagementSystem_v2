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
	Books
	, Authors, Category, Genre
	, Language, Publisher
)
from ..models.DB_Models import (
	RelBooksAuthors, RelBooksCategory
	, RelBooksGenre, RelBooksLanguage
	, RelBooksPublisher
)
from ..models.DB_Models import (
	Review
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

from ..models.CacheConfig import api_cache

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
# =========================== [ BookFilterResource ] ==========================
# =============================================================================

class BookFilterResource(Resource):
	"""
	This resource class is used to handle the following:
		* Get response with filtered book's details produced by the provided
		filter.

		Direct Database Table(s) used: 
		`books`, `authors`, `category`,`genre`, `language`, `publisher`
		
		, `rel_books_authors`, `rel_books_category`, `rel_books_genre`
		, `rel_books_language`, `rel_books_publisher`
	"""

	"""
	This set contains all of the valid filter-names that the user/client
	can request and each one of them have their own defined format for the
	respective values that is needed in order to let the function perform
	the requiered search. 
	"""
	DEFINED_BOOK_FILTERS :set = {
		"category"
		, "genre"
		, "language"
		, "author"
		, "publisher"

		, "pub_date_between"

		, "title_like"
		, "desc_like"

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
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_FETCH_BOOK_DETAILS"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def _fetch_single_book(self, given_book_id :str):
		"""
		This Internal Function returns all required details of any book given
		its `book_id` and further we are assuming that the provided `book_id`
		has already been exists in the database to avoid further checks and
		thus lowering the time consumption in camparisions.

		Also, this function returns the details specific to the user's role
		who requested the details. And in case of undesirable role caught,
		the system will log it in using the APILogger and return empty list.
		"""

		# okay... we have to provide details for only the given 'book_id'
		rdata = dict()

		if get_jwt()["role"] == 0:
			# ADMIN

			record = DB.session.query(
					Books
					, RelBooksPublisher
					, RelBooksLanguage
				).join(
					RelBooksPublisher
				).join(
					RelBooksLanguage
				).filter(
					Books.book_id	== given_book_id
			).one_or_none()

			# we are using try-except here because we are checking weather the
			# book exists or not later... so if it is None then all is well...
			try:
				rdata["added_by_id"]		=	record[0].added_by
				rdata["added_by_name"]		=	record[0].relation_user_id.name
				rdata["is_deleted"]			=	record[0].is_deleted
				rdata["is_active"]			=	record[0].is_active
				rdata["uploaded_on"]		=	record[0].current_timestamp
				rdata["last_updated_on"]	=	record[0].last_updated_timestamp
			except:
				pass

		elif get_jwt()["role"] == 1:
			# LIBRARIAN

			record = DB.session.query(
					Books
					, RelBooksPublisher
					, RelBooksLanguage
				).join(
					RelBooksPublisher
				).join(
					RelBooksLanguage
				).filter(
					Books.book_id		==	given_book_id
					, Books.is_deleted	==	0
			).one_or_none()

			# we are using try-except here because we are checking weather the
			# book exists or not later... so if it is None then all is well...
			try:
				rdata["is_active"]		=	record[0].is_active
			except:
				pass

		elif get_jwt()["role"] == 2:
			# USER
			record = DB.session.query(
					Books
					, RelBooksPublisher
					, RelBooksLanguage
				).join(
					RelBooksPublisher
				).join(
					RelBooksLanguage
				).filter(
					Books.book_id		==	given_book_id
					, Books.is_deleted	==	0
					, Books.is_active	==	1
			).one_or_none()
		
		else:
			# something went wrong
			api_logger.exception(
				"Something went wrong for the provided book_id = {}\nThe role in jwt is {}".format(
					self.get_body.get("book_id")
					, get_jwt()["role"]
				)
			)
		# end check for roles

		if record is None:
			return None
		# end check for book existance

		# Now, here we can modify what attributes are to be given to user
		rdata["book_id"]			=	record[0].book_id
		rdata["isbn"]				=	record[0].isbn
		rdata["title"]				=	record[0].title
		rdata["description"]		=	record[0].description
		rdata["price"]				=	record[0].price
		# rdata["content"]			=	record[0].content
		rdata["edition"]			=	record[0].edition
		rdata["publication_date"]	=	record[0].publication_date

		#
		rdata["publisher"]			=	record[1].relation_publisher_id.name
		rdata["language"]			=	record[2].relation_language_id.name


		# start - getting all authors
		authors = DB.session.query(
			Authors
		).join(
			RelBooksAuthors
		).filter(
			RelBooksAuthors.book_id		==	given_book_id
		).limit(
			self.__record_limit
		).all()

		rdata["authors"] = []
		for author in authors:
			rdata["authors"].append(author.name)
		# end - getting authors

		# start - getting all categories
		categories = DB.session.query(
			Category
		).join(
			RelBooksCategory
		).filter(
			RelBooksCategory.book_id		==	given_book_id
		).limit(
			self.__record_limit
		).all()

		rdata["category"] = []
		for category in categories:
			rdata["category"].append(category.name)
		# end - getting categories

		# start - getting all genre
		genre = DB.session.query(
			Genre
		).join(
			RelBooksGenre
		).filter(
			RelBooksGenre.book_id		==	given_book_id
		).limit(
			self.__record_limit
		).all()

		rdata["genre"] = []
		for g in genre:
			rdata["genre"].append(g.name)
		# end - getting genre
			
		
		# start - getting feedbacks
		feedbacks = DB.session.query(
			Review
		).filter(
			Review.book_id		==	given_book_id
		).all()

		rdata["feedbacks"] = []
		for f in feedbacks:
			rdata["feedbacks"].append(
				{
					"feedback": f.feedback
					, "rating": f.rating
				}
			)
		# end - getting feedbacks

		# start - getting link to the cover-image
		_cover_img = fileManager.retrive(
			record[0].cover_image
			, app.config["UPLOADED_BOOK_COVER_IMAGE_DIRRECTORY"]
		)

		if _cover_img is not None:
			rdata["cover_image"]	=	record[0].cover_image
		else:
			# default image
			rdata["cover_image"]	=	app.config["DEFAULT_BOOK_COVER_IMAGE_FILENAME"]
		# end - getting name to the cover-image

		return rdata


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_FETCH_BOOK_DETAILS"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def __getBooksFromDistinctMasters(self, SearchInModel, RelationModel, RelationalAttribute):
		"""
		This Internal Function returns the records of books such that they
		belongs to a specified 'Master' (`SearchInModel`) with the help of
		their relational model ie, `RelationModel` and the above two connects
		or say holds relation in-between by `RelationalAttribute`.
		"""

		return (
			DB.session.query(
				Books
			).join(
				RelationModel
			).filter(
				getattr(SearchInModel, "name")			==	self.get_body["filter_value"]

				, getattr(RelationModel, "book_id")		==	Books.book_id
				, getattr(RelationModel, RelationalAttribute)	==	getattr(SearchInModel, RelationalAttribute)
			).limit(
				self.__record_limit
			).all()
		)


	decorators = [
		role_restriction(app.config["AVAILABLE_USER_ROLES"] if app.config["DEBUG"] else [0, 1])
		, jwt_required(optional = app.config["TESTING"])
	]
	def __getBooksWithActiveStatues(self, is_active :bool):
		"""
		This Internal Function returns the records of books such that they
		satisfy the criterion, `Books.is_active = is_active`.

		The aim to seprate this functionality is to restrict the access to a
		specified role
		"""

		return (
			DB.session.query(Books).filter(
				Books.is_active == is_active
			).limit(
				self.__record_limit
			).all()
		)


	decorators = [
		role_restriction(app.config["AVAILABLE_USER_ROLES"] if app.config["DEBUG"] else [0])
		, jwt_required(optional = app.config["TESTING"])
	]
	def __getBooksWithDeletedStatues(self, is_deleted :bool):
		"""
		This Internal Function returns the records of books such that they
		satisfy the criterion, `Books.is_deleted = is_deleted`.

		The aim to seprate this functionality is to restrict the access to a
		specified role
		"""

		return (
			DB.session.query(Books).filter(
				Books.is_deleted == is_deleted
			).limit(
				self.__record_limit
			).all()
		)


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_FETCH_BOOK_DETAILS"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def get(self):
		"""
		To process GET Method
		"""

		if (not(("book_id" in self.get_body)
				^
			({"filter_name", "filter_value"}.issubset(set(self.get_body)))
		)):
			# raise this response if neither `book_id` nor `filter_name` &
			# `filter_value` is present in the GET params using "inverted XOR"
			return self.__invalidActionError()

		self.__record_limit = app.config["LIMIT_MAX_FETCH_RECORDS"]
		# default limiting the records to be fetched.. to avoid system-hand
		# and also bandwidth


		# checking for roles
		if "book_id" in self.get_body:
			bookData = self._fetch_single_book(given_book_id = self.get_body["book_id"])

			if bookData is not None and len(bookData) > 0:
				return APIResponse(
					status_code	=	302
					, data = bookData
				).get_response()
				# returned the data in the response
			else:
				return APIResponse(
					status_code	=	404
					, success	=	False
					, errors	=	[
						"The book(s) you are looking for does not exists!"
					]
				).get_response()
				# returned the response when book is not found

		elif self.get_body["filter_name"] is not None:
			if "limit" in self.get_body:
				try:
					self.__record_limit = int(self.get_body["limit"])
					# overwriting the provided limit
				except ValueError:
					return self.__response_invalid_given_value("Invalid `limit` value")
			# ok.. the given limit have been set

			if self.get_body["filter_name"] not in self.DEFINED_BOOK_FILTERS:
				return self.__response_invalid_given_value("Invalid `filter_name`")
			# ok.. the given filter-name is valid

			bookData = self._fetch_books_using_filter()

			if len(bookData) > 0:

				return APIResponse(
					status_code	=	302
					, data = bookData
				).get_response()
				# returned the data in the response
			else:
				return APIResponse(
					status_code	=	404
					, success	=	False
					, errors	=	[
						"The book(s) you are looking for does not exists!"
					]
				).get_response()
				# returned the response when book is not found
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
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_FETCH_BOOK_DETAILS"])
		, jwt_required(optional = app.config["TESTING"])
		, api_cache.memoize(app.config['CACHE_DEFAULT_TIMEOUT'])
	]
	def _fetch_books_using_filter(self) -> tuple:
		"""
		The Internal Function returns a tuple of data which contains the
		requested filtered records.
		"""

		filteredRecords :list = []
		# empty list of filtered items

		# switch-case approach for each filter
		if self.get_body["filter_name"] == "category":
			for book in self.__getBooksFromDistinctMasters(Category, RelBooksCategory, "category_id"):
				filteredRecords.append(
					self._fetch_single_book(
						book.book_id
					)
				)

		elif self.get_body["filter_name"] == "genre":
			for book in self.__getBooksFromDistinctMasters(Genre, RelBooksGenre, "genre_id"):
				filteredRecords.append(
					self._fetch_single_book(
						book.book_id
					)
				)

		elif self.get_body["filter_name"] == "language":
			for book in self.__getBooksFromDistinctMasters(Language, RelBooksLanguage, "lang_id"):
				filteredRecords.append(
					self._fetch_single_book(
						book.book_id
					)
				)

		elif self.get_body["filter_name"] == "author":
			for book in self.__getBooksFromDistinctMasters(Authors, RelBooksAuthors, "author_id"):
				filteredRecords.append(
					self._fetch_single_book(
						book.book_id
					)
				)

		elif self.get_body["filter_name"] == "publisher":
			for book in self.__getBooksFromDistinctMasters(Publisher, RelBooksPublisher, "publisher_id"):
				filteredRecords.append(
					self._fetch_single_book(
						book.book_id
					)
				)

		elif self.get_body["filter_name"] == "title_like":
			filtered_book_ids = DB.session.query(Books).filter(
				Books.title.like("%{}%".format(
					self.get_body["filter_value"]
				))
			)

		elif self.get_body["filter_name"] == "desc_like":
			filtered_book_ids = DB.session.query(Books).filter(
				Books.description.like("%{}%".format(
					self.get_body["filter_value"]
				))
			)

		elif self.get_body["filter_name"] == "pub_date_between":
			tmp = self.get_body["filter_value"].split(',')

			after_date	=	datetime.strptime(tmp[0].strip()[1::], "%d-%m-%Y")
			before_date	=	datetime.strptime(tmp[1].strip()[0:-1], "%d-%m-%Y")

			filtered_book_ids = DB.session.query(Books).filter(
				Books.publication_date		>=	after_date
				, Books.publication_date	<=	before_date
			)

		elif self.get_body["filter_name"] == "active_status":
			filtered_book_ids = self.__getBooksWithActiveStatues(is_active = self.get_body["filter_value"])

		elif self.get_body["filter_name"] == "deleted_status":
			filtered_book_ids = self.__getBooksWithDeletedStatues(is_deleted = self.get_body["filter_value"])

		for book in filtered_book_ids:
			tmp = self._fetch_single_book(
					book.book_id
			)
			if tmp is not None and len(tmp):
				filteredRecords.append(tmp)

		if len(filteredRecords) == 1 and filteredRecords[0] == None:
			return tuple()

		return tuple(filteredRecords)
		# returned filtered records
