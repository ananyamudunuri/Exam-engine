# filepath: /c:/Users/infor/Downloads/examengine/config.py
import os

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "exam")  # Optional fallback
DB_NAME = os.getenv("DB_NAME", "examdb")
DB_HOST = os.getenv("DB_HOST", "/cloudsql/exam-engine-462520:us-central1:examengine-postgres")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@/{DB_NAME}?host={DB_HOST}"
