# Snaply - Social Network API 🚀

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/) [![Django](https://img.shields.io/badge/Django-4.2%2B-green)](https://www.djangoproject.com/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A RESTful API inspired by social networks, built with Django and Django REST Framework (DRF). Supports user registration, posts, follows, likes, comments, and personalized feed. Fully authenticated with JWT and documented with Swagger.

## Features
- **Secure Authentication**: JWT tokens for stateless sessions.
- **Robust Endpoints**: CRUD for users and posts, with interactions (follow, like, comments, feed).
- **Advanced Serialization**: Dynamic counts (followers, likes) and nested data; partial updates (PATCH) for bio/password (blocks username/email).
- **Automatic Documentation**: Swagger UI and ReDoc for interactive testing.
- **Unit Tests**: Basic coverage for serializers and views.

## Prerequisites
- Python 3.8+.
- Git.

## Quick Installation
1. Clone the repository:
   ```
   git clone https://github.com/Mauriciofnti/api_social_network.git
   cd social-api
   ```
2. Create and activate virtual environment:
   ```
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Linux/Mac: source venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Apply migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Create superuser:
   ```
   python manage.py createsuperuser
   ```
6. Start the server:
   ```
   python manage.py runserver
   ```
   - Admin: `http://127.0.0.1:8000/admin/`
   - API: `http://127.0.0.1:8000/api/`

## API Usage
Base URL: `http://127.0.0.1:8000/api/`.

### Main Endpoints
| Method | Endpoint                  | Description                                      | Authentication |
|--------|---------------------------|--------------------------------------------------|---------------|
| GET    | `/users/`                | List users                                       | No            |
| POST   | `/users/`                | Create user (body: `{"username": "...", "email": "...", "password": "...", "bio": "..."}`) | No            |
| GET    | `/users/<id>/`           | User details (open read)                         | No            |
| PATCH  | `/users/<id>/`           | Partial update (body: ex. `{"bio": "...", "email": "..."}`; blocks username/email) | Yes (owner only) |
| POST   | `/users/<id>/follow/`    | Follow user                                      | Yes           |
| POST   | `/users/<id>/unfollow/`  | Unfollow user                                    | Yes           |
| POST   | `/posts/`                | Create post (body: `{"content": "..."}`)         | Yes           |
| GET    | `/posts/`                | List logged-in user's posts                      | Yes           |
| GET    | `/posts/<id>/`           | Post details                                     | Yes           |
| POST   | `/posts/<id>/like/`      | Like/unlike post                                 | Yes           |
| POST   | `/posts/<id>/comments/`  | Add comment (body: `{"content": "..."}`)         | Yes           |
| GET    | `/posts/<id>/comments/`  | List post comments                               | Yes           |
| GET    | `/feed/`                 | Feed (posts from followed users)                 | Yes           |

- **Authentication**: POST `/api/token/` with body `{"username": "...", "password": "..."}` → Returns `access` and `refresh`. Use header `Authorization: Bearer <access_token>` for protected endpoints. Renew with POST `/api/token/refresh/`.

## Testing
- **Postman**: Create a collection with variable `{{base_url}} = http://127.0.0.1:8000`. Add script in "Tests" of login to save `{{access_token}}`.
- **Swagger UI**: `http://127.0.0.1:8000/api/schema/swagger-ui/` (click "Authorize" for JWT).
- **ReDoc**: `http://127.0.0.1:8000/api/schema/redoc/`.
- **Unit Tests**: `python manage.py test network`.

## Project Structure
```
social-django/
├── manage.py
├── social_api/          # Global configurations
│   ├── settings.py
│   └── urls.py
├── network/             # Main app
│   ├── models.py        # User, Post, Comment
│   ├── serializers.py   # UserSerializer, PostSerializer, CommentSerializer
│   ├── views.py         # Generic views and @api_view
│   ├── urls.py          # API routes
│   ├── admin.py
│   └── tests.py         # Unit tests
├── db.sqlite3           # Local DB (ignored in Git)
├── requirements.txt     # Dependencies
├── README.md            # This file
└── .gitignore           # Excludes venv, db, etc.
```

## Contribution
1. Fork the repo.
2. Create branch: `git checkout -b feature/new-feature`.
3. Commit: `git commit -m "Add new feature"`.
4. Push: `git push origin feature/new-feature`.
5. Open PR.

Issues for bugs or ideas!

## License
MIT License – see [LICENSE](LICENSE).