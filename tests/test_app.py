from pathlib import Path

from app import app

import pytest
import database


@pytest.fixture(autouse=True)
def temp_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")

@pytest.fixture(autouse=True)
def test_admin_password(monkeypatch):
    import settings
    monkeypatch.setattr(settings, "ADMIN_PASSWORD", "test-password")

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

def test_gallery_groups_items_under_category_headings():
    client = app.test_client()
    response = client.get("/gallery")
    assert b"<h3>Uniforms</h3>" in response.data
    assert b"<h3>Dresses</h3>" in response.data
    assert b"<h3>Alterations</h3>" in response.data

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