from app import app

def test_home_page_shows_business_name():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Sample Tailoring Studio" in response.data


def test_services_page_loads():
    client = app.test_client()
    response = client.get("/services")
    assert response.status_code == 200
    assert b"Services" in response.data

def test_home_page_is_html_with_title():
    client = app.test_client()
    response = client.get("/")
    assert b"<title>" in response.data
    assert b"Sample Tailoring Studio" in response.data
    assert b"Chat on WhatsApp" in response.data

def test_services_page_uses_shared_layout():
    client = app.test_client()
    response = client.get("/services")
    assert b"<title>" in response.data
    assert b"Sample Tailoring Studio" in response.data
    assert b"Chat on WhatsApp" in response.data

def test_whatsapp_link_uses_settings():
    from settings import WHATSAPP_NUMBER
    client = app.test_client()
    response = client.get("/")
    assert WHATSAPP_NUMBER.encode() in response.data

def test_whatsapp_number_change_shows_on_page():
    import settings
    original = settings.WHATSAPP_NUMBER
    settings.WHATSAPP_NUMBER = "27111111111"
    try:
        client = app.test_client()
        response = client.get("/")
        assert b"27111111111" in response.data
    finally:
        settings.WHATSAPP_NUMBER = original

def test_gallery_page_lists_items():
    client = app.test_client()
    response = client.get("/gallery")
    assert response.status_code == 200
    assert b"Gallery" in response.data
    assert b"uniform" in response.data

def test_gallery_items_have_enquire_buttons():
    client = app.test_client()
    response = client.get("/gallery")
    assert b"Enquire on WhatsApp" in response.data
    assert b"uniform" in response.data

def test_gallery_shows_images():
    client = app.test_client()
    response = client.get("/gallery")
    assert b"/static/images/uniform.png" in response.data