import datetime

from flask import current_app as app
from os.path import join as path_join

from jinja2 import Template
from weasyprint import HTML

from ..CeleryConfig import celery
from ...models.DB_object import DB

from ...functions.functions import sendBulkHTMLMails, sendSingleHTMLMail


REPORT_PERIOD = str(datetime.datetime.now().month-1 if datetime.datetime.now().month > 1 else 12) + '-' + str(datetime.datetime.now().year)
REPORT_PERIOD = '08-2024'

@celery.task()
def book_not_opened_yet_reminder():
	from ...models.DB_Models import BorrowHistory

	from ...functions.functions import sendBulkHTMLMails
	from jinja2 import Template

	listUnopendBook = DB.session.query(
		BorrowHistory
	).filter(
		BorrowHistory.is_opened   ==  0
	).all()

	u_dict = {}
	for i in listUnopendBook:
		name_title = ''

		if i.relation_issued_to.gender == 'M':
			name_title = 'Mr.'
		if i.relation_issued_to.gender == 'F':
			name_title = 'Ms./Mrs.'

		u_dict[i.relation_issued_to.email] = {
			'name_title'	: name_title
			, 'name'		: i.relation_issued_to.name
		}

	sendBulkHTMLMails(
		addresses		=	  set(u_dict.keys())		  # using python set, we can have distinct email ids
		, subject		=	  'Reminder for your recent rental/purchase'
		, HTMLTemplate   =	  Template(
									open(
										path_join(
											app.root_path
											, 'ams'
											, 'EmailTemplates'
											, 'EmailTemplate_book_not_opned_yet_reminder.html'
										)
									, 'r').read()
								)
		, TemplateData   =	  u_dict
	)

@celery.task()
def due_date_reminder():
	from ...models.DB_Models import BorrowHistory

	from ...functions.functions import sendBulkHTMLMails

	from jinja2 import Template

	from datetime import date, datetime, timedelta

	listBooksToDue = DB.session.query(
		BorrowHistory
	).filter(
		BorrowHistory.is_returned	   ==  0
		, BorrowHistory.date_of_return  ==  datetime.strftime(datetime.now() + timedelta(days = app.config['DUE_DATE_REMINDER_PRIOR_DAYS']), '%Y-%m-%d')
	).all()

	u_dict = {}
	for i in listBooksToDue:
		name_title = ''

		if i.relation_issued_to.gender == 'M':
			name_title = 'Mr.'
		if i.relation_issued_to.gender == 'F':
			name_title = 'Ms./Mrs.'

		u_dict[i.relation_issued_to.email] = {
			'name_title'	: name_title
			, 'name'		: i.relation_issued_to.name
			, 'book_title'  : i.relation_book_id.title
		}

	sendBulkHTMLMails(
		addresses		=	  set(u_dict.keys())		  # using python set, we can have distinct email ids
		, subject		=	  'Due date reminder'
		, HTMLTemplate   =	  Template(
									open(
										path_join(
											app.root_path
											, 'ams'
											, 'EmailTemplates'
											, 'EmailTemplate_due_date_reminder.html'
										)
									, 'r').read()
								)
		, TemplateData   =	  u_dict
	)

@celery.task()
def send_montly_activity_report():
	from ...models.DB_Models import BorrowHistory, Books, Users, RelBooksAuthors
	from sqlalchemy import asc, extract

	user_details = DB.session.query(
		Users
	).filter(
		Users.role		  	==  2
		, Users.is_active   ==  1
		, Users.is_deleted  ==  0
	).all()

	u_dict = {}
	for user in user_details:
		name_title = ''

		if user.gender == 'M':
			name_title = 'Mr.'
		if user.gender == 'F':
			name_title = 'Ms./Mrs.'

		u_dict[user.email] = {
			'name_title'		:   name_title
			, 'name'			:   user.name
			, 'prefer_pdf'		:	user.prefer_pdf_monthly_report
		}

		###
		# REPORT_PERIOD = '04-2024'

		list_history = DB.session.query(BorrowHistory).filter(
			BorrowHistory.issued_to == user.user_id
			, extract('month', BorrowHistory.current_timestamp) == REPORT_PERIOD.split('-')[0]
			, extract('year', BorrowHistory.current_timestamp) == REPORT_PERIOD.split('-')[1]
		).order_by(
			asc(BorrowHistory.current_timestamp)
		).all()

		records_data	=	[]

		if len(list_history) > 0:
			for tup in list_history:
				tmp = dict()

				theBook = DB.session.query(Books).filter_by(
					book_id = tup.book_id
				).one()

				tmp["book_authors"]		=	[]
				authors = DB.session.query(RelBooksAuthors).filter(
					RelBooksAuthors.book_id == theBook.book_id
				).all()

				for a in authors:
					tmp["book_authors"].append(a.relation_author_id.name)

				tmp["book_isbn"]		=	theBook.isbn
				tmp["book_title"]		=	theBook.title
				tmp["date_issued"]		=	datetime.datetime.strftime(tup.date_of_issue, '%d-%m-%Y') if tup.date_of_issue is not None else 'NA'
				tmp["date_returned"]	=	datetime.datetime.strftime(tup.date_returned, '%d-%m-%Y') if tup.date_returned is not None else 'NA'

				records_data.append(tmp)

		u_dict[user.email]['table_data']	=	records_data.copy()
		u_dict[user.email]['report_period'] =	REPORT_PERIOD

	for eachEmail in u_dict:
		if u_dict[eachEmail]['prefer_pdf']:
			pdf_attachment = None

			if len(u_dict[eachEmail]['table_data']) > 0:
				HTML(string = Template(
					open(
						path_join(
							app.root_path
							, 'ams'
							, 'EmailTemplates'
							, 'pdf'
							, 'user_monthly_activity.html'
						)
					, 'r').read()
				).render(u_dict[eachEmail])).write_pdf('/tmp/user_monthly_activity_report-{}.pdf'.format(REPORT_PERIOD))

				pdf_attachment = {
					'file'		:	'/tmp/user_monthly_activity_report-{}.pdf'.format(REPORT_PERIOD)
					, 'filename':	'/tmp/user_monthly_activity_report-{}.pdf'.format(REPORT_PERIOD)
				}

			sendSingleHTMLMail(
				email			=	eachEmail
				, subject		=	'Reader Monthly Activity Report - Project LMS'
				, HTMLTemplate  =	Template(
										open(
											path_join(
												app.root_path
												, 'ams'
												, 'EmailTemplates'
												, 'EmailTemplate_user_monthly_activity_report_for_pdf.html'
											)
										, 'r').read()
									)
				, TemplateData   =	u_dict[eachEmail]
				, attachment	 = pdf_attachment
			)
		else:
			sendSingleHTMLMail(
				email			=	eachEmail
				, subject		=	'Reader Monthly Activity Report - Project LMS'
				, HTMLTemplate  =	Template(
										open(
											path_join(
												app.root_path
												, 'ams'
												, 'EmailTemplates'
												, 'EmailTemplate_user_monthly_activity_report.html'
											)
										, 'r').read()
									)
				, TemplateData   =	u_dict[eachEmail]
			)



