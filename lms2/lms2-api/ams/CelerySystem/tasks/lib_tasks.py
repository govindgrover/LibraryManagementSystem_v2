from flask import current_app as app
from os.path import join as path_join

from .. import CeleryConfig
celery = CeleryConfig.celery

from ...models.DB_object import DB
from ...models.DB_Models import Users

from ...functions.functions import sendBulkHTMLMails, sendSingleHTMLMail

from jinja2 import Template
from weasyprint import HTML


import matplotlib.pyplot as plt
import numpy as np
import base64
import io

from sqlalchemy import text
from datetime import datetime

REPORT_PERIOD = str(datetime.now().month-1 if datetime.now().month > 1 else 12)+'-'+str(datetime.now().year)
REPORT_PERIOD = '08-2024'

class GraphMaker():

	__PLOT_COLORS__ :list = [
		"#00897B", "#43A047", "#7CB342"
		, "#C0CA33", "#FFB300", "#FB8C00"
		, "#F4511E"
	]


	def __set_size_and_make_buffer(self, figObject):
		figObject.set_size_inches(10, 8)

		buffer = io.BytesIO()
		figObject.savefig(buffer, format='png')
		buffer.seek(0)

		return base64.b64encode(buffer.getvalue()).decode()


	def _get_bar_graph(self, data: dict, graph_title :str, x_title :str, y_title :str,):
		fig, ax = plt.subplots()

		ax.bar(
			data.keys(), data.values()
			, width=0.6
			, color = self.__PLOT_COLORS__
			, linewidth=1
		)

		plt.yticks(np.arange(
			min(data.values())
			, max(data.values()) + 1
			, 1
		))

		plt.title(graph_title)
		plt.xlabel(x_title)
		plt.ylabel(y_title)

		return self.__set_size_and_make_buffer(fig)


	def _get_pie_graph(self, data :dict, graph_title :str):
		fig, ax = plt.subplots()

		ax.pie(
			data.values()
			, labels	=	data.keys()
			, colors	=	self.__PLOT_COLORS__
			, wedgeprops=	{
				"linewidth"		:	2
				, "edgecolor"	:	"white"
			}
		)

		plt.title(graph_title)

		return self.__set_size_and_make_buffer(fig)


	def _get_stem_graph(self, data: dict, graph_title :str, x_title :str, y_title :str,):
		fig, ax = plt.subplots()

		ax.stem(
			data.keys()
			, data.values()
		)

		ax.set(label = data.keys())

		plt.yticks(np.arange(
			min(data.values())
			, max(data.values()) + 1
			, 1
		))

		plt.title(graph_title)
		plt.xlabel(x_title)
		plt.ylabel(y_title)

		return self.__set_size_and_make_buffer(fig)


	def _get_plot_graph(self, data: dict, graph_title :str, x_title :str, y_title :str,):
		fig, ax = plt.subplots()

		ax.plot(
			data.keys()
			, data.values()
		)

		ax.set(label = data.keys())

		plt.yticks(np.arange(
			min(data.values())
			, max(data.values()) + 1
			, 1
		))

		plt.title(graph_title)
		plt.xlabel(x_title)
		plt.ylabel(y_title)

		return self.__set_size_and_make_buffer(fig)


	def _get_custom_plot_graph(self, data: dict, graph_title :str, y_title :list,):
		fig, ax = plt.subplots()
		gs = fig.add_gridspec(2, 1)
		axs = gs.subplots(sharex=True, sharey=False)

		# removing the label from the whole graph
  		# later will apply as per the requirement
		ax.set_xticklabels([])
		ax.set_yticklabels([])

		tmp0 = []
		for x in list(data.values()):
			tmp0.append(x[0])

		tmp1 = []
		for x in list(data.values()):
			tmp1.append(x[1])

		axs[0].plot(
			data.keys()
			, tmp0
			, color = self.__PLOT_COLORS__[0]
			, linewidth = 2
		)
		axs[1].plot(
			data.keys()
			, tmp1
			, color = self.__PLOT_COLORS__[1]
			, linewidth = 2
		)

		axs[0].set_yticks(np.arange(
			min(tmp0)
			, max(tmp0) + 15
			, 15
		))

		axs[1].set_yticks(np.arange(
			min(tmp1)
			, max(tmp1) + 50
			, 50
		))

		plt.suptitle(graph_title)
		axs[0].set_ylabel(y_title[0])
		axs[1].set_ylabel(y_title[1])

		return self.__set_size_and_make_buffer(fig)


	def get_graphs_on_request(self, is_monthly :bool = False):
		image_buff = dict()

		to_dos = [
			{
				"name": "category_names_vs_book_count.png"
				, "query": """
					SELECT DISTINCT(c.name) AS name, COUNT(r.book_id) AS count
						FROM category c, rel_books_category r
					WHERE r.category_id = c.category_id
					{}
						GROUP BY r.category_id;
				""".format(
					("AND STRFTIME('%m-%Y', c.current_timestamp) == '"+ REPORT_PERIOD +"'") if (is_monthly == True) else ""
				)
				, "graph_type": "bar"
				, "titles": [
					"Distribution of books into categories"
					, "Distinct categories"
					, "Book count"
				]
			}
			, {
				"name": "genre_names_vs_book_count.png"
				, "query": """
					SELECT DISTINCT(g.name) AS name, COUNT(r.book_id) AS count
						FROM genre g, rel_books_genre r
					WHERE r.genre_id = g.genre_id
					{}
						GROUP BY r.genre_id;
				""".format(
					("AND STRFTIME('%m-%Y', g.current_timestamp) == '"+ REPORT_PERIOD +"'") if (is_monthly == True) else ""
				)
				, "graph_type": "bar"
				, "titles": [
					"Distribution of books into genre"
					, "Distinct genres"
					, "Book count"
				]
			}
			, {
				"name": "language_names_vs_book_count.png"
				, "query": """
					SELECT DISTINCT(l.name) AS name, COUNT(r.book_id) AS count
						FROM language l, rel_books_language r
					WHERE r.lang_id = l.lang_id
					{}
						GROUP BY r.lang_id;
				""".format(
					("AND STRFTIME('%m-%Y', l.current_timestamp) == '"+ REPORT_PERIOD +"'") if (is_monthly == True) else ""
				)
				, "graph_type": "bar"
				, "titles": [
					"Distribution of books into languages"
					, "Distinct languages"
					, "Book count"
				]
			}
			, {
				"name": "readers_gender_vs_book_count.png"
				, "query": """
					SELECT u.gender, count(u.gender) AS count
						FROM users u
					WHERE u.role = 2
					{}
						GROUP BY u.gender;
				""".format(
					("AND STRFTIME('%m-%Y', u.current_timestamp) == '"+ REPORT_PERIOD +"'") if (is_monthly == True) else ""
				)
				, "graph_type": "bar"
				, "titles": [
					"Distribution of readers into gender"
					, "Gender"
					, "Reader count"
				]
			}
			, {
				"name": "publishers_vs_book_count.png"
				, "query": """
					SELECT p.name AS name, count(p.name) AS count
						FROM publisher p, rel_books_publisher r
					WHERE r.publisher_id = p.publisher_id AND p.is_active = 1
					{}
						GROUP BY p.name;
				""".format(
					("AND STRFTIME('%m-%Y', p.current_timestamp) == '"+ REPORT_PERIOD +"'") if (is_monthly == True) else ""
				)
				, "graph_type": "pie"
				, "titles": [
					"Distribution of books under active publishers"
				]
			}
			, {
				"name": "authors_vs_book_count.png"
				, "query": """
					SELECT a.name AS name, count(a.name) AS count
						FROM authors a, rel_books_authors r
					WHERE r.author_id = a.author_id AND a.is_active = 1
					{}
						GROUP BY a.name;
				""".format(
					("AND STRFTIME('%m-%Y', a.current_timestamp) == '"+ REPORT_PERIOD +"'") if (is_monthly == True) else ""
				)
				, "graph_type": "pie"
				, "titles": [
					"Distribution of books under active authors"
				]
			}
			, {
				"name": "unanswered_issue_requests.png"
				, "query": """
					SELECT strftime("%d-%m-%Y", br.current_timestamp) date, count(*) AS count
						FROM borrow_requests br
					WHERE br.request_processed = 0
					{}
						GROUP BY strftime("%d-%m-%Y", br.current_timestamp);
				""".format(
					("AND STRFTIME('%m-%Y', br.current_timestamp) == '"+ REPORT_PERIOD +"'") if (is_monthly == True) else ""
				)
				, "graph_type": "stem"
				, "titles": [
					"Number of unanswered issue requests"
					, "Dates"
					, "Number of requests"
				]
			}
			, {
				"name": "total_issue_requests_raised_trend.png"
				, "query": """
					SELECT date(b.current_timestamp) AS date, COUNT(*) AS count
						FROM borrow_history b
						{}
					GROUP BY date(b.current_timestamp)
						ORDER BY date(b.current_timestamp) ASC;
				""".format(
					("WHERE STRFTIME('%m-%Y', b.current_timestamp) == '"+ REPORT_PERIOD +"'") if (is_monthly == True) else ""
				)
				, "graph_type": "plot"
				, "titles": [
					"Number of requests raised"
					, "Dates"
					, "Number of requests"
				]
			}
			, {
				"name": "count_and_sum_by_date_of_book_purchase.png"
				, "query": """
					SELECT strftime("%m-%Y", bp.current_timestamp) AS date, COUNT(*) AS count, SUM(cost) AS total_cost
						FROM book_purchases bp
						{}
					GROUP BY strftime("%m-%Y", bp.current_timestamp);
				""".format(
					("WHERE STRFTIME('%m-%Y', bp.current_timestamp) == '"+ REPORT_PERIOD +"'") if (is_monthly == True) else ""
				)
				, "graph_type": "custom-plot-01"
				, "titles": [
					"Count (upper) and Sum of costs (lower) of book purchases for each month"
					, "Months"
					, [
						"Count"
						, "Sum of cost"
					]
				]
			}
			, {
				"name": "top_5_selling_books.png"
				, "query": """
					SELECT substr(b.title, -length(b.title), 27) || "..." AS title, count(bh.book_id) AS count
						FROM books b, borrow_history bh
					WHERE bh.book_id = b.book_id
					{}
						GROUP BY bh.book_id
					ORDER BY count DESC
						LIMIT 5;
				""".format(
					("AND STRFTIME('%m-%Y', bh.current_timestamp) == '"+ REPORT_PERIOD +"'") if (is_monthly == True) else ""
				)
				, "graph_type": "bar"
				, "titles": [
					"Top 5 selling books"
					, "Book titles"
					, "Counts sold"
				]
			}
		]

		for to_do in to_dos:
			results		=	DB.session.execute(text(to_do["query"]))
			tmp_dict	=	dict()

			for result in results:
				if len(result) == 2:
					tmp_dict[result[0]] = result[1]
				elif len(result) == 3:
					tmp_dict[result[0]] = (result[1], result[2])

			if tmp_dict == {}:
				continue

			if to_do["graph_type"] == "bar":
				image_buff[to_do["name"]] = str(self._get_bar_graph(
					data 			=	tmp_dict
					, graph_title	=	to_do["titles"][0]
					, x_title		=	to_do["titles"][1]
					, y_title		=	to_do["titles"][2]
				))
			elif to_do["graph_type"] == "pie":
				image_buff[to_do["name"]] = str(self._get_pie_graph(
					data			=	tmp_dict
					, graph_title	=	to_do["titles"][0]
				))
			elif to_do["graph_type"] == "stem":
				image_buff[to_do["name"]] = str(self._get_stem_graph(
					data			=	tmp_dict
					, graph_title	=	to_do["titles"][0]
					, x_title		=	to_do["titles"][1]
					, y_title		=	to_do["titles"][2]
				))
			elif to_do["graph_type"] == "plot":
				image_buff[to_do["name"]] = str(self._get_plot_graph(
					data			=	tmp_dict
					, graph_title	=	to_do["titles"][0]
					, x_title		=	to_do["titles"][1]
					, y_title		=	to_do["titles"][2]
				))
			elif to_do["graph_type"] == "custom-plot-01":
				image_buff[to_do["name"]] = str(self._get_custom_plot_graph(
					data			=	tmp_dict
					, graph_title	=	to_do["titles"][0]
					, y_title		=	to_do["titles"][2]
				))

		return image_buff


@celery.task()
def lib_activity_report(requestee_id: str):
	listLibrarians = DB.session.query(
		Users
	).filter(
		Users.role		  	==  1
		, Users.is_active   ==  1
		, Users.is_deleted  ==  0
		, Users.user_id 	==	requestee_id
	).all()

	GM = GraphMaker()
	analytics_data = GM.get_graphs_on_request()

	u_dict = {}
	for i in listLibrarians:
		name_title = ''

		if i.gender == 'M':
			name_title = 'Mr.'
		if i.gender == 'F':
			name_title = 'Ms./Mrs.'

		u_dict[i.email] = {
			'name_title'		:   name_title
			, 'name'			:   i.name
			, 'analytics_data'  :   analytics_data
			, 'requested_date'	:	datetime.strftime(datetime.now(), '%A, %B %d %Y')

		}

	sendBulkHTMLMails(
		addresses	   =	  list(u_dict.keys())
		, subject	   =	  'Requested Activity Report for Librarian - Project LMS'
		, HTMLTemplate  =	  Template(
									open(
										path_join(
											app.root_path
											, 'ams'
											, 'EmailTemplates'
											, 'EmailTemplate_lib_activity_report.html'
										)
									, 'r').read()
								)
		, TemplateData  =	  u_dict
	)

@celery.task()
def lib_monthly_report():
	listLibrarians = DB.session.query(
		Users
	).filter(
		Users.role		  ==  1
		, Users.is_active   ==  1
		, Users.is_deleted  ==  0
	).all()


	GM = GraphMaker()
	analytics_data = GM.get_graphs_on_request(is_monthly = True)

	u_dict = {}
	for i in listLibrarians:
		name_title = ''

		if i.gender == 'M':
			name_title = 'Mr.'
		if i.gender == 'F':
			name_title = 'Ms./Mrs.'

		u_dict[i.email] = {
			'name_title'		:   name_title
			, 'name'			:   i.name
			, 'analytics_data'  :   analytics_data
			, 'report_period'	:	str(REPORT_PERIOD)
			# , 'prefer_pdf'		:	i.prefer_pdf_monthly_report

		}

	sendBulkHTMLMails(
		addresses		=	  list(u_dict.keys())		  # using python set, we can have distinct email ids
		, subject		=	  'Monthly Report for Librarians - Project LMS'
		, HTMLTemplate  =	  Template(
									open(
										path_join(
											app.root_path
											, 'ams'
											, 'EmailTemplates'
											, 'EmailTemplate_lib_monthly_report.html'
										)
									, 'r').read()
								)
		, TemplateData   =	  u_dict
	)

	# for eachEmail in u_dict:
		# if u_dict[eachEmail]['prefer_pdf']:
		# 	pdf_attachment = None

		# 	if len(u_dict[eachEmail]['analytics_data']) > 0:
		# 		HTML(string = Template(
		# 			open(
		# 				path_join(
		# 					app.root_path
		# 					, 'ams'
		# 					, 'EmailTemplates'
		# 					, 'pdf'
		# 					, 'librarian_monthly_activity.html'
		# 				)
		# 			, 'r').read()
		# 		).render(u_dict[eachEmail])).write_pdf('/tmp/librarian_monthly_activity_report-{}.pdf'.format(REPORT_PERIOD))

		# 		pdf_attachment = {
		# 			'file'		:	'/tmp/librarian_monthly_activity_report-{}.pdf'.format(REPORT_PERIOD)
		# 			, 'filename':	'/tmp/librarian_monthly_activity_report-{}.pdf'.format(REPORT_PERIOD)
		# 		}

		# 	sendSingleHTMLMail(
		# 		email			=	eachEmail
		# 		, subject		=	'Librarian Monthly Activity Report - Project LMS'
		# 		, HTMLTemplate  =	Template(
		# 								open(
		# 									path_join(
		# 										app.root_path
		# 										, 'ams'
		# 										, 'EmailTemplates'
		# 										, 'EmailTemplate_lib_monthly_report.html'
		# 									)
		# 								, 'r').read()
		# 							)
		# 		, TemplateData   =	u_dict[eachEmail]
		# 		, attachment	 = pdf_attachment
		# 	)
		# else:
		# 	sendSingleHTMLMail(
		# 		email			=	eachEmail
		# 		, subject		=	'Librarian Monthly Activity Report - Project LMS'
		# 		, HTMLTemplate  =	Template(
		# 								open(
		# 									path_join(
		# 										app.root_path
		# 										, 'ams'
		# 										, 'EmailTemplates'
		# 										, 'EmailTemplate_lib_monthly_report.html'
		# 									)
		# 								, 'r').read()
		# 							)
		# 		, TemplateData   =	u_dict[eachEmail]
		# 	)


@celery.task()
def download_all_borrow_history(requestee_id: str):
	from ...models.DB_Models import BorrowHistory, BorrowRequest, Books, Users, Authors, RelBooksAuthors
	from sqlalchemy import asc

	import tempfile
	import csv
	from os import remove as remove_file

	lib_user_details = DB.session.query(
		Users
	).filter(
		Users.role		  	==  1
		, Users.is_active   ==  1
		, Users.is_deleted  ==  0
		, Users.user_id 	==	requestee_id
	).all()

	u_dict = {}
	for i in lib_user_details:
		name_title = ''

		if i.gender == 'M':
			name_title = 'Mr.'
		if i.gender == 'F':
			name_title = 'Ms./Mrs.'

		u_dict[i.email] = {
			'name_title'		:   name_title
			, 'name'			:   i.name
		}

	list_all_request = DB.session.query(BorrowHistory).order_by(
		asc(BorrowHistory.current_timestamp)
	).all()

	records_data = []

	if len(list_all_request) > 0:
		for tup in list_all_request:
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

			tmp["max_price"]				=	theBook.price
			tmp["book_isbn"]				=	theBook.isbn
			tmp["book_title"]				=	theBook.title
			tmp["requested_by_name"]		=	tup.relation_issued_to.name
			tmp["request_approved_by_name"]	=	tup.relation_issued_by.name
			tmp["date_of_issue"]			=	datetime.strftime(tup.date_of_issue, '%d-%m-%Y') if tup.date_of_issue is not None else 'NA'
			tmp["date_of_return"]			=	datetime.strftime(tup.date_of_return, '%d-%m-%Y') if tup.date_of_return is not None else 'NA'
			tmp["is_purchased"]				=	tup.is_purchased
			tmp["is_returned"]				=	tup.is_returned
			tmp["is_opened"]				=	tup.is_opened

			records_data.append(tmp)

	with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', suffix='.csv') as temp_file:
		writer = csv.writer(temp_file)

		writer.writerow(list(records_data[0].keys()))		# writing headers
		for line in records_data:
			writer.writerow(list(line.values()))			# writing data

		temp_file_path = temp_file.name

	sendBulkHTMLMails(
		addresses		=	list(u_dict.keys())		  # using python set, we can have distinct email ids
		, subject		=	'Requested Borrance Report for Librarians - Project LMS'
		, HTMLTemplate  =	Template(
								open(
									path_join(
										app.root_path
										, 'ams'
										, 'EmailTemplates'
										, 'EmailTemplate_lib_download_all_borrows.html'
									)
								, 'r').read()
							)
		, TemplateData   =	u_dict
		, attachment	 = 	{
			'file'		:	temp_file_path
			, 'filename':	'lib-requested-borrowance-report-' + datetime.strftime(datetime.now(), '%d-%m-%Y') + '.csv'
		}
	)

	remove_file(temp_file_path)
