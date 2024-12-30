# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# importing flask' current app
from flask import current_app as app

# for path joining
from os.path import join as path_join

# to parse JSON file
from json import load as loadJson

# importing logging mechanism
from ..functions.functions import api_logger

# ++++++++++++++++++++++++++++++++ END IMPORTS ++++++++++++++++++++++++++++++++


# =============================================================================
# ============================= [ APIStatusCodes ] ============================
# =============================================================================
class APIStatusCodes():
	"""
	This class aims to centralize all the status codes used in this system
	through a JSON file with respective message such that it will fetch it from
	there whenever needed.

	If the given code is not found in the JSON, then it will return the message
	as "Unknown error occured" and calls api_logger simultanesouly.

		Direct Database Table(s) used: None
	"""

	def __init__(self) -> None:
		pass

	def get_status_msg(self, _code: int) -> str:
		"""
		Function to return a <str> for the provided 'code' if found in the
		file, else it will be 'Unknown error occured'		 
		"""

		with open(path_join(app.root_path, "ams", app.config["API_RESPONSE_CODES_JSON_FILE"])) as f:
			codes :dict	=	loadJson(f)
			_code :str	=	str(_code)

			if _code in codes.keys():
				return codes[_code]
			
		
		api_logger.exception(
			"Unable to understand the given status_code = {}".format(
				_code
			)
		)

		return "Unknown error occured"
