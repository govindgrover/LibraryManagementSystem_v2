# ============================= [ START IMPORTS ] =============================

# flask functionalities
from flask import current_app as app
from flask import session

# to handle requests
from flask import render_template, redirect, url_for

# to restrict with a login
from ..functions.functions import login_required

# ============================== [ END IMPORTS ] ==============================


# ============================== [ START ROUTES ] =============================

@app.route("/", methods = ["GET"])
def page_index():
	return render_template("index.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route("/access-denied", methods = ["GET"])
def page_access_denied():
	if "is_access_denied" in session and session["is_access_denied"]:
		return render_template("access_denied.html")
	
	return redirect("/home")

@app.route("/404", methods = ["GET"])
def page_404():
	return render_template("404.html")


# =============================== [ END ROUTES ] ==============================
