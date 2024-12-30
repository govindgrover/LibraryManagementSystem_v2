# +++++++++++++++++++++++++++++ START APP IMPORTS +++++++++++++++++++++++++++++

# tools
import os
import json

# flask modules
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

# ++++++++++++++++++++++++++++++ END APP IMPORTS ++++++++++++++++++++++++++++++


# ++++++++++++++++++++++++++++++ START APP SETUP ++++++++++++++++++++++++++++++

# creating flask APP
app = Flask(__name__)

# setting configuration from file
app.config.from_file(
	os.path.join(
		app.root_path
		, "ams"
		, "config.json"
	)
	, load = json.load
)

app.config["SQLALCHEMY_DATABASE_URI"] = r"sqlite:///" + os.path.join(app.root_path, "ams", "database", app.config["SQLITE_DB"])

# overriding for testing purposes
if app.config["TESTING"]:
	app.config["PROPAGATE_EXCEPTIONS"] = False

# importing `DB` object for setup
from ams.models.DB_object import DB

# initializing sqlalchemy database to the APP
DB.init_app(app)
app.app_context().push()

# creating API object of the APP
api = Api(app)

# setting-up Flask-JWT Authentication
jwt = JWTManager(app)

# setup for expired JWT token
from ams.models.APIResponse import APIResponse

@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
	if not app.config["TESTING"]:
		return APIResponse(
			success			=	False
			, status_code	=	428
			, errors		=	[
				"Bearer Authorization Token Expired!"
			]
		).get_response()
	else:
		return {}

# importing logging mechanism
from ams.functions.functions import api_logger

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')
# updating the static value, if any

# ++++++++++++++++++++++++++++++ END APP SETUP ++++++++++++++++++++++++++++++++


# +++++++++++++++++++++++++++++ START CACHE SETUP +++++++++++++++++++++++++++++

from ams.models import CacheConfig
app.app_context().push()

if app.config['DEBUG']:
	CacheConfig.api_cache.clear()
	app.config['CACHE_DEFAULT_TIMEOUT'] = 5		# if DEBUG then expire the cache every after 5s
	print('DEBUG MODE ACTIVE!! CACHE API CLEARED BEFORE RUN UP. AND DEFAULT EXPIRY SET TO 5s.')

# ++++++++++++++++++++++++++++++ END CACHE SETUP ++++++++++++++++++++++++++++++


# ++++++++++++++++++++++++++++ START CELERY SETUP +++++++++++++++++++++++++++++

# setting-up Celery and other conf
from ams.CelerySystem.CeleryConfig import CeleryContextClass, celery

from ams.CelerySystem.tasks.user_tasks import (
	book_not_opened_yet_reminder, due_date_reminder
	, send_montly_activity_report
)
# user tasks imported

from ams.CelerySystem.tasks.lib_tasks import (
	lib_monthly_report, download_all_borrow_history
)
# librarian tasks imported

from celery.schedules import crontab

celery.conf.update(
	broker_url		=	app.config["CELERY_BROKER_URL"]
	, result_backend=	app.config["CELERY_BACKEND_URL"]
	, enable_utc	=	False
	# , timezone = "Asia/Kolkata"
	# , broker_connection_retry_on_startup = True
)

celery.Task = CeleryContextClass
app.app_context().push()

celery.conf.beat_schedule = {
		'beat-schedule-book_not_opened_yet_reminder': {
			'task'		:	'ams.CelerySystem.tasks.user_tasks.book_not_opened_yet_reminder'
			, 'schedule':	crontab(hour = 8)
		}
		# reminder to those will be sent until the user not opens the book

		, 'beat-schedule-due_date_reminder': {
			'task'		:	'ams.CelerySystem.tasks.user_tasks.due_date_reminder'
			, 'schedule':	crontab(hour = 11, minute = 35)
		}
		# reminder to those will be sent one day prior to due date

		, 'beat-schedule-lib_monthly_report': {
			'task'		:	'ams.CelerySystem.tasks.lib_tasks.lib_monthly_report'
			, 'schedule':	crontab(day_of_month=1)
		}
		# montly analytics will be sent to all librarians 

		, 'beat-schedule-montly_ebook_analysis': {
			'task'		:	'ams.CelerySystem.tasks.user_tasks.send_montly_activity_report'
			, 'schedule':	crontab(day_of_month=1)
		}
		# montly analytics will be sent to all readers
	}

# ++++++++++++++++++++++++++++++ END CELERY SETUP +++++++++++++++++++++++++++++


# +++++++++++++++++++++++ START IMPORTING API RESOURCES +++++++++++++++++++++++

# Accounts Resourece
from ams.resources.AccountResource import AccountResource

# Operational Resources
from ams.resources.BookMasterOperationalResource import BookMasterOperationalResource
from ams.resources.BookOperationResource import BookOperationResource

# Interactional Resources
from ams.resources.UserInteractionResource import UserInteractionResource
from ams.resources.LibrarianInteractionResource import LibrarianInteractionResource

# Filter Resources
from ams.resources.BookFilterResource import BookFilterResource
from ams.resources.BookMasterFilterResource import BookMasterFilterResource
from ams.resources.UserFilterResource import UserFilterResource

# Book Retrival Resource
from ams.resources.BookRetrivalResource import BookRetrivalResource

# Static Folder Retrival Resource
from ams.resources.GetStaticFiles import GetStaticFiles

# Statistical Analysis Resource
from ams.resources.AnalysisResource import AnalysisResource

# ++++++++++++++++++++++++ END IMPORTING API RESOURCES ++++++++++++++++++++++++


# +++++++++++++++++++++++++ START API ENDPOINTS SETUP +++++++++++++++++++++++++

# for dealing with different user accounts
api.add_resource(AccountResource, "/api/v2/user/account/")

# for dealing with book's master attributes by admin and/or librarian
api.add_resource(BookMasterOperationalResource, "/api/v2/book/master/<component_name>")

# for dealing with books and its fields by admin and/or librarian
api.add_resource(BookOperationResource, "/api/v2/book/operation/")

# for dealing with interactions by the other users;
api.add_resource(UserInteractionResource, "/api/v2/interact/user")

# for dealing with interactions made by the admin or librarian;
api.add_resource(LibrarianInteractionResource, "/api/v2/interact/librarian")


# for applying different filter on the books
api.add_resource(BookFilterResource, "/api/v2/fetch/details/books")

# for applying different filter on the book's master
api.add_resource(BookMasterFilterResource, "/api/v2/fetch/details/master/<master_name>")

# for applying different filter on the users
api.add_resource(UserFilterResource, "/api/v2/fetch/details/users")

# to retrive the book's content file with valid access token
api.add_resource(BookRetrivalResource, "/api/v2/book/retrive/<access_token>")

# to retrive the content of static folder
api.add_resource(GetStaticFiles, "/api/v2/fetch/static/<directory>/<filename>")


# for getting analytical data to make graphs
api.add_resource(AnalysisResource, "/api/v2/analyze")

# ++++++++++++++++++++++++++ END API ENDPOINTS SETUP ++++++++++++++++++++++++++

# =============================================================================
# ============================== [ RUNNING APP ] ==============================
# =============================================================================
if __name__ == "__main__":
	try:
		app.run(
			host = "0.0.0.0"
			, port = 5000
		)
	except Exception as e:
		api_logger.error(e)
