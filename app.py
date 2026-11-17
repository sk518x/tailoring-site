from flask import Flask, render_template, request, redirect, session, send_file
import settings
import database
import re
import io
import qrcode

app = Flask(__name__)

app.secret_key = settings.SECRET_KEY

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

def clean_source(value):
    return re.sub(r"[^a-zA-Z0-9_-]", "", value)[:20]


@app.before_request
def remember_source():
    source = request.args.get("src")
    if source:
        session["source"] = clean_source(source)

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
        database.save_enquiry(name, phone, message, session.get("source", ""))
        return render_template("thanks.html")
    return render_template("enquire.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if settings.ADMIN_PASSWORD and password == settings.ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect("/admin")
        return render_template("admin_login.html", error="Incorrect password")
    return render_template("admin_login.html")

@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return redirect("/admin/login")
    return render_template("admin.html", enquiries=database.get_enquiries())

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect("/admin/login")

@app.route("/qr.png")
def qr_code():
    image = qrcode.make(settings.SITE_URL + "/?src=qr")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
