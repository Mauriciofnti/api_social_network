# Snaply - Social Network API 🚀

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/) [![Django](https://img.shields.io/badge/Django-4.2%2B-green)](https://www.djangoproject.com/) [![DRF](https://img.shields.io/badge/DRF-3.15%2B-orange)](https://www.django-rest-framework.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A RESTful API for a social network, built with Django and Django REST Framework (DRF). Supports user registration/login, posts, follows, likes, comments, and personalized feed. Fully authenticated with JWT and documented with Swagger.

## Features
- **Secure Authentication**: JWT tokens for stateless sessions (login/register with token refresh).
- **User Management**: CRUD with partial updates (PATCH for bio only; username/email protected).
- **Post Interactions**: Create, edit, delete, like/unlike (toggle), comments.
- **Follow System**: Follow/unfollow with dynamic toggle and status check; counts for followers/following.
- **Personalized Feed**: Posts from followed users + own posts (always included).
- **Advanced Serialization**: Nested author data, dynamic counts (likes, followers).
- **Automatic Documentation**: Swagger UI and ReDoc for interactive testing.
- **Unit Tests**: Basic coverage for serializers and views.
- **CORS & Deployment Ready**: Config for local/Render/Neon DB.

## Prerequisites
- Python 3.8+.
- Git.

## Quick Installation
1. Clone the repository:
git clone https://github.com/Mauriciofnti/api_social_network.git
cd social-api
text2. Create and activate virtual environment:
python -m venv venv
Windows: venv\Scripts\activate
Linux/Mac: source venv/bin/activate
text3. Install dependencies:
pip install -r requirements.txt
text4. Apply migrations:
python manage.py makemigrations
python manage.py migrate
text5. Create superuser:
python manage.py createsuperuser
text6. Start the server:
python manage.py runserver
text- Admin: `http://127.0.0.1:8000/admin/`
- API: `http://127.0.0.1:8000/api/`

## API Usage
Base URL: `http://127.0.0.1:8000/api/`.

### Main Endpoints
| Method | Endpoint                  | Description                                      | Authentication |
|--------|---------------------------|--------------------------------------------------|---------------|
| GET    | `/users/`                | List users                                       | No            |
| POST   | `/users/`                | Create user (body: `{"username": "...", "email": "...", "password": "...", "bio": "..."}`) | No            |
| GET    | `/users/<id>/`           | User details (open read)                         | No            |
| PATCH  | `/users/<id>/`           | Partial update (body: `{"bio": "..."}`; username/email protected) | Yes (owner only) |
| GET    | `/users/me/`             | Current user details/update                      | Yes           |
| POST   | `/users/<id>/follow/`    | Follow user                                      | Yes           |
| POST   | `/users/<id>/unfollow/`  | Unfollow user                                    | Yes           |
| POST   | `/users/<id>/toggle_follow/` | Toggle follow/unfollow (dynamic button)          | Yes           |
| GET    | `/users/<id>/is_following/` | Check follow status (for button init)            | Yes           |
| POST   | `/posts/`                | Create post (body: `{"content": "..."}`)         | Yes           |
| GET    | `/posts/?author=<id>`    | List user's posts (query param)                  | Yes           |
| GET    | `/posts/<id>/`           | Post details                                     | Yes           |
| PATCH  | `/posts/<id>/`           | Edit post (body: `{"content": "..."}`; owner only) | Yes (owner only) |
| DELETE | `/posts/<id>/`           | Delete post (owner only)                         | Yes (owner only) |
| POST   | `/posts/<id>/like/`      | Like/unlike post (toggle)                        | Yes           |
| POST   | `/posts/<id>/comments/`  | Add comment (body: `{"content": "..."}`)         | Yes           |
| GET    | `/posts/<id>/comments/`  | List post comments                               | Yes           |
| GET    | `/posts/feed/`           | Personalized feed (followed + own posts)         | Yes           |

- **Authentication**: POST `/token/` with `{"username": "...", "password": "..."}` → `{access, refresh, user}`. Use `Authorization: Bearer <access>` for protected. Refresh with POST `/token/refresh/`.

## Testing
- **Postman**: Set `{{base_url}} = http://127.0.0.1:8000`. Save `{{access_token}}` from login response.
- **Swagger UI**: `/api/schema/swagger-ui/` (Authorize with JWT).
- **ReDoc**: `/api/schema/redoc/`.
- **Unit Tests**: `python manage.py test network`.

## Deployment
### Render
1. Push to GitHub.
2. New Web Service > Connect repo.
3. Build: `pip install -r requirements.txt && python manage.py migrate`.
4. Start: `python manage.py runserver 0.0.0.0:$PORT`.
5. Env Vars: `SECRET_KEY` (new), `DATABASE_URL` (Neon/Render Postgres), `DEBUG=False`, `ALLOWED_HOSTS=*.onrender.com`, `CORS_ALLOWED_ORIGINS=https://seu-frontend.onrender.com`.

### Neon DB (Serverless Postgres)
- Sign up at neon.tech, create DB, copy `DATABASE_URL` (postgres://...).
- Set in Render env vars.
- Local test: Set `DATABASE_URL` in `.env`, run migrate.

## License
MIT License – see [LICENSE](LICENSE).
Commit das Mudanças (em Inglês)
No terminal do backend (dir social-django):
bashgit add README.md
git commit -m "Update README: Added new endpoints (toggle_follow, is_following), deployment notes for Render/Neon, updated features and structure"
git push origin main
Commit feito? O README agora tá atualizado e pronto pra repo/GitHub. Testa o app — tudo deve rolar! Quer deploy frontend ou mais? 😊### Adjusted README.md
markdown# Snaply - Social Network API 🚀

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/) [![Django](https://img.shields.io/badge/Django-4.2%2B-green)](https://www.djangoproject.com/) [![DRF](https://img.shields.io/badge/DRF-3.15%2B-orange)](https://www.django-rest-framework.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A RESTful API for a social network, built with Django and Django REST Framework (DRF). Supports user registration/login, posts, follows, likes, comments, and personalized feed. Fully authenticated with JWT and documented with Swagger.

## Features
- **Secure Authentication**: JWT tokens for stateless sessions (login/register with token refresh).
- **User Management**: CRUD with partial updates (PATCH for bio only; username/email protected).
- **Post Interactions**: Create, edit, delete, like/unlike (toggle), comments.
- **Follow System**: Follow/unfollow with dynamic toggle and status check; counts for followers/following.
- **Personalized Feed**: Posts from followed users + own posts (always included).
- **Advanced Serialization**: Nested author data, dynamic counts (likes, followers).
- **Automatic Documentation**: Swagger UI and ReDoc for interactive testing.
- **Unit Tests**: Basic coverage for serializers and views.
- **CORS & Deployment Ready**: Config for local/Render/Neon DB.

## Prerequisites
- Python 3.8+.
- Git.

## Quick Installation
1. Clone the repository:
git clone https://github.com/Mauriciofnti/api_social_network.git
cd social-api
text2. Create and activate virtual environment:
python -m venv venv
Windows: venv\Scripts\activate
Linux/Mac: source venv/bin/activate
text3. Install dependencies:
pip install -r requirements.txt
text4. Apply migrations:
python manage.py makemigrations
python manage.py migrate
text5. Create superuser:
python manage.py createsuperuser
text6. Start the server:
python manage.py runserver
text- Admin: `http://127.0.0.1:8000/admin/`
- API: `http://127.0.0.1:8000/api/`

## API Usage
Base URL: `http://127.0.0.1:8000/api/`.

### Main Endpoints
| Method | Endpoint                  | Description                                      | Authentication |
|--------|---------------------------|--------------------------------------------------|---------------|
| GET    | `/users/`                | List users                                       | No            |
| POST   | `/users/`                | Create user (body: `{"username": "...", "email": "...", "password": "...", "bio": "..."}`) | No            |
| GET    | `/users/<id>/`           | User details (open read)                         | No            |
| PATCH  | `/users/<id>/`           | Partial update (body: `{"bio": "..."}`; username/email protected) | Yes (owner only) |
| GET    | `/users/me/`             | Current user details/update                      | Yes           |
| POST   | `/users/<id>/follow/`    | Follow user                                      | Yes           |
| POST   | `/users/<id>/unfollow/`  | Unfollow user                                    | Yes           |
| POST   | `/users/<id>/toggle_follow/` | Toggle follow/unfollow (dynamic button)          | Yes           |
| GET    | `/users/<id>/is_following/` | Check follow status (for button init)            | Yes           |
| POST   | `/posts/`                | Create post (body: `{"content": "..."}`)         | Yes           |
| GET    | `/posts/?author=<id>`    | List user's posts (query param)                  | Yes           |
| GET    | `/posts/<id>/`           | Post details                                     | Yes           |
| PATCH  | `/posts/<id>/`           | Edit post (body: `{"content": "..."}`; owner only) | Yes (owner only) |
| DELETE | `/posts/<id>/`           | Delete post (owner only)                         | Yes (owner only) |
| POST   | `/posts/<id>/like/`      | Like/unlike post (toggle)                        | Yes           |
| POST   | `/posts/<id>/comments/`  | Add comment (body: `{"content": "..."}`)         | Yes           |
| GET    | `/posts/<id>/comments/`  | List post comments                               | Yes           |
| GET    | `/posts/feed/`           | Personalized feed (followed + own posts)         | Yes           |

- **Authentication**: POST `/token/` with `{"username": "...", "password": "..."}` → `{access, refresh, user}`. Use `Authorization: Bearer <access>` for protected. Refresh with POST `/token/refresh/`.

## Testing
- **Postman**: Set `{{base_url}} = http://127.0.0.1:8000`. Save `{{access_token}}` from login response.
- **Swagger UI**: `/api/schema/swagger-ui/` (Authorize with JWT).
- **ReDoc**: `/api/schema/redoc/`.
- **Unit Tests**: `python manage.py test network`.

## Deployment
### Render
1. Push to GitHub.
2. New Web Service > Connect repo.
3. Build: `pip install -r requirements.txt && python manage.py migrate`.
4. Start: `python manage.py runserver 0.0.0.0:$PORT`.
5. Env Vars: `SECRET_KEY` (new), `DATABASE_URL` (Neon/Render Postgres), `DEBUG=False`, `ALLOWED_HOSTS=*.onrender.com`, `CORS_ALLOWED_ORIGINS=https://seu-frontend.onrender.com`.

### Neon DB (Serverless Postgres)
- Sign up at neon.tech, create DB, copy `DATABASE_URL` (postgres://...).
- Set in Render env vars.
- Local test: Set `DATABASE_URL` in `.env`, run migrate.

## Project Structure
social-django/
├── manage.py
├── social_api/          # Global configs
│   ├── settings.py
│   └── urls.py
├── network/             # Main app
│   ├── models.py        # User, Post, Comment
│   ├── serializers.py   # UserSerializer (nested), PostSerializer
│   ├── views.py         # Generics + @api_view (toggle, like)
│   ├── urls.py          # API routes
│   ├── admin.py
│   └── tests.py
├── db.sqlite3           # Local DB (gitignore)
├── requirements.txt
├── README.md
└── .gitignore
text## Contribution
1. Fork the repo.
2. Branch: `git checkout -b feature/new-feature`.
3. Commit: `git commit -m "Add new feature"`.
4. Push: `git push origin feature/new-feature`.
5. PR!

## License
MIT License – see [LICENSE](LICENSE).