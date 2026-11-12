import re

def test_all_images_have_non_empty_alt_text(client, db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    
    # Log in as a host so we can access all protected pages too
    client.post("/sessions", data={
        "email": "alice@example.com",
        "password": "password123",
    }, follow_redirects=True)

    pages = ["/", "/login", "/spaces", "/spaces/new", "/requests", "/make_request/1"]

    for route in pages:
        response = client.get(route, follow_redirects=True)
        html = response.data.decode("utf-8")
        
        img_tags = re.findall(r"<img\b[^>]*>", html, flags=re.IGNORECASE)
        for img in img_tags:
            match = re.search(r'\balt=["\']([^"\']+)["\']', img, flags=re.IGNORECASE)
            assert match is not None and match.group(1).strip() != "", (
                f"Image missing non-empty alt attribute on {route}: {img}"
            )

def test_all_form_inputs_have_labels(client, db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    
    # Log in so we can check forms on protected pages (/spaces/new and /make_request/1)
    client.post("/sessions", data={
        "email": "alice@example.com",
        "password": "password123",
    }, follow_redirects=True)

    form_pages = ["/", "/login", "/spaces/new", "/make_request/1"]

    for route in form_pages:
        response = client.get(route, follow_redirects=True)
        html = response.data.decode("utf-8")
        
        inputs = re.findall(r"<input\b[^>]*>", html, flags=re.IGNORECASE)
        for inp in inputs:
            # Skip hidden and submit inputs since they don't use <label>
            if re.search(r'\btype=["\'](hidden|submit)["\']', inp, flags=re.IGNORECASE):
                continue
                
            id_match = re.search(r'\bid=["\']([^"\']+)["\']', inp, flags=re.IGNORECASE)
            assert id_match is not None, f"Input missing id attribute on {route}: {inp}"
            
            input_id = id_match.group(1)
            has_label = re.search(rf'<label\b[^>]*\bfor=["\']{re.escape(input_id)}["\']', html, flags=re.IGNORECASE)
            assert has_label is not None, f"Input #{input_id} missing <label for='{input_id}'> on {route}"