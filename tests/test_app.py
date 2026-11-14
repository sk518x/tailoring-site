from app import app

def test_home_page_shows_business_name():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Sample Tailoring Studio" in response.data