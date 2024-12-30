# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# importing SQLAlchemy' DataTypes
from sqlalchemy import (
	Column, Integer, String
	, Float, Boolean, TIMESTAMP
	, Date
)

# importing SQLAlchemy' object to define the same
from sqlalchemy import ForeignKey

# importing SQLAlchemy' method to define relations
from sqlalchemy.orm import relationship

# importing SQLAlchemy' Base to connect all the models to the ORM
from sqlalchemy.ext.declarative import declarative_base

# this variable is used to access the database' in-build functions, like `current_timestamp`
from sqlalchemy import func

# ++++++++++++++++++++++++++++++++ END IMPORTS ++++++++++++++++++++++++++++++++


# declaring the ORM Base
Base	=	declarative_base()

class Users(Base):
	"""
		Database equivalent table: `users`
	"""

	__tablename__				=	'users'

	id							=	Column(Integer, primary_key=True, autoincrement=True)
	user_id						=	Column(String, unique=True, nullable=False)
	role						=	Column(Integer, nullable=False, default=2)
	name						=	Column(String, nullable=False)
	email						=	Column(String, unique=True, nullable=False)
	password					=	Column(String, nullable=False)
	profile_picture				=	Column(String)
	gender						=	Column(String, nullable=False)
	dob							=	Column(Date, nullable=False)
	is_active					=	Column(Boolean, nullable=False, default=True)
	is_deleted					=	Column(Boolean, nullable=False, default=False)
	prefer_pdf_monthly_report	=	Column(Integer, nullable=False, default=0)

	current_timestamp			=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp		=	Column(TIMESTAMP, onupdate = func.current_timestamp())

class Books(Base):
	"""
		Database equivalent table: `books`
	"""

	__tablename__			=	'books'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	book_id					=	Column(String, unique=True, nullable=False)
	title					=	Column(String, nullable=False)
	isbn					=	Column(String, nullable=False)
	publication_date		=	Column(Date, nullable=False)
	edition					=	Column(String, nullable=False)
	description				=	Column(String, nullable=False)
	cover_image				=	Column(String, nullable=False)
	content					=	Column(String, nullable=False)
	price					=	Column(Float, nullable=False, default=0)
	added_by				=	Column(String, ForeignKey("users.user_id"), nullable=False)
	is_active				=	Column(Boolean, nullable=False, default=True)
	is_deleted				=	Column(Boolean, nullable=False, default=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

	# Relationship to User
	relation_user_id = relationship("Users", foreign_keys = [added_by])

class Publisher(Base):
	"""
		Database equivalent table: `publisher`
	"""

	__tablename__			=	'publisher'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	publisher_id			=	Column(String, unique=True, nullable=False)
	name					=	Column(String, nullable=False)
	desc					=	Column(String, nullable=False)
	is_active				=	Column(Boolean, nullable=False, default=True)
	is_deleted				=	Column(Boolean, nullable=False, default=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

class Language(Base):
	"""
		Database equivalent table: `language`
	"""

	__tablename__			=	'language'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	lang_id					=	Column(String, unique=True, nullable=False)
	name					=	Column(String, nullable=False)
	is_active				=	Column(Boolean, nullable=False, default=True)
	is_deleted				=	Column(Boolean, nullable=False, default=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

class Category(Base):
	"""
		Database equivalent table: `category`
	"""

	__tablename__			=	'category'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	category_id				=	Column(String, unique=True, nullable=False)
	name					=	Column(String, nullable=False)
	is_active				=	Column(Boolean, nullable=False, default=True)
	is_deleted				=	Column(Boolean, nullable=False, default=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

class Genre(Base):
	"""
		Database equivalent table: `genre`
	"""

	__tablename__			=	'genre'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	genre_id				=	Column(String, unique=True, nullable=False)
	name					=	Column(String, nullable=False)
	is_active				=	Column(Boolean, nullable=False, default=True)
	is_deleted				=	Column(Boolean, nullable=False, default=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

class Authors(Base):
	"""
		Database equivalent table: `authors`
	"""

	__tablename__			=	'authors'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	author_id				=	Column(String, nullable=False)
	name					=	Column(String, nullable=False)
	biography				=	Column(String, nullable=False)
	is_active				=	Column(Boolean, nullable=False, default=True)
	is_deleted				=	Column(Boolean, nullable=False, default=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

class Review(Base):
	"""
		Database equivalent table: `reviews`
	"""

	__tablename__			=	'reviews'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	book_id					=	Column(String, ForeignKey('books.book_id'), nullable=False)
	user_id					=	Column(String, ForeignKey('users.user_id'), nullable=False)
	rating					=	Column(Integer, nullable=False)
	feedback				=	Column(String, nullable=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

	# Relationship to Books and Users
	relation_book_id	=	relationship("Books", foreign_keys = [book_id])
	relation_user_id	=	relationship("Users", foreign_keys = [user_id])

class BorrowRequest(Base):
	"""
		Database equivalent table: `borrow_requests`
	"""

	__tablename__			=	'borrow_requests'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	book_id					=	Column(String, ForeignKey('books.book_id'), nullable=False)
	requested_by			=	Column(String, ForeignKey('users.user_id'), nullable=False)
	issued_by				=	Column(String, ForeignKey('users.user_id'), nullable=True)
	date_requested			=	Column(Date, nullable=False)
	date_issued				=	Column(Date)
	request_processed		=	Column(Boolean, nullable=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

	# Relationship to Books and Users
	relation_book_id		=	relationship("Books", foreign_keys = [book_id])
	relation_requested_by_id=	relationship("Users", foreign_keys = [requested_by])
	relation_issued_id		=	relationship("Users", foreign_keys = [issued_by])

class BorrowHistory(Base):
	"""
		Database equivalent table: `borrow_history`
	"""

	__tablename__			=	'borrow_history'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	book_id					=	Column(String, ForeignKey('books.book_id'), nullable=False)
	issued_by				=	Column(String, ForeignKey('users.user_id'), nullable=True)
	issued_to				=	Column(String, ForeignKey('users.user_id'), nullable=False)
	date_of_issue			=	Column(Date, nullable=True)
	date_of_return			=	Column(Date, nullable=True)
	access_allowed			=	Column(Boolean, nullable=False)
	access_token			=	Column(String, nullable=True)
	is_returned				=	Column(Boolean, nullable=False)
	is_purchased			=	Column(Boolean, nullable=False, default = False)
	is_opened				=	Column(Boolean, nullable=False, default = False)
	date_returned			=	Column(Date)

	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

	# Relationship to Books and Users
	relation_book_id	=	relationship("Books", foreign_keys = [book_id])
	relation_issued_by	=	relationship("Users", foreign_keys = [issued_by])
	relation_issued_to	=	relationship("Users", foreign_keys = [issued_to])

class BookPurchase(Base):
	"""
		Database equivalent table: `book_purchases`
	"""

	__tablename__			=	'book_purchases'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	book_id					=	Column(String, ForeignKey('books.book_id'), nullable=False)
	user_id					=	Column(String, ForeignKey('users.user_id'), nullable=False)
	cost					=	Column(Float, nullable=False)
	transaction_id			=	Column(String, nullable=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

	# Relationship to Books and Users
	relation_book_id	=	relationship("Books", foreign_keys = [book_id])
	relation_user_id	=	relationship("Users", foreign_keys = [user_id])

class RelBooksPublisher(Base):
	"""
		Database equivalent table: `rel_books_publisher`
	"""

	__tablename__			=	'rel_books_publisher'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	publisher_id			=	Column(String, ForeignKey('publisher.publisher_id'), nullable=False)
	book_id					=	Column(String, ForeignKey('books.book_id'), nullable=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

	# Relationship to Publisher and Users
	relation_publisher_id	=	relationship("Publisher", foreign_keys = [publisher_id])
	relation_book_id		=	relationship("Books", foreign_keys = [book_id])

class RelBooksLanguage(Base):
	"""
		Database equivalent table: `rel_books_language`
	"""

	__tablename__			=	'rel_books_language'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	lang_id					=	Column(String, ForeignKey('language.lang_id'), nullable=False)
	book_id					=	Column(String, ForeignKey('books.book_id'), nullable=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

	# Relationship to Language and Users
	relation_language_id	=	relationship("Language", foreign_keys = [lang_id])
	relation_book_id		=	relationship("Books", foreign_keys = [book_id])

class RelBooksCategory(Base):
	"""
		Database equivalent table: `rel_books_category`
	"""

	__tablename__			=	'rel_books_category'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	category_id				=	Column(String, ForeignKey('category.category_id'), nullable=False)
	book_id					=	Column(String, ForeignKey('books.book_id'), nullable=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

	# Relationship to Category and Users
	relation_category_id	=	relationship("Category", foreign_keys = [category_id])
	relation_book_id		=	relationship("Books", foreign_keys = [book_id])

class RelBooksGenre(Base):
	"""
		Database equivalent table: `rel_books_genre`
	"""

	__tablename__			=	'rel_books_genre'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	genre_id				=	Column(String, ForeignKey('genre.genre_id'), nullable=False)
	book_id					=	Column(String, ForeignKey('books.book_id'), nullable=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

	# Relationship to Genre and Users
	relation_genre_id	=	relationship("Genre", foreign_keys = [genre_id])
	relation_book_id	=	relationship("Books", foreign_keys = [book_id])

class RelBooksAuthors(Base):
	"""
		Database equivalent table: `rel_books_authors`
	"""

	__tablename__			=	'rel_books_authors'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	author_id				=	Column(String, ForeignKey('authors.author_id'), nullable=False)
	book_id					=	Column(String, ForeignKey('books.book_id'), nullable=False)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())

	# Relationship to Authors and Users
	relation_author_id	=	relationship("Authors", foreign_keys = [author_id])
	relation_book_id	=	relationship("Books", foreign_keys = [book_id])

class Trace(Base):
	"""
		Database equivalent table: `trace`
	"""

	__tablename__			=	'trace'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	event					=	Column(Integer, nullable=False)
	ip						=	Column(String)
	browser					=	Column(String)
	query					=	Column(String, nullable=False)
	error					=	Column(String)
	page_url				=	Column(String)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())



class LoginTrace(Base):
	"""
		Database equivalent table: `login_trace`
	"""

	__tablename__			=	'login_trace'

	id						=	Column(Integer, primary_key=True, autoincrement=True)

	role					=	Column(Integer)
	email					=	Column(String, nullable=False)
	ip						=	Column(String, nullable=False)
	browser					=	Column(String, nullable=False)
	user_agent				=	Column(String, nullable=False)
	user_id					=	Column(String, ForeignKey('users.user_id'))
	jwt						=	Column(String)
	process					=	Column(String)
	
	current_timestamp		=	Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
	last_updated_timestamp	=	Column(TIMESTAMP, onupdate = func.current_timestamp())
