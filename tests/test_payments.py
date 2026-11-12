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

#checkout session is created and in the correct amount
def test_checkout_session_is_created_with_the_correct_amount(db_connection, monkeypatch):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    captured = patch_create(monkeypatch)

    response = logged_in_client(BOB).post("/checkout/3")

    assert response.status_code == 303
    assert response.headers["Location"] == FakeCheckoutSession.url
    line_item = captured["line_items"][0]
    assert line_item["price_data"]["unit_amount"] == 42000   # 3 nights x £140, in pence since thats what stripe natively accepts, but i have already written a finction to convert it fr in action
    assert line_item["price_data"]["currency"] == "gbp"
    assert captured["mode"] == "payment"
    assert captured["client_reference_id"] == "3"
    assert "payment_method_types" not in captured   # Stripe rejects this now