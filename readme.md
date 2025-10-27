# Snaply - Social Network API 🚀

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/) 
[![Django](https://img.shields.io/badge/Django-5.2%2B-green)](https://www.djangoproject.com/) 
[![DRF](https://img.shields.io/badge/DRF-3.15%2B-orange)](https://www.django-rest-framework.org/) 
[![PostgreSQL](https://img.shields.io/badge/DB-PostgreSQL-brightgreen)](https://www.postgresql.org/) 
[![MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A scalable RESTful API for social networking, powered by Django 5.2 and DRF. Features JWT auth, user profiles (bio editing), post CRUD, dynamic follows/likes/comments, and personalized feeds (followed + own posts). Production-ready with env configs and Neon/Render Postgres support.

## ✨ Features
- **Auth**: JWT login/register (auto-login on signup), token refresh.
- **Users**: CRUD, bio PATCH (username/email protected), follow toggle with status/counts.
- **Posts**: Full CRUD (owner-only edit/delete), toggle likes, per-post comments.
- **Feed**: Chronological posts from followed + own users.
- **Serialization**: Nested authors, dynamic counts (followers/likes).
- **Docs**: Auto Swagger/ReDoc.
- **Security**: Partial updates, CORS for local/prod.
- **Tests**: Unit coverage for serializers/views.

## 📋 Prerequisites
- Python 3.8+.
- Git.
- PostgreSQL for prod (Neon free tier).

## 🚀 Quick Start (Local)
1. Clone: `git clone https://github.com/Mauriciofnti/api_social_network.git && cd social-api`.
2. Virtual env: `python -m venv venv` (activate: `source venv/bin/activate` or `venv\Scripts\activate`).
3. Install: `pip install -r requirements.txt`.
4. Migrate: `python manage.py makemigrations && python manage.py migrate`.
5. Superuser: `python manage.py createsuperuser`.
6. Run: `python manage.py runserver`.
   - Admin: `http://127.0.0.1:8000/admin/`
   - API: `http://127.0.0.1:8000/api/`
   - Swagger: `http://127.0.0.1:8000/api/schema/swagger-ui/`

## ⚙️ Environment Setup
Create `.env` in root (gitignored).

**Local (.env)**:
```
SECRET_KEY=django-insecure-dev-key  # Generate: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

**Production (Render Dashboard)**:
- `SECRET_KEY`: Strong generated key.
- `DEBUG`: `False`.
- `ALLOWED_HOSTS`: `*.onrender.com`.
- `DATABASE_URL`: Neon/Render Postgres URL.
- `CORS_ALLOWED_ORIGINS`: Frontend domain.

`settings.py` auto-loads env vars.

## 📡 API Endpoints
| Method | Endpoint                     | Description            | Auth        |
| ------ | ---------------------------- | ---------------------- | ----------- |
| GET    | `/users/`                    | List all users         | No          |
| POST   | `/users/`                    | Create user            | No          |
| GET    | `/users/<id>/`               | Get user details       | No          |
| PATCH  | `/users/<id>/`               | Update bio (partial)   | Yes (owner) |
| GET    | `/users/me/`                 | Get current user info  | Yes         |
| POST   | `/users/<id>/follow/`        | Follow user            | Yes         |
| POST   | `/users/<id>/unfollow/`      | Unfollow user          | Yes         |
| POST   | `/users/<id>/toggle_follow/` | Toggle follow/unfollow | Yes         |
| GET    | `/users/<id>/is_following/`  | Check if following     | Yes         |
| POST   | `/posts/`                    | Create post            | Yes         |
| GET    | `/posts/?author=<id>`        | Get posts by user      | Yes         |
| GET    | `/posts/<id>/`               | Get post details       | Yes         |
| PATCH  | `/posts/<id>/`               | Edit post              | Yes (owner) |
| DELETE | `/posts/<id>/`               | Delete post            | Yes (owner) |
| POST   | `/posts/<id>/like/`          | Like/unlike post       | Yes         |
| POST   | `/posts/<id>/comments/`      | Add comment            | Yes         |
| GET    | `/posts/<id>/comments/`      | List comments          | Yes         |
| GET    | `/posts/feed/`               | Personalized feed      | Yes         |

## ☁️ Deployment

Local: python manage.py runserver.
Render:

Build: pip install -r requirements.txt && python manage.py migrate.
Start: python manage.py runserver 0.0.0.0:$PORT.
Env Vars: SECRET_KEY (strong), DEBUG=False, DATABASE_URL (Neon), ALLOWED_HOSTS=*.onrender.com, CORS_ALLOWED_ORIGINS=frontend-domain.


DB: SQLite local; Neon/Render Postgres prod (migrate on deploy).