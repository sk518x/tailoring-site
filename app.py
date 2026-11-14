from flask import Flask, render_template
import settings
app = Flask(__name__)

@app.context_processor
def inject_settings():
    return {
        "business_name": settings.BUSINESS_NAME,
        "whatsapp_number": settings.WHATSAPP_NUMBER,
        "whatsapp_message": settings.WHATSAPP_MESSAGE,
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

if __name__ == "__main__":
    app.run(debug=True)
