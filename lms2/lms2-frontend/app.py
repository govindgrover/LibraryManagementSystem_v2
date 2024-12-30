# **************************
# importing required modules
# **************************

# python pre-defined modules
from os.path import join as path_join
import json

# importing 'flask' for web development using python
from flask import Flask

app = Flask(__name__)

app.config.from_file(
	path_join(
		app.root_path
		, "ams"
		, "config.json"
	)
	, load = json.load
)

# overriding for testing purposes
if app.config["TESTING"]:
	app.config["PROPAGATE_EXCEPTIONS"] = False

app.app_context().push()

from ams.functions.functions import app_logger
# logger setup done

# importing controllers
from ams.controllers.common_routes import *
from ams.controllers.accounting import *
from ams.controllers.admin_routes import *
from ams.controllers.lib_routes import *
from ams.controllers.user_routes import *

from ams.views.commom import *

if __name__ == "__main__":
	try:
		app.run(
			host = "0.0.0.0"
			, port = 8000
		)
	except Exception as e:
		app_logger.critical(e)
