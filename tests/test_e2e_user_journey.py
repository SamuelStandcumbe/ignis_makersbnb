import re
from datetime import date, timedelta
from playwright.sync_api import Page, expect
from werkzeug.security import generate_password_hash

NEXT_MONTH = date.today() + timedelta(days=30)
NEXT_MONTH_STR = NEXT_MONTH.strftime("%Y-%m-%d")
END_MONTH_STR = (NEXT_MONTH + timedelta(days=3)).strftime("%Y-%m-%d")


def test_complete_user_journey(page: Page, test_web_address, db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    
    # Overwrite passwords with a fresh hash for 'password123' and ensure Alice is a host
    pw_hash = generate_password_hash("password123")
    db_connection.execute(
        f"UPDATE users SET host = TRUE, password = '{pw_hash}' WHERE email = 'alice@example.com'"
    )
    db_connection.execute(
        f"UPDATE users SET password = '{pw_hash}' WHERE email = 'bob@example.com'"
    )
    
    base_url = test_web_address

    # 1. Bob logs in as guest
    page.goto(f"{base_url}/login")
    page.fill("#email", "bob@example.com")
    page.fill("#password", "password123")
    page.click("#submit")

    expect(page).to_have_url(re.compile(r".*/spaces$"))

    # 2. Guest selects Alice's space and submits booking request
    page.click('a.space-link:has-text("Fisherman\'s cottage by the harbour")')
    page.fill("#start-date", NEXT_MONTH_STR)
    page.fill("#end-date", END_MONTH_STR)
    page.click('button:has-text("Request to Book!")')

    expect(page).to_have_url(re.compile(r".*/requests$"))
    expect(page.locator("body")).to_contain_text("Pending")

    # 3. Host (Alice) logs in and accepts request
    page.click('button:has-text("Log Out")')
    page.goto(f"{base_url}/login")
    page.fill("#email", "alice@example.com")
    page.fill("#password", "password123")
    page.click("#submit")

    page.click('a:has-text("Requests")')
    request_card = (
        page.locator("article.card")
        .filter(has_text="Fisherman's cottage by the harbour")
        .filter(has_text=f"{NEXT_MONTH_STR} to {END_MONTH_STR}")
    )
    expect(request_card).to_be_visible()
    request_card.locator('button:has-text("Accept Request")').click()

    expect(request_card).to_contain_text("Approved")

    # 4. Bob logs back in, checks status, and verifies payment button
    page.click('button:has-text("Log Out")')
    page.goto(f"{base_url}/login")
    page.fill("#email", "bob@example.com")
    page.fill("#password", "password123")
    page.click("#submit")

    page.click('a:has-text("Requests")')
    guest_card = (
        page.locator("article.card")
        .filter(has_text="Fisherman's cottage by the harbour")
        .filter(has_text=f"{NEXT_MONTH_STR} to {END_MONTH_STR}")
    )
    expect(guest_card).to_contain_text("Approved, payment due")
    expect(guest_card.locator('button:has-text("Pay now")')).to_be_visible()