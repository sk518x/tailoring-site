from flask import Flask, render_template, request
import settings
app = Flask(__name__)

@app.context_processor
def inject_settings():
    return {
        "business_name": settings.BUSINESS_NAME,
        "whatsapp_number": settings.WHATSAPP_NUMBER,
        "whatsapp_message": settings.WHATSAPP_MESSAGE,
        "address": settings.ADDRESS,
        "opening_hours": settings.OPENING_HOURS,
        "phone": settings.PHONE,
    }

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html", items=settings.GALLERY_ITEMS)

@app.route("/contact")
def contact():
    return render_template("contact.html")

def test_gallery_groups_items_under_category_headings():
    client = app.test_client()
    response = client.get("/gallery")
    assert b"<h3>Uniforms</h3>" in response.data
    assert b"<h3>Dresses</h3>" in response.data
    assert b"<h3>Alterations</h3>" in response.data

@app.route("/enquire", methods=["GET", "POST"])
def enquire():
    if request.method == "POST":
        name = request.form["name"].strip()
        phone = request.form["phone"].strip()
        message = request.form["message"].strip()
        if not name:
            return render_template("enquire.html", error="Please enter your name")
        return render_template("thanks.html")
    return render_template("enquire.html")

if __name__ == "__main__":
    app.run(debug=True)
