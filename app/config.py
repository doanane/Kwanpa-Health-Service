import os
from dotenv import load_dotenv

load_dotenv()

# Simple configuration with direct attribute access
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:S%400570263170s@localhost:5432/kwanpa_db")
SECRET_KEY = os.getenv("SECRET_KEY", "_XjLINqUxdiTa56Q__UHngKx4Uat3kXCpnRfIoLwuCI")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))