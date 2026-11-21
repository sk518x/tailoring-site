import os

BUSINESS_NAME = os.environ.get("BUSINESS_NAME", "Sample Tailoring Studio")
WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "27000000000")
WHATSAPP_MESSAGE = "Hi, I'd like to enquire"
ADDRESS = os.environ.get("ADDRESS", "123 Sample Street, Sample City")
OPENING_HOURS = os.environ.get("OPENING_HOURS", "Mon to Fri, 8:00 to 17:00")
PHONE = os.environ.get("PHONE", "018 000 0000")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")

SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:5000")

SERVICES = [
    {
        "slug": "dresses",
        "title": "Custom outfits",
        "summary": "Made to your measurements and your design.",
        "info": "Bring a picture or an idea. We take measurements, agree on fabric, and fit you before finishing.",
        "image": "images/dress.png",
        "items": [
            {"title": "Traditional dress", "image": "images/dress.png"},
        ],
    },

    {
        "slug": "uniforms",
        "title": "Uniforms",
        "summary": "Durable uniforms, sewn to last.",
        "info": "We sew to your group's specifications. Bring your school, church or work requirements and we will match them.",
        "image": "images/uniform.png",
        "items": [
            {"title": "Church uniform", "image": "images/uniform.png"},
        ],
    },
    {
        "slug": "alterations",
        "title": "Alterations",
        "summary": "Hems, tapering, resizing and repairs.",
        "info": "Hems, zips, taking in or letting out. Most small jobs are ready within a few days.",
        "image": "images/hem.png",
        "items": [
            {"title": "Trouser hem", "image": "images/hem.png"},
        ],
    },
]

CITY = os.environ.get("CITY", "Sample City")
FEATURES = [
    {"icon": "📏", "title": "Made to measure", "text": "Fitted to you, not off the rack."},
    {"icon": "🧵", "title": "Quick alterations", "text": "Most small jobs ready in days."},
    {"icon": "📍", "title": f"Local in {CITY}", "text": "For more info, let's chat on WhatsApp."},
]

DEBUG = os.environ.get("DEBUG", "") == "1"

if os.environ.get("USE_LOCAL_SETTINGS") == "1":
    try:
        from local_settings import SERVICES
    except ModuleNotFoundError:
        import logging
        logging.getLogger(__name__).warning(
            "local_settings.py not found, using placeholder SERVICES"
        )
if os.environ.get("USE_LOCAL_SETTINGS") == "1":
    try:
        from local_settings import SERVICES
    except ModuleNotFoundError:
        import logging
        logging.getLogger(__name__).warning(
            "local_settings.py not found, using placeholder SERVICES"
        )