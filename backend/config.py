import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///nbkpay.db")
    JWT_SECRET = os.getenv("JWT_SECRET", "change_this_jwt_secret")
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
    TWILIO_FROM = os.getenv("TWILIO_FROM")
    BLOCKCHAIN_ETH_URL = os.getenv("BLOCKCHAIN_ETH_URL")
    BLOCKCHAIN_TRON_URL = os.getenv("BLOCKCHAIN_TRON_URL")
    BLOCKCHAIN_BTC_URL = os.getenv("BLOCKCHAIN_BTC_URL")
    # Add more config as needed

config = Config()
