from lib.space_repository import SpaceRepository
from lib.request_repository import RequestRepository
from database_connection import DatabaseConnection
from flask import Flask, render_template, request
from datetime import date, timedelta
import calendar

app = Flask(__name__)
app.config["DATABASE_CONNECTION"] = None

@app.route('/make_request/<id>', methods=["GET"])
def get_booking_page(id):
    connection = app.config["DATABASE_CONNECTION"]
    if connection is None:
        connection = DatabaseConnection()
        connection.connect()
    print(connection._database_name())

    space_repository = SpaceRepository(connection)
    space = space_repository.find_by_space_id(id)

    request_repository = RequestRepository(connection)
    unavailable_dates = request_repository.find_unavailable_dates_by_space_id(id)

    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    first_day = date(year, month, 1)

    previous_month = first_day - timedelta(days=1)
    next_month = date(year, month, calendar.monthrange(year, month)[1]) + timedelta(days=1)

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


if __name__ == '__main__':
    app.run(debug=True, port=5001)
