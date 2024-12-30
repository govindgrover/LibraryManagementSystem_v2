# +++++++++++++++++++++++++++++++ START IMPORTS +++++++++++++++++++++++++++++++

# importing flask' current app
from flask import current_app as app

# to handle requests
from flask import request

# to abort the connection when needed
from flask import abort

# importing SQLAlchemy's Error class to handle errors
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy import text

# importing Flask Restful-API Resources
from flask_restful import Resource

# importing Flask-JWT methods
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt

# to handle date conversion from string to python' date-object
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import io

# importing APIResponse to make responses
from ..models.APIResponse import APIResponse 

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



# =============================================================================
# ======================== [ AnalysisResource ] ========================
# =============================================================================

class AnalysisResource(Resource):
	"""
	This resource class is used to handle the following:
		* 

		Direct Database Table(s) used: 
			`books`, `review`, `book_purchase`
			, `borrow_request`, `borrow_history`
	"""

	__PLOT_COLORS__ :list = [
		"#00897B", "#43A047", "#7CB342"
		, "#C0CA33", "#FFB300", "#FB8C00"
		, "#F4511E"
	]

	def __init__(self):
		# getting request JSON
		if request.is_json:
			self.request_action	=	request.get_json()["action"]

			# since sometimes we dont need the key 'body' to be present.
			if "body" in request.get_json():
				self.json_body		=	request.get_json()["body"]

			return
		
		# getting request POST-Form
		elif len(request.form):
			self.request_action	=	request.form.get("action")
			self.request_form	=	request.form

			# since there is possibilty of having file when POST-Form is sent
			self.request_files	=	request.files

			return

		# getting request GET-Parameters
		elif len(request.args) > 0:
			self.get_body		=	request.args

			return

		api_logger.critical(
			"Invalid Request-Data has been sent; ie, neither JSON nor POST-Form nor GET-Parameters. Hence aborted the connection!"
		)
		abort(code = 404)


	def __invalidActionError(self):
		"""
		Internal Function to return response with `code = 406` if the provided
		'action' in the	JSON Request Body is not avaiable in the system.
		"""

		return APIResponse(
			status_code	=	406		# not acceptable
			, success	=	False
			, errors	=	[
				"API Request body for the given endpoint does not found!"
			]
		).get_response()


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

		fig.set_size_inches(10, 8)

		buffer = io.BytesIO()
		fig.savefig(buffer, format='png')
		buffer.seek(0)

		return buffer


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

		fig.set_size_inches(10, 8)

		buffer = io.BytesIO()
		fig.savefig(buffer, format='png')
		buffer.seek(0)

		return buffer


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

		fig.set_size_inches(10, 8)

		buffer = io.BytesIO()
		fig.savefig(buffer, format='png')
		buffer.seek(0)

		return buffer


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

		fig.set_size_inches(10, 8)

		buffer = io.BytesIO()
		fig.savefig(buffer, format='png')
		buffer.seek(0)

		return buffer


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

		fig.set_size_inches(10, 8)

		buffer = io.BytesIO()
		fig.savefig(buffer, format='png')
		buffer.seek(0)

		return buffer


	decorators = [
		role_restriction(app.config["RESOURCE_RESTRICTION_FOR_BOOK_OPERATION"])
		, jwt_required(optional = app.config["TESTING"])
	]
	def get(self):
		"""
		To process GET Method
		"""

		if self.request_action == "get_dashboard_graphs":
			return self.get_all_graphs()

		return self.__invalidActionError()

	def get_all_graphs(self):
		image_buff = dict()

		to_dos = [
			{
				"name": "category_names_vs_book_count.png"
				, "query": """
					SELECT DISTINCT(c.name) AS name, COUNT(r.book_id) AS count
						FROM category c, rel_books_category r
					WHERE r.category_id = c.category_id
						GROUP BY r.category_id;
				"""
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
						GROUP BY r.genre_id;
				"""
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
						GROUP BY r.lang_id;
				"""
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
					SELECT gender, count(gender) AS count
						FROM users
					WHERE role = 2
						GROUP BY gender;
				"""
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
						GROUP BY p.name;
				"""
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
						GROUP BY a.name;
				"""
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
						GROUP BY strftime("%d-%m-%Y", br.current_timestamp);
				"""
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
					GROUP BY date(b.current_timestamp)
						ORDER BY date(b.current_timestamp) ASC;
				"""
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
					GROUP BY strftime("%m-%Y", bp.current_timestamp);
				"""
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
						GROUP BY bh.book_id
					ORDER BY count DESC
						LIMIT 5;
				"""
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
				).read())
			elif to_do["graph_type"] == "pie":
				image_buff[to_do["name"]] = str(self._get_pie_graph(
					data			=	tmp_dict
					, graph_title	=	to_do["titles"][0]
				).read())
			elif to_do["graph_type"] == "stem":
				image_buff[to_do["name"]] = str(self._get_stem_graph(
					data			=	tmp_dict
					, graph_title	=	to_do["titles"][0]
					, x_title		=	to_do["titles"][1]
					, y_title		=	to_do["titles"][2]
				).read())
			elif to_do["graph_type"] == "plot":
				image_buff[to_do["name"]] = str(self._get_plot_graph(
					data			=	tmp_dict
					, graph_title	=	to_do["titles"][0]
					, x_title		=	to_do["titles"][1]
					, y_title		=	to_do["titles"][2]
				).read())
			elif to_do["graph_type"] == "custom-plot-01":
				image_buff[to_do["name"]] = str(self._get_custom_plot_graph(
					data			=	tmp_dict
					, graph_title	=	to_do["titles"][0]
					, y_title		=	to_do["titles"][2]
				).read())

		return APIResponse(
			status_code	=	300
			, data		=	image_buff
		).get_response()
