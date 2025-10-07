# Social API 

Uma API RESTful inspirada em redes sociais, usando Django e Django REST Framework (DRF). Funcionalidades: cadastro de usuários, posts, follows, likes e feed.

## Recursos
- Autenticação JWT.
- Endpoints para usuários, posts e interações.
- Serialização com contagens (ex: número de followers/likes).

## Pré-requisitos
- Python 3.8+.

## Instalação
1. Clone o repositório:
git clone https://github.com/SEU_USUARIO/social-api.git
cd social-api
text2. Crie um ambiente virtual:
python -m venv venv
Ative: venv\Scripts\activate (Windows) ou source venv/bin/activate (Linux/Mac)
text3. Instale dependências:
pip install -r requirements.txt
text4. Rode migrações:
python manage.py makemigrations
python manage.py migrate
text5. Crie um superusuário:
python manage.py createsuperuser
text6. Rode o servidor:
python manage.py runserver
textAcesse em `http://127.0.0.1:8000/admin/` para admin.

## Uso da API
- Base URL: `http://127.0.0.1:8000/api/`.
- Use Postman ou o navegador para testar (DRF tem interface browsable).

### Endpoints Principais
| Método | Endpoint              | Descrição                          | Autenticação? |
|--------|-----------------------|------------------------------------|---------------|
| GET    | /users/              | Lista usuários                     | Não           |
| POST   | /users/              | Cria usuário (body: username, email, password) | Não           |
| GET    | /users/<id>/         | Detalhe de usuário                 | Não           |
| POST   | /users/<id>/follow/  | Segue usuário                      | Sim           |
| POST   | /posts/              | Cria post (body: content)          | Sim           |
| GET    | /posts/              | Lista meus posts                   | Sim           |
| POST   | /posts/<id>/like/    | Curte/descurte post                | Sim           |
| GET    | /feed/               | Feed (posts de quem segue)         | Sim           |

- **Autenticação**: POST `/api/token/` com body `{username: "...", password: "..."}` para obter token. Use header `Authorization: Bearer <token>` em requests protegidos.

## Testando
- Use Postman: Crie collection com base URL `{{base_url}}/api/` (veja setup no tutorial).
- Exemplo de login: POST `/token/` → Copie `access` token.

## Estrutura do Projeto
- `social_api/`: Configurações globais.
- `network/`: App principal (modelos, views, serializers).
- `db.sqlite3`: Banco local (não commite!).

