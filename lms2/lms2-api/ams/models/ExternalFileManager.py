# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# importing flask' current app
from flask import current_app as app

# to remove special characters
from werkzeug.utils import secure_filename

# to make UNIQUE every filenames
from uuid import uuid4

# to return the requested file
from flask import send_from_directory

# to join path for any OS and to check path's existance 
from os.path import join as path_join
from os.path import exists as path_exists
from os.path import dirname as dirname

# importing logging mechanism
from ..functions.functions import api_logger

# ++++++++++++++++++++++++++++++++ END IMPORTS ++++++++++++++++++++++++++++++++


# =============================================================================
# ========================== [ ExternalFileManager ] ==========================
# =============================================================================

class ExternalFileManager():
	"""
	This class aims to handle file uploading and retriving:

		Direct Database Table(s) used: None
	"""

	def __init__(self) -> None:
		pass

	def _is_ext_allowed(self, filename :str) -> bool:
		"""
		Returns `True` iff the file-extention is defined in,
		config.json->`ALLOWED_EXTENSIONS`
		"""

		if '.' in filename:
			return (
				filename.rsplit('.', 1)[1].lower()
					in app.config["ALLOWED_EXTENSIONS"]
			)
		else:
			return False

	def upload(self, _FlaskRequestFileObject, directory: str) -> dict:
		"""
		This function provides ease while uploading the file that has been
		brought by Flask's request object.

		First it check weather the file extention is allowed or not.

		The filename assigned to the uploaded file is of the format,
		`<UUID>$<GIVEN_FILENAME_AFTER_REMOVING_SPECIAL_CHARS>.<EXTENTION>`

		As far as we are using UUIDs, therefore we are not concerned with
		overwriting the files by this mechanism.

		In return, it produces a dict with the following keys,
			*`success`: str
			*`filename`: str
			*`error`: str
		"""

		try:
			if not self._is_ext_allowed(_FlaskRequestFileObject.filename):
				return {
					"success" : False
					, "error" : "File extention not allowed"
				}

			# unique filename
			filename = (
				str(uuid4())
				+ '.'
				+ _FlaskRequestFileObject.filename.rsplit('.', 1)[1].lower()
			)

			_FlaskRequestFileObject.save(
				path_join(
					app.config['UPLOAD_FOLDER']
					, directory
					, filename
				)
			)

			return {
				"success" 	: True
				, "filename": filename
				, "error" 	: ""
			}

		except Exception as e:
			api_logger.error(e)

			return {
				"success" : False
				, "error" : "Internal Error"
			}
				
	def retrive(self, filename, directory: str):
		"""
		This function provides ease while retriving the uploaded file from the
		disk.

		The filename should be like as disscussed in `upload()` method, ie
		`<UUID>$<GIVEN_FILENAME_AFTER_REMOVING_SPECIAL_CHARS>.<EXTENTION>`

		In return, it produces the requested file or None otherwise.
		"""

		file_path = path_join(
			app.config['UPLOAD_FOLDER']
			, directory
			, filename if filename is not None else ""
		)

		if filename is not None and path_exists(file_path):
			return send_from_directory(
				path_join(
					app.config['UPLOAD_FOLDER']
					, directory
				)
				, filename
				, as_attachment = True
			)
		else:
			return None

	# RequestEntityTooLarge
