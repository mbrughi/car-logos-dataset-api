# 🚗 Car Logos API

**Car Logos API** is a **FastAPI + MySQL + Redis** application that provides car manufacturer logos and related information (brand, country, file variants) via secure, rate-limited REST APIs.

The project originates as a fork of [car-logos-dataset](https://github.com/filippofilip95/car-logos-dataset) by @filippofilip95 and has been extended into a full-fledged API service suitable for use in external software integrations, for non commercial use.

---

## ✨ Key Features

- ✅ JSON endpoints for brands and logos (`/v1/brands`, `/v1/logos`)
- 🔐 Authentication via **API Key**
- 📈 Request rate limiting and logging powered by **Redis**
- ⚡ Browser/CDN caching with `Cache-Control` headers
- 🧠 Automatic dataset import from the original fork
- 🧩 Easy integration 
- 🧰 Production-ready (Gunicorn/Uvicorn + Nginx reverse proxy)

---

## 🧱 Tech Stack

| Component | Description |
|------------|-------------|
| **Python 3.10+** | Primary language |
| **FastAPI** | Web framework |
| **MySQL 8** | Persistent database |
| **SQLAlchemy + Alembic** | ORM and migrations |
| **Redis** | Rate-limit, logging, and runtime cache |
| **Uvicorn** | ASGI server |
| **Nginx** | Reverse proxy and static file handling |

---

## 📁 Project Structure

```
app/
 ├── main.py
 ├── config.py
 ├── db.py
 ├── models/
 │    ├── brand.py
 │    └── api_key.py
 ├── routers/
 │    ├── brands.py
 │    ├── logos.py
 │    └── admin.py
 ├── services/
 │    ├── rate_limit.py
 │    └── storage.py
 ├── middleware/
 │    ├── request_log.py
 │    └── ratelimit_headers.py
 └── security/
      ├── auth.py
      └── admin_only.py

migrations/
scripts/
 └── create_api_key.py
logos/
 ├── optimized/
 ├── thumb/
 ├── original/
 └── local-logos/
```

---

## ⚙️ Installation

```bash
# clone the fork
git clone https://github.com/<your-username>/car-logos-api.git
cd car-logos-api

# create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# configure environment
cp .env.example .env
nano .env

# create database tables
alembic upgrade head

# import dataset
python scripts/import_dataset.py --json-path logos/data.json

# run the server (for development)
uvicorn app.main:app --reload --port 9090
```

---

## 🔑 Generate an API Key

```bash
python scripts/create_api_key.py wordpress-plugin
```

---


## 📜 License
**Usage License**: The Car Logos API is provided for personal, educational, and non-commercial use only. Commercial use, resale, or redistribution of the API or its data is strictly prohibited.
All logo images are the property of their respective owners and are subject to their own licensing terms.
Based on [car-logos-dataset](https://github.com/filippofilip95/car-logos-dataset) (MIT License).  
All modifications and API code © 2025 [Marco Brughi].
