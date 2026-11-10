from flask import Flask, render_template, request, redirect 
import calendar
from database_connection import DatabaseConnection
#User imports
from lib.user import User
from lib.user_repository import UserRepository

app = Flask(__name__)

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

# To view a form to create a new space.
@app.route('/spaces/new', methods=['GET'])
def get_create_space_form():
    return render_template("create_new_space.html")

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
