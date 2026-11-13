import psycopg
from lib.request import Request
from flask import Flask, session, flash

class RequestRepository:
    def __init__(self, connection):
        self._connection = connection

    #moved the filter to the sql
    #each approved booking is put into request.dates
    def find_unavailable_dates_by_space_id(self, space_id):
        rows = self._connection.execute(
            'SELECT * FROM requests WHERE space_id = %s AND approved = TRUE ORDER BY start_date' , [space_id])
        unavailable_dates = []
        for row in rows:
            request = Request(
                row["space_id"],
                row["user_id"],
                row["approved"],
                row["start_date"],
                row["end_date"],
                row["host_id"],
                row["id"],
                row["paid"],
                row["stripe_session_id"]
            )
            unavailable_dates.extend(request.dates())
        return unavailable_dates

    #function to see if there is overlap in the requested dates - requested and booked/unavailable. 
    def has_overlap(self, space_id, start_date, end_date):
        rows = self._connection.execute(
            'SELECT id FROM requests WHERE space_id = %s AND approved = True '
            'AND start_date <= %s AND end_date >= %s',
            [space_id, end_date, start_date])
        return len(rows) > 0 #only returns true if there is overlap - otherwise False

    # Save a new booking request for one or more nights
    def create(self, booking_request):
        rows = self._connection.execute(
            'INSERT INTO requests (space_id, user_id, approved, start_date, end_date, host_id) '
            'VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
            [booking_request.space_id, booking_request.user_id, booking_request.approved,
            booking_request.start_date, booking_request.end_date, booking_request.host_id])
        booking_request.id = rows[0]["id"]
        return booking_request

    def approve_request(self, request_id):
        # Approves a request only if none of its nights are already booked.
        # Returns True if it was approved, False if it clashes with an approved booking.
        found = self.find_request_by_id(request_id)
        if not found:
            return False
        booking_request = found

        # 1. Recheck availability on the server, right before approving
        if self.has_overlap(booking_request.space_id, booking_request.start_date, booking_request.end_date):
            return False

        # 2. The no_double_booking rule in the database is the final safety net:
        #    if two approvals happen at the same moment, only one can succeed.
        try:
            self._connection.execute(
                "UPDATE requests SET approved = True WHERE id = %s;", [request_id]
            )
        except psycopg.errors.ExclusionViolation:
            self._connection.connection.rollback()
            return False
        return True

    def check_ownership(self, request_id):
        found = self.find_request_by_id(request_id)
        if not found:
            return False
        booking_request = found
        # Only accept if the host id of the requested space is the same as the user id of the session
        if session["user_id"] != booking_request.host_id:
            return False
        return True

    def reject_request(self, request_id):
        self._connection.execute(
            "DELETE FROM requests WHERE id = %s;", [request_id]
        )

    def find_request_by_id(self, request_id):
        rows = self._connection.execute(
            "SELECT * FROM requests WHERE id = %s;", [request_id]
        )
        if not rows:
            return None
        row = rows[0]
        return Request(
            row["space_id"],
            row["user_id"],
            row["approved"],
            row["start_date"],
            row["end_date"],
            row["host_id"],
            row["id"],
            row["paid"],
            row["stripe_session_id"]
        )

    def find_by_user(self, user_id):
        rows = self._connection.execute(
            "SELECT * FROM requests WHERE host_id = %s ORDER BY id",
            [user_id]
        )
        return [
            Request(
                row["space_id"],
                row["user_id"],
                row["approved"],
                row["start_date"],
                row["end_date"],
                row["host_id"],
                row["id"],
                row["paid"],
                row["stripe_session_id"]
            )
            for row in rows
        ]

    def find_requests_made_by_user(self, user_id):
        rows = self._connection.execute(
            "SELECT * FROM requests WHERE user_id = %s ORDER BY id",
            [user_id]
        )
        return [
            Request(
                row["space_id"],
                row["user_id"],
                row["approved"],
                row["start_date"],
                row["end_date"],
                row["host_id"],
                row["id"],
                row["paid"],
                row["stripe_session_id"]
            )
            for row in rows
        ]

    #marks a request as paid and saves the stripe session id
    def mark_as_paid(self, request_id, stripe_session_id):
        self._connection.execute(
            "UPDATE requests SET paid = True, stripe_session_id = %s WHERE id = %s;",
            [stripe_session_id, request_id]
        )