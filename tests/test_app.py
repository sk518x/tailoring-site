from pathlib import Path

from app import app

import pytest
import database
from pathlib import Path


@pytest.fixture(autouse=True)
def temp_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")

@pytest.fixture(autouse=True)
def test_admin_password(monkeypatch):
    import settings
    monkeypatch.setattr(settings, "ADMIN_PASSWORD", "test-password")

@pytest.fixture(autouse=True)
def clear_login_attempts():
    import app as app_module
    if hasattr(app_module, "FAILED_LOGINS"):
        app_module.FAILED_LOGINS.clear()

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

def test_contact_page_shows_details():
    client = app.test_client()
    response = client.get("/contact")
    assert response.status_code == 200
    assert b"Contact" in response.data
    assert b"123 Sample Street" in response.data
    assert b"Mon to Fri" in response.data

def test_navigation_links_to_contact():
    client = app.test_client()
    response = client.get("/")
    assert b'href="/contact"' in response.data

def test_enquiry_page_shows_form():
    client = app.test_client()
    response = client.get("/enquire")
    assert response.status_code == 200
    assert b"<form" in response.data
    assert b'name="name"' in response.data
    assert b'name="phone"' in response.data
    assert b'name="message"' in response.data

def test_enquiry_submission_shows_thank_you():
    client = app.test_client()
    response = client.post("/enquire", data={
        "name": "Test Person",
        "phone": "0710000000",
        "message": "I need a school uniform",
    })
    assert response.status_code == 200
    assert b"Thank you" in response.data

def test_enquiry_without_name_is_rejected():
    client = app.test_client()
    response = client.post("/enquire", data={
        "name": "",
        "phone": "0710000000",
        "message": "Hello",
    })
    assert b"Please enter your name" in response.data

def test_save_and_get_enquiry():
        database.save_enquiry("Test Person", "0710000000", "School uniform", "status")
        enquiries = database.get_enquiries()
        assert len(enquiries) == 1
        assert enquiries[0]["name"] == "Test Person"
        assert enquiries[0]["source"] == "status"


def test_newest_enquiry_comes_first():
    database.save_enquiry("First Person", "0710000001", "Hello")
    database.save_enquiry("Second Person", "0710000002", "Hello again")
    enquiries = database.get_enquiries()
    assert enquiries[0]["name"] == "Second Person"


def test_submitting_form_saves_enquiry():
    client = app.test_client()
    client.post("/enquire", data={
        "name": "Form Person",
        "phone": "0710000003",
        "message": "A dress please",
    })
    enquiries = database.get_enquiries()
    assert len(enquiries) == 1
    assert enquiries[0]["phone"] == "0710000003"


def test_rejected_enquiry_is_not_saved():
    client = app.test_client()
    client.post("/enquire", data={"name": "", "phone": "0710000004", "message": "Hi"})
    assert database.get_enquiries() == []

def test_admin_requires_login():
    client = app.test_client()
    response = client.get("/admin")
    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_wrong_password_is_rejected():
    client = app.test_client()
    response = client.post("/admin/login", data={"password": "wrong"})
    assert b"Incorrect password" in response.data
    assert client.get("/admin").status_code == 302


def test_correct_password_shows_enquiries():
    database.save_enquiry("Listed Person", "0710000009", "A skirt", "status")
    client = app.test_client()
    client.post("/admin/login", data={"password": "test-password"})
    response = client.get("/admin")
    assert response.status_code == 200
    assert b"Listed Person" in response.data
    assert b"0710000009" in response.data

def test_source_tag_is_saved_with_enquiry():
    client = app.test_client()
    client.get("/?src=status")
    client.post("/enquire", data={
        "name": "Source Person",
        "phone": "0710000010",
        "message": "A dress",
    })
    enquiries = database.get_enquiries()
    assert enquiries[0]["source"] == "status"


def test_source_tag_survives_browsing_other_pages():
    client = app.test_client()
    client.get("/gallery?src=flyer")
    client.get("/services")
    client.post("/enquire", data={
        "name": "Browser Person",
        "phone": "0710000011",
        "message": "A hem",
    })
    assert database.get_enquiries()[0]["source"] == "flyer"


def test_enquiry_without_source_has_empty_source():
    client = app.test_client()
    client.post("/enquire", data={
        "name": "Direct Person",
        "phone": "0710000012",
        "message": "A skirt",
    })
    assert database.get_enquiries()[0]["source"] == ""


def test_source_tag_is_cleaned_up():
    client = app.test_client()
    client.get("/?src=<script>alert(1)</script>")
    client.post("/enquire", data={
        "name": "Odd Person",
        "phone": "0710000013",
        "message": "Hi",
    })
    source = database.get_enquiries()[0]["source"]
    assert "<" not in source
    assert len(source) <= 20

def test_logout_ends_admin_session():
    client = app.test_client()
    client.post("/admin/login", data={"password": "test-password"})
    assert client.get("/admin").status_code == 200
    client.post("/admin/logout")
    assert client.get("/admin").status_code == 302

def test_pages_link_the_stylesheet():
    client = app.test_client()
    response = client.get("/")
    assert b"/static/style.css" in response.data
    assert client.get("/static/style.css").status_code == 200

def test_qr_code_is_a_png_image():
    client = app.test_client()
    response = client.get("/qr.png")
    assert response.status_code == 200
    assert response.content_type == "image/png"
    assert response.data.startswith(b"\x89PNG")


def test_qr_code_does_not_change_the_source_tag():
    client = app.test_client()
    client.get("/qr.png")
    client.post("/enquire", data={
        "name": "Scan Person",
        "phone": "0710000014",
        "message": "A dress",
    })
    assert database.get_enquiries()[0]["source"] == ""

def test_enquiry_form_has_privacy_note():
    client = app.test_client()
    response = client.get("/enquire")
    assert b"/privacy" in response.data


def test_privacy_page_loads():
    client = app.test_client()
    response = client.get("/privacy")
    assert response.status_code == 200
    assert b"Privacy" in response.data
    assert b"phone number" in response.data

def test_whatsapp_chat_button_only_on_chosen_pages():
    client = app.test_client()
    for path in ["/services/dresses", "/enquire", "/privacy"]:
        response = client.get(path)
        assert b"Chat on WhatsApp" not in response.data


def test_footer_shows_opening_hours_on_every_page():
    client = app.test_client()
    for path in ["/", "/services/dresses", "/privacy"]:
        response = client.get(path)
        assert b"Mon to Fri" in response.data

def test_pages_load_heading_font():
    client = app.test_client()
    response = client.get("/")
    assert b"fonts.googleapis.com" in response.data


def test_home_page_has_hero_section():
    client = app.test_client()
    response = client.get("/")
    assert b"hero" in response.data
    assert b"Chat on WhatsApp" in response.data

def test_inner_pages_have_no_banner():
    client = app.test_client()
    for path in ["/services", "/services/dresses", "/contact", "/enquire", "/privacy"]:
        response = client.get(path)
        assert b"page-banner" not in response.data

def test_services_page_links_to_each_service():
    client = app.test_client()
    response = client.get("/services")
    assert b'href="/services/dresses"' in response.data
    assert b'href="/services/uniforms"' in response.data
    assert b'href="/services/alterations"' in response.data


def test_service_page_shows_info_and_items():
    client = app.test_client()
    response = client.get("/services/uniforms")
    assert response.status_code == 200
    assert b"Uniforms" in response.data
    assert b"Church uniform" in response.data
    assert b"Church%20uniform" in response.data

def test_unknown_service_is_not_found():
    client = app.test_client()
    assert client.get("/services/nonsense").status_code == 404


def test_old_gallery_link_goes_to_services():
    client = app.test_client()
    response = client.get("/gallery")
    assert response.status_code == 301
    assert response.headers["Location"].endswith("/services")


def test_menu_no_longer_has_gallery():
    client = app.test_client()
    response = client.get("/")
    assert b'href="/gallery"' not in response.data

def test_stylesheet_has_page_background():
    client = app.test_client()
    css = client.get("/static/style.css").data
    assert b"page-background" in css

def test_services_page_uses_photo_cards_with_pill_labels():
    client = app.test_client()
    response = client.get("/services")
    assert b"photo-card" in response.data
    assert b"pill" in response.data
    assert b"Custom outfits" in response.data

def test_home_hero_has_headline_underline_and_button():
    client = app.test_client()
    response = client.get("/")
    assert b"hero-underline" in response.data
    assert b"View our services" in response.data
    assert b"Chat on WhatsApp" in response.data

def test_home_page_has_feature_row():
    client = app.test_client()
    response = client.get("/")
    assert b"feature-row" in response.data
    assert b"Made to measure" in response.data
    assert b"Quick alterations" in response.data
    import settings
    assert f"Local in {settings.CITY}".encode() in response.data

def test_enquiry_form_is_in_a_glass_card():
    client = app.test_client()
    response = client.get("/enquire")
    assert b"glass-card" in response.data

def test_debug_is_off_by_default():
    import settings
    assert settings.DEBUG is False


def test_health_page_says_ok():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert b"ok" in response.data

def test_real_photos_stay_out_of_git():
    gitignore = (Path(__file__).parent.parent / ".gitignore").read_text()
    assert "local_settings.py" in gitignore
    assert "static/photos/" in gitignore

def test_service_images_are_paths_inside_static():
    import settings
    for service in settings.SERVICES:
        assert service["image"].startswith(("images/", "photos/"))
        for item in service["items"]:
            assert item["image"].startswith(("images/", "photos/"))

def test_missing_local_settings_falls_back_to_placeholders(monkeypatch):
    import importlib
    import sys
    import settings
    monkeypatch.setenv("USE_LOCAL_SETTINGS", "1")
    monkeypatch.setitem(sys.modules, "local_settings", None)
    try:
        importlib.reload(settings)
        for service in settings.SERVICES:
            assert service["image"].startswith("images/")
    finally:
        monkeypatch.delenv("USE_LOCAL_SETTINGS")
        importlib.reload(settings)

def test_session_cookie_is_hardened():
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["SESSION_COOKIE_SECURE"] is True

def test_logout_link_does_nothing_on_get():
    client = app.test_client()
    client.post("/admin/login", data={"password": "test-password"})
    assert client.get("/admin/logout").status_code == 405
    assert client.get("/admin").status_code == 200

def test_enquiry_form_has_hidden_trap_field():
    client = app.test_client()
    response = client.get("/enquire")
    assert b'name="website"' in response.data


def test_filled_trap_field_is_not_saved():
    client = app.test_client()
    response = client.post("/enquire", data={
        "name": "Spam Bot",
        "phone": "0710000099",
        "message": "Buy cheap stuff",
        "website": "http://spam.example",
    })
    assert response.status_code == 200
    assert b"Thank you" in response.data
    assert database.get_enquiries() == []

def test_repeated_wrong_passwords_lock_the_login():
    client = app.test_client()
    for _ in range(5):
        client.post("/admin/login", data={"password": "wrong"})
    response = client.post("/admin/login", data={"password": "wrong"})
    assert response.status_code == 429


def test_locked_login_rejects_the_correct_password():
    client = app.test_client()
    for _ in range(5):
        client.post("/admin/login", data={"password": "wrong"})
    response = client.post("/admin/login", data={"password": "test-password"})
    assert response.status_code == 429
    assert client.get("/admin").status_code == 302

def test_successful_login_resets_the_counter():
    client = app.test_client()
    for _ in range(4):
        client.post("/admin/login", data={"password": "wrong"})
    client.post("/admin/login", data={"password": "test-password"})
    assert client.get("/admin").status_code == 200
    for _ in range(4):
        client.post("/admin/login", data={"password": "wrong"})
    response = client.post("/admin/login", data={"password": "test-password"})
    assert response.status_code == 302

def test_lockout_expires():
    import app as app_module
    client = app.test_client()
    for _ in range(5):
        client.post("/admin/login", data={"password": "wrong"})
    assert client.post("/admin/login", data={"password": "test-password"}).status_code == 429
    app_module.WINDOW_SECONDS = 0
    try:
        response = client.post("/admin/login", data={"password": "test-password"})
        assert response.status_code == 302
    finally:
        app_module.WINDOW_SECONDS = 15 * 60