# ExamEngine

A FastAPI-based exam platform for multiple-choice tests (supports **multiple correct answers**).  
It exposes clean REST APIs, serves a minimal HTML UI, and returns detailed grading.  
Production runs on **Google Cloud Run** behind a **Google Cloud HTTPS Load Balancer** (static IP + managed SSL) with a **Cloud SQL (Postgres)** database restricted to backend access.

---

## ✨ Features

- Create questions with options (one or many correct)
- List questions & tests
- Submit answers → **score + per-question breakdown**
- OpenAPI docs at `/docs`
- Minimal UI from `templates/` (with assets in `static/`)

---

## 🧱 Tech Stack

- **FastAPI**, **SQLAlchemy**, **Pydantic**
- **PostgreSQL** (Cloud SQL) in prod; **SQLite** for local dev
- **Docker** → **Artifact Registry** → **Cloud Run**
- **HTTPS External Application Load Balancer** using **Serverless NEG**
- Optional: Cloud SQL **Python Connector** for secure DB connections

---

## 📁 Project Structure

examengine/
├── app.py # FastAPI app (routes, scoring)
├── config.py # DB config (SQLite dev / Cloud SQL prod)
├── requirements.txt
├── Dockerfile
├── templates/
│ ├── index.html
│ └── results.html
└── static/ # CSS/JS/assets


---

## 🗄️ Data Model

- `tests(id, name)`
- `questions(id, text, test_id → tests.id)`
- `options(id, text, is_correct, question_id → questions.id)`

**Scoring rule:** a question is correct **only if** the set of selected option IDs **exactly equals** the set of correct option IDs.

---
