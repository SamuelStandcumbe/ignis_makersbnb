import stripe
from app import app
from lib.request_repository import RequestRepository

BOB = 2  # not a host - made requests 1,2 and 3
ALICE = 1  # host

# helper functions/classes so that there isnt an actual stripe checkout session
def logged_in_client(user_id):
    app.config["TESTING"] = True
    client = app.test_client()
    with client.session_transaction() as session:
        session["user_id"] = user_id
    return client

class FakeCheckoutSession:
    url = "https://checkout.stripe.test/pay"

class FakePaidCheckout:
    payment_status = "paid"
    client_reference_id = "3"

class FakeUnpaidCheckout:
    payment_status = "unpaid"
    client_reference_id = "3"

#replaces stripes create call, instead returns a dict that records arguments
def patch_create(monkeypatch):
    captured = {}
    def fake_create(**kwargs):
        captured.update(kwargs)
        return FakeCheckoutSession()
    monkeypatch.setattr(stripe.checkout.Session, "create", fake_create)
    return captured

#tests for the session
#checkout session is created and in the correct amount
def test_checkout_session_is_created_with_the_correct_amount(db_connection, monkeypatch):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    captured = patch_create(monkeypatch)

    response = logged_in_client(BOB).post("/checkout/3")

    assert response.status_code == 303
    assert response.headers["Location"] == FakeCheckoutSession.url
    line_item = captured["line_items"][0]
    assert line_item["price_data"]["unit_amount"] == 28000   # 2 nights x £140, in pence since thats what stripe natively accepts, but i have already written a finction to convert it fr in action
    assert line_item["price_data"]["currency"] == "gbp"
    assert captured["mode"] == "payment"
    assert captured["client_reference_id"] == "3"
    assert "payment_method_types" not in captured   # Stripe rejects this now

# booking is marked paid after a successful payment
def test_booking_is_marked_paid_after_successful_payment(db_connection, monkeypatch):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    monkeypatch.setattr(stripe.checkout.Session, "retrieve",
                        lambda session_id: FakePaidCheckout())

    response = logged_in_client(BOB).get("/payment/success?session_id=cs_test_123")

    assert response.status_code == 302
    booking = RequestRepository(db_connection).find_request_by_id(3)
    assert booking.paid == True
    assert booking.stripe_session_id == "cs_test_123"

# booking stays unpaid after a failed or cancelled payment
def test_booking_stays_unpaid_after_cancelled_payment(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    client = logged_in_client(BOB)

    response = client.get("/payment/cancel", follow_redirects=True)

    assert response.status_code == 200
    assert "remains unpaid" in response.get_data(as_text=True)
    assert RequestRepository(db_connection).find_request_by_id(3).paid == False

#tests for the routes
# a payment Stripe reports as unpaid must not mark the booking paid
def test_unpaid_stripe_session_does_not_mark_booking_paid(db_connection, monkeypatch):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    monkeypatch.setattr(stripe.checkout.Session, "retrieve",
                        lambda session_id: FakeUnpaidCheckout())

    logged_in_client(BOB).get("/payment/success?session_id=cs_test_123")

    assert RequestRepository(db_connection).find_request_by_id(3).paid == False

# a user can't start a payment for someone else's request
def test_cannot_pay_for_someone_elses_request(db_connection, monkeypatch):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    captured = patch_create(monkeypatch)

    response = logged_in_client(ALICE).post("/checkout/3")   # request 3 is bob's

    assert response.status_code == 302
    assert response.headers["Location"] == "/requests"
    assert captured == {}   # Stripe was never called

# a request the host hasn't approved can't be paid for
def test_cannot_pay_for_an_unapproved_request(db_connection, monkeypatch):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    captured = patch_create(monkeypatch)

    response = logged_in_client(BOB).post("/checkout/1")   # request 1 is unapproved

    assert response.headers["Location"] == "/requests"
    assert captured == {}

# an already-paid booking can't be paid for again
def test_cannot_pay_twice_for_the_same_booking(db_connection, monkeypatch):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    RequestRepository(db_connection).mark_as_paid(3, "cs_test_123")
    captured = patch_create(monkeypatch)

    response = logged_in_client(BOB).post("/checkout/3")

    assert response.headers["Location"] == "/requests"
    assert captured == {}

# a logged-out visitor is sent to the login page
def test_logged_out_user_is_sent_to_login(db_connection):
    app.config["TESTING"] = True
    response = app.test_client().post("/checkout/3")
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"