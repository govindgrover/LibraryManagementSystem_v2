# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# importing flask' current app
from flask import current_app as app

# to handle requests
from flask import request

# to abort the connection when needed
from flask import abort

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
# ============================ [ GetStaticFiles ] =============================
# =============================================================================

class GetStaticFiles(Resource):
	"""
	This resource class is used to handle the following:
		* Retrive the requested static files from the static folder

			Direct Database Table(s) used: None
	"""

	def __init__(self):
		pass
	
	def get(self, directory: str = None, filename: str = None):
		"""
		To process GET Method
		"""

		if filename is not None and directory is not None:		# '32' since we are using UUID4()
			return self.send_requested_file(directory, filename)
	
		return None


	def send_requested_file(self, dir: str, fname: str):
		"""
		"""

		return fileManager.retrive(
			filename	=	fname
			, directory	=	dir
		)
