from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Sample Tailoring Studio"

@app.route("/services")
def services():
    return "Services"

if __name__ == "__main__":
    app.run(debug=True)
