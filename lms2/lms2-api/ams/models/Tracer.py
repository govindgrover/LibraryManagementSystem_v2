# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# importing required DB Models for current usage
from .DB_Models import LoginTrace

# importing 'DB' object for querying
from .DB_object import DB

# importing logging mechanism
from ..functions.functions import api_logger

# ++++++++++++++++++++++++++++++++ END IMPORTS ++++++++++++++++++++++++++++++++


# =============================================================================
# ================================ [ Tracer ] =================================
# =============================================================================

class Tracer():
	"""
	This class aims to handle tracing for the following:
		* Login trace at each successful/failed login and logout requests

		Direct Database Table(s) used: `login_trace`
	"""

	def __init__(self) -> None:
		pass

	def trace_login(self, params: dict) -> bool:
		"""
		Function to trace login-logout attempts.

		`params: dict = keys <process, role, email, password, ip, browser
		, user_agent, user_id, jwt>`
		"""

		insert = LoginTrace(
			role		=	int(params["role"]) if "role" in params else None
			, email		=	params["email"]
			, ip		=	params["ip"]
			, browser	=	params["browser"] if (params["browser"] != None) else ""
			, user_agent=	params["user_agent"] if (params["user_agent"] != None) else ""
			, user_id	=	params["user_id"]
			, jwt		=	params["jwt"]
			, process	=	params["process"]
		)

		try:
			DB.session.add(insert)
			DB.session.commit()
		except Exception as exp:
			api_logger.error(exp)
			return False

		return True
