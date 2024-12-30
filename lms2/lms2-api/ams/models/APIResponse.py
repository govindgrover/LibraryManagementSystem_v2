# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# to handle status-code's specific msgs
from .APIStatusCodes import APIStatusCodes

# to do as-is
from flask import jsonify, make_response

# importing logging mechanism
from ..functions.functions import api_logger

# ++++++++++++++++++++++++++++++++ END IMPORTS ++++++++++++++++++++++++++++++++


# =============================================================================
# ============================== [ APIResponse ] ==============================
# =============================================================================

class APIResponse(APIStatusCodes):
	"""
	This class aims to centralize all the responses that will be generated
	to handle the responses in a more systematic manner and enable further
	manuplation

		Direct Database Table(s) used: None
	"""
	def __init__(self
			, status_code	: int	=	200
			, success		: bool	=	True
			, data			: dict	=	{}
			, errors		: list	=	[]
			, headers		: dict	=	{}
			, content_type	: str	=	"application/json"
			# , response_code	: int	=	None
	) -> None:
		self.status_code	: int	=	status_code
		self.success		: bool	=	success
		self.data			: dict	=	data
		self.errors			: list	=	errors
		self.headers		: dict	=	headers
		self.content_type	: str	=	content_type
		# self.response_code	: int	=	response_code

	def __genrate_response_json(self) -> dict:
		"""
		Internal Function to structure/create the required API Response
		"""

		res_dict = {
			"status_code": self.status_code
			, "msg": self.get_status_msg(self.status_code)
			, "IsError": not(self.success)
			, "error": {
				"code": self.status_code if (len(self.errors)) else None
				, "errors": self.errors
			}
			, "data": self.data
		}

		return jsonify(res_dict)

	def get_response(self, res_type : str = "JSON"):
		"""
		Function to return Flask-Response type object to be returned as
		response such that, it follows the API-Application standards and
		formatting for our system to work fluently.
		"""

		response = None

		if res_type == "JSON":
			response = make_response(self.__genrate_response_json())
			response.status_code	=	self.status_code
			response.headers		=	self.headers
			response.content_type	=	self.content_type

			return response
		else:
			api_logger.critical("Invalid response type used!")
			exit()
