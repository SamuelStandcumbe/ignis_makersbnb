import os
import calendar
import psycopg
from flask import Flask, render_template, request, redirect, session
from database_connection import get_flask_database_connection
from lib.space import Space
from lib.space_repository import SpaceRepository

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")


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


# To view a form to create a new space.
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


if __name__ == '__main__':
    app.run(debug=True, port=5001)