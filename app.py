import os
import calendar
import psycopg
from flask import Flask, render_template, request, redirect, session
from database_connection import DatabaseConnection, get_flask_database_connection
from lib.space import Space
from lib.space_repository import SpaceRepository
#User imports
from lib.user import User
from lib.user_repository import UserRepository

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")


def get_connection():
    connection = DatabaseConnection(test_mode=app.config.get("TESTING", False))
    connection.connect()
    return connection

#  View landing/ signup page
@app.route('/', methods=['GET'])
def get_sign_up():
    return render_template("sign_up_page.html")

# View Form for Login
@app.route('/login', methods=['GET'])
def get_log_in():
    return render_template("log_in_page.html")

# To view a list of all available spaces
@app.route('/spaces', methods=['GET'])
def get_available_spaces():
    return render_template("available_spaces.html")

# To view a form to create a new space (logged-in users only)
@app.route('/spaces/new', methods=['GET'])
def get_create_space_form():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("create_new_space.html", errors=[], form={})

# Save a new space for the logged-in user
@app.route('/spaces', methods=['POST'])
def create_space():
    if "user_id" not in session:
        return redirect("/login")
    space = Space(
        None,
        request.form.get("space_name", "").strip(),
        request.form.get("location", "").strip(),
        request.form.get("description", "").strip(),
        request.form.get("price", "").strip(),
        session["user_id"],
    )

    if not space.is_valid():
        return render_template("create_new_space.html",
                            errors=space.generate_errors(), form=request.form), 400

    try:
        SpaceRepository(get_flask_database_connection(app)).create(space)
    except psycopg.Error:
        return render_template("create_new_space.html",
                            errors=["Sorry, we could not save your space. Please try again."],
                            form=request.form), 500

    return redirect("/spaces")

# To view available dates for a specific property
# Scope to turn this into a .find with space ID in future
# EG : /spaces/<space_id>
@app.route('/make_booking')
def show_calendar():
    year = 2026
    month = 11

    weeks = calendar.monthcalendar(year, month)

    available_dates = [10, 12, 17, 19, 24, 26]

    return render_template(
        'make_booking.html',
        weeks=weeks,
        available_dates=available_dates,
        month_name=calendar.month_name[month],
        year=year
    )

# To view requests recieved by a space owner
# Scope to turn this into a .find with user ID when logged in.
@app.route('/requests', methods=['GET'])
def get_requests():
    return render_template("requests.html")

# To view requests you as a user have made on spaces for a specific date
# Scope to work specifically with log in.
@app.route('/view_requests', methods=['GET'])
def get_requests_made():
    return render_template("view_requests.html")

#receive signup form and save new user - then redirects to /login
@app.route('/users', methods=['POST'])
def post_users():
    repo = UserRepository(get_connection())
    user = User(
        request.form["username"],
        request.form["email"],
        request.form["password"],
        "is_host" in request.form,
    )
    repo.create(user)
    return redirect("/login")

if __name__ == '__main__':
    app.run(debug=True, port=5001)