import os

from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv(
    "NOTIFICATION_WEBHOOK_URL"
)

GENERATOR_CAPACITY = float(
    os.getenv("GENERATOR_CAPACITY", 500)
)