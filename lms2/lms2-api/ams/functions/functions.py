# =============================================================================
# ==================== [ SETUP FOR API LOGGER (ONLY ONCE) ] ===================
# =============================================================================

from ..models.APILogger import APILogger

# setting-up logger
api_logger = APILogger().logger


# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# importing flask' current app
from flask import current_app as app

# to abort the connection when needed
from flask import abort

# to check JWT data
from flask_jwt_extended import get_jwt

# to create app-specific decorator function(s)
from functools import wraps

# for 'sendBulkHTMLMails()'
import jinja2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ++++++++++++++++++++++++++++++++ END IMPORTS ++++++++++++++++++++++++++++++++


def role_restriction(allowed_roles : list):
	"""
	Function to allow only `allowed_roles` to proceed and abort(a Flask function) otherwise 
	"""

	def decorator(fn):

		@wraps(fn)
		def wrapper(*args, **kwargs):
			# u = Users()
			current_user_role = get_jwt()["role"] if ("role" in get_jwt()) else None

			if (
				(current_user_role not in allowed_roles)
				and not app.config["TESTING"]				# API-DEBUG
			):
			# if (
			# 	not u.has_permission(permission = permission_)
			# ):
				return abort(403)

			return fn(*args, **kwargs)
		
		return wrapper
	
	return decorator

def sendBulkHTMLMails(addresses: list, subject: str, HTMLTemplate: jinja2.Template, TemplateData: dict, attachment: dict = None):	
	try:
		for email in addresses:
			smtp_ = smtplib.SMTP()
			smtp_.connect(
				host 	=	app.config['SMTP_SERVER_HOST']
				, port 	=	app.config['SMTP_SERVER_PORT']
			)
			# connected to SMTP Server

			smtp_.login(app.config['SENDER_ADDRESS'], app.config['SENDER_PASSWORD'])
			# logged in the connected server

			msg = MIMEMultipart()
			msg['From']		=	app.config['SENDER_ADDRESS']
			msg['To']		=	email
			msg['Subject']	=	subject
			# basics done

			if attachment is not None:
				from email.mime.application import MIMEApplication

				with open(attachment['file'], 'rb') as f:
					mime = MIMEApplication(f.read(), name=attachment['filename'])
					mime['Content-Disposition'] = f'attachment; filename="' + attachment['filename'] + '"'
					msg.attach(mime)

			msg.attach(MIMEText(HTMLTemplate.render(TemplateData[email]), 'html'))
			# attached html

			smtp_.send_message(msg)
			# sended

			smtp_.quit()
			# byee

		return True

	except Exception as e:
		api_logger.warning(f"Unable to send Email. E: {e}")
		return False

def sendSingleHTMLMail(email: list, subject: str, HTMLTemplate: jinja2.Template, TemplateData: dict, attachment: dict = None):	
	try:
		smtp_ = smtplib.SMTP()
		smtp_.connect(
			host 	=	app.config['SMTP_SERVER_HOST']
			, port 	=	app.config['SMTP_SERVER_PORT']
		)
		# connected to SMTP Server

		smtp_.login(app.config['SENDER_ADDRESS'], app.config['SENDER_PASSWORD'])
		# logged in the connected server

		msg = MIMEMultipart()
		msg['From']		=	app.config['SENDER_ADDRESS']
		msg['To']		=	email
		msg['Subject']	=	subject
		# basics done

		if attachment is not None:
			from email.mime.application import MIMEApplication

			with open(attachment['file'], 'rb') as f:
				mime = MIMEApplication(f.read(), name=attachment['filename'])
				mime['Content-Disposition'] = f'attachment; filename="' + attachment['filename'] + '"'
				msg.attach(mime)

		msg.attach(MIMEText(HTMLTemplate.render(TemplateData), 'html'))
		# attached html

		smtp_.send_message(msg)
		# sended

		smtp_.quit()
		# byee

		return True
	except Exception as e:
		api_logger.warning(f"Unable to send Email. E: {e}")
		return False
