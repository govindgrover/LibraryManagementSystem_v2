# ============================= [ START IMPORTS ] =============================

# flask functionalities
from flask import current_app as app
from flask import session, redirect

# python logging module
import logging

# importing decorator function - used in 'require_login()'
from functools import wraps

# ============================== [ END IMPORTS ] ==============================

def login_required():
	"""
	"""

	def wrapper(fn):
		@wraps(fn)
		def wrapped(*args, **kwargs):
			if "app_user" in session:
				return fn(*args, **kwargs)

			return redirect("/login")
		
		return wrapped

	return wrapper 

def restrict_access(roles : set):
	"""
	The function requires the flask-session variable, `flask_session_variable`
	and `role : int` of the user, such that if the role satisfy the current
	active user in the session then it allows them to access certain parts of
	of the application otherwise no. So, basically it maintains kind-of
	authority of each roles. ie, 0 or 1 or 2 by returning True or False as the
	`access_allowed : bool` param of the called function.
	"""

	def wrapper(fn):
		@wraps(fn)
		def wrapped(*args, **kwargs):
			is_allowed: bool = False

			if roles.issubset({0, 1, 2}) and "app_user" in session and "role" in session["app_user"]:
				if int(session["app_user"]["role"]) in roles:
					return fn(*args, is_allowed = True,**kwargs)

				return fn(*args, is_allowed,**kwargs)

		return wrapped

	return wrapper 

def setupLogger():
	from os.path import join, dirname
	from os import makedirs

	from logging.handlers import TimedRotatingFileHandler

	_logger = logging.getLogger("APP Logger")

	file = join(
		app.root_path
		, "logs"
		, app.config["APP_LOGGER_FILE"]
	)

	makedirs(
		dirname(file)
		, exist_ok	=	True
	)
	# creating directory and directory if not exists else ok..

		# crate new file for each day
	_logger_handler = TimedRotatingFileHandler(
		file
		, when = "midnight"
	)


	_logger_handler.setFormatter(
		logging.Formatter(
			"[%(asctime)s] (%(levelname)s by %(name)s):\n"
			+ "At >> File: %(filename)s > Module: %(module)s > Line No: %(lineno)d > In Func: %(funcName)s\n"
			+ "Message: %(message)s\n"
		)
	)

	_logger.addHandler(_logger_handler)

	return _logger


app_logger = setupLogger()
