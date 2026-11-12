import os
import calendar
import psycopg
from datetime import date, timedelta
from flask import Flask, render_template, request, redirect, session, flash
from database_connection import DatabaseConnection, get_flask_database_connection
from lib.space import Space
from lib.space_repository import SpaceRepository
from lib.request_repository import RequestRepository
from lib.user import User
from lib.user_repository import UserRepository

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")


def get_connection():
    connection = DatabaseConnection(test_mode=app.config.get("TESTING", False))
    connection.connect()
    return connection

# View landing / signup page
@app.route('/', methods=['GET'])
def get_sign_up():
    return render_template("sign_up_page.html")

# ------------------------------------------------
# SEARCH ROUTES
# ------------------------------------------------

# To post the search terms
@app.route('/', methods=['POST'])
def create_search():
    search_term = request.form["search"]
    return redirect(f"/search/{search_term}")

# collects search term, looks up in db, renders results here
@app.route('/search/<search_term>', methods=['GET'])
def get_search_results(search_term):
    connection = DatabaseConnection()
    connection.connect()
    repository = SpaceRepository(connection)
    related_spaces = repository.find_by_search(search_term)
    return render_template("search_results.html", related_spaces = related_spaces)

# -------------------------------------------------


# View form for login
@app.route('/login', methods=['GET'])
def get_log_in():
    if 'user_id' in session:
        return redirect('/spaces')
    
    return render_template("log_in_page.html")

@app.route('/sessions', methods=['POST'])
def create_sessions():
    connection = DatabaseConnection()
    connection.connect()
    user_repository = UserRepository(connection)

    email_address = request.form["email"]
    password = request.form["password"]

    user = user_repository.find_by_email_address(email_address)
    if user is not None  and user.password == password:
        session["user_id"] = user.id
        session["email"] = user.email
        return redirect("/spaces")
    else:
        flash("⚠️ Invalid Email Address or Password! ")
        return redirect("/login")

# View form to create a new space (logged-in users only)
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
        request.form.get("space_name", "").strip(),
        request.form.get("location", "").strip(),
        request.form.get("description", "").strip(),
        request.form.get("price", "").strip(),
        session["user_id"],
        None,
    )

    if not space.is_valid():
        return render_template(
            "create_new_space.html",
            errors=space.generate_errors(),
            form=request.form
        ), 400

    try:
        SpaceRepository(get_flask_database_connection(app)).create(space)
    except psycopg.Error:
        return render_template(
            "create_new_space.html",
            errors=["Sorry, we could not save your space. Please try again."],
            form=request.form
        ), 500

    return redirect("/spaces")


# View available dates for a specific property
@app.route('/make_request/<id>', methods=["GET"])
def get_booking_page(id):
    connection = get_flask_database_connection(app)

    space_repository = SpaceRepository(connection)
    space = space_repository.find_by_space_id(id)

    request_repository = RequestRepository(connection)
    unavailable_dates = request_repository.find_unavailable_dates_by_space_id(id)

    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    first_day = date(year, month, 1)

    previous_month = first_day - timedelta(days=1)
    next_month = first_day + timedelta(days=calendar.monthrange(year, month)[1])

    weeks = calendar.Calendar().monthdatescalendar(year, month)

    return render_template(
        'make_request.html',
        weeks=weeks,
        unavailable_dates=unavailable_dates,
        month_name=calendar.month_name[month],
        year=year,
        today=today,
        month=month,
        previous_month=previous_month,
        next_month=next_month,
        space_name=space.space_name,
        space_location=space.location,
        space_price=space.price,
        space_description=space.description
    )

# View booking requests sent and received by user 1
@app.route('/requests', methods=['GET'])
def get_requests():
    user_id = 1  # Temporary until login is implemented
    connection = get_flask_database_connection(app)

    request_repo = RequestRepository(connection)
    space_repo = SpaceRepository(connection)

    received_requests = request_repo.find_by_user(user_id)
    sent_requests = request_repo.find_requests_made_by_user(user_id)
    spaces = space_repo.all()
    spaces_by_id = {space.id: space for space in spaces}

    return render_template(
        "requests.html",
        received_requests=received_requests,
        sent_requests=sent_requests,
        spaces_by_id=spaces_by_id
    )

@app.route('/requests/<user_id>/<request_id>/reject', methods=['POST'])
def post_request_declined(user_id, request_id):
    repo = RequestRepository(get_connection())
    repo.reject_request(request_id)
    return redirect("/requests")


@app.route('/requests/<user_id>/<request_id>/approve', methods=['POST'])
def post_request_approved(user_id, request_id):
    repo = RequestRepository(get_connection())
    repo.approve_request(request_id)
    return redirect("/requests")

# To view a list of all available spaces
@app.route('/spaces', methods=['GET'])
def get_all_available_spaces():
    connection = DatabaseConnection()
    connection.connect()
    available_spaces_repository = SpaceRepository(connection)
    available_spaces = available_spaces_repository.all()
    return render_template("available_spaces.html", available_spaces = available_spaces)


# Receive signup form and save new user
@app.route('/users', methods=['POST'])
def post_users():
    repo = UserRepository(get_connection())
    user = User(
        request.form["full_name"],
        request.form["email"],
        request.form["password"],
        "is_host" in request.form,
    )
    repo.create(user)
    return redirect("/login")

@app.route('/logout', methods=['POST'])
def logging_out():
    session.clear()
    flash(" 🔒 You have been logged out. 👋")
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
