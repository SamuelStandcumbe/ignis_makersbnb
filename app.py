from flask import Flask, render_template
import calendar
from database_connection import *
from lib.space_repository import *
from lib.space import*

app = Flask(__name__)

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

@app.route('/', methods=['GET'])
def get_all_available_spaces():
    connection = DatabaseConnection()
    connection.connect()
    available_spaces_repository = SpaceRepository()
    available_spaces = available_spaces_repository.all()
    return render_template("available_spaces.html", boavailable_spacesoks = available_spaces)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
