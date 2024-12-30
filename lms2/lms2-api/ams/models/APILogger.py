# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# importing flask' current app
from flask import current_app as app

# for path joining
import os
from os.path import join as path_join

# importing python' in-build logging objects
import logging
from logging.handlers import TimedRotatingFileHandler

# ++++++++++++++++++++++++++++++++ END IMPORTS ++++++++++++++++++++++++++++++++


# =============================================================================
# ============================== [ APILogger ] ================================
# =============================================================================

class APILogger():
	"""
	This class aims to handle file logging processes for the API:

		Direct Database Table(s) used: None
	"""

	def __init__(self) -> None:
		# making the logger accessible after initializtion
		self.logger = self._initialize()

	def _initialize(self):
		"""
		Internal Function to initialize python file logger
		"""

		# setting logger
		logger = logging.getLogger("API Logger")

		# level for the logger has been from DEBUG level
		logger.setLevel(logging.DEBUG)

		os.makedirs(
			os.path.dirname(
				path_join(app.root_path, app.config["LOGGER_FILE"][0], app.config["LOGGER_FILE"][1])
			)
			, exist_ok = True
		)
		# creating directory if not exists

		# crate new file for each day
		api_loggin_handler = TimedRotatingFileHandler(
				path_join(app.root_path, app.config["LOGGER_FILE"][0], app.config["LOGGER_FILE"][1])
			, when = "midnight"
		)

		# custom format for logging
		api_logger_format = logging.Formatter(
			"[%(asctime)s] (%(levelname)s by %(name)s):\n"
			+ "At >> File: %(filename)s > Module: %(module)s > Line No: %(lineno)d > In Func: %(funcName)s\n"
			+ "Message: %(message)s\n"
		)

		# setting up formatting
		api_loggin_handler.setFormatter(api_logger_format)

		# configuring logging handler
		logger.addHandler(api_loggin_handler)

		# logger created and returned
		return logger
