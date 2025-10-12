# Social API 🚀

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/) [![Django](https://img.shields.io/badge/Django-4.2%2B-green)](https://www.djangoproject.com/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Uma API RESTful inspirada em redes sociais, construída com Django e Django REST Framework (DRF). Suporta cadastro de usuários, posts, follows, likes e feed personalizado. Totalmente autenticada com JWT e documentada com Swagger.

## Recursos
- **Autenticação Segura**: Tokens JWT para sessões stateless.
- **Endpoints Robustos**: CRUD para usuários e posts, com interações (follow, like, feed).
- **Serialização Avançada**: Contagens dinâmicas (followers, likes) e aninhamento de dados.
- **Documentação Automática**: Swagger UI e ReDoc para testes interativos.
- **Testes Unitários**: Cobertura básica para serializers e views.

## Pré-requisitos
- Python 3.8+.
- Git.

## Instalação Rápida
1. Clone o repositório:
   ```
   git clone https://github.com/Mauriciofnti/api_social_network.git
   cd social-api
   ```
2. Crie e ative ambiente virtual:
   ```
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Linux/Mac: source venv/bin/activate
   ```
3. Instale dependências:
   ```
   pip install -r requirements.txt
   ```
4. Aplique migrações:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Crie superusuário:
   ```
   python manage.py createsuperuser
   ```
6. Inicie o servidor:
   ```
   python manage.py runserver
   ```
   - Admin: `http://127.0.0.1:8000/admin/`
   - API: `http://127.0.0.1:8000/api/`

## Uso da API
Base URL: `http://127.0.0.1:8000/api/`.

### Endpoints Principais
| Método | Endpoint                  | Descrição                                      | Autenticação |
|--------|---------------------------|------------------------------------------------|--------------|
| GET    | `/users/`                | Lista usuários                                 | Não         |
| POST   | `/users/`                | Cria usuário (body: `{"username": "...", "email": "...", "password": "..."}`) | Não         |
| GET    | `/users/<id>/`           | Detalhes de usuário                            | Não         |
| POST   | `/users/<id>/follow/`    | Segue usuário                                  | Sim         |
| POST   | `/users/<id>/unfollow/`  | Para de seguir usuário                         | Sim         |
| POST   | `/posts/`                | Cria post (body: `{"content": "..."}`)         | Sim         |
| GET    | `/posts/`                | Lista posts do usuário logado                  | Sim         |
| GET    | `/posts/<id>/`           | Detalhes de post                               | Sim         |
| POST   | `/posts/<id>/like/`      | Curte/descurte post                            | Sim         |
| GET    | `/feed/`                 | Feed (posts de usuários seguidos)              | Sim         |

- **Autenticação**: POST `/api/token/` com body `{"username": "...", "password": "..."}` → Retorna `access` e `refresh`. Use header `Authorization: Bearer <access_token>` em endpoints protegidos. Renove com POST `/api/token/refresh/`.

## Testando
- **Postman**: Crie uma collection com variável `{{base_url}} = http://127.0.0.1:8000`. Adicione script no "Tests" do login para salvar `{{access_token}}`.
- **Swagger UI**: `http://127.0.0.1:8000/api/schema/swagger-ui/` (clique "Authorize" para JWT).
- **ReDoc**: `http://127.0.0.1:8000/api/schema/redoc/`.
- **Testes Unitários**: `python manage.py test network`.

## Estrutura do Projeto
```
social-django/
├── manage.py
├── social_api/          # Configurações globais
│   ├── settings.py
│   └── urls.py
├── network/             # App principal
│   ├── models.py        # User, Post
│   ├── serializers.py   # UserSerializer, PostSerializer
│   ├── views.py         # Views genéricas e @api_view
│   ├── urls.py          # Rotas da API
│   ├── admin.py
│   └── tests.py         # Testes unitários
├── db.sqlite3           # Banco local (ignorado no Git)
├── requirements.txt     # Dependências
├── README.md            # Este arquivo
└── .gitignore           # Exclui venv, db, etc.
```

## Deploy
- **Heroku (Grátis)**: Adicione `Procfile` (`web: gunicorn social_api.wsgi`), `runtime.txt` (`python-3.12.3`), instale `gunicorn dj-database-url`. Rode `heroku create`, `git push heroku main`, `heroku run migrate`.
- Alternativas: Railway (GitHub auto-deploy), Vercel.

## Contribuição
1. Fork o repo.
2. Crie branch: `git checkout -b feature/nova-funcionalidade`.
3. Commit: `git commit -m "Adiciona nova funcionalidade"`.
4. Push: `git push origin feature/nova-funcionalidade`.
5. Abra PR.

Issues para bugs ou ideias!

## Licença
MIT License – veja [LICENSE](LICENSE).