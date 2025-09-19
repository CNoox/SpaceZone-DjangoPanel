# SpaceZone Django Panel

A robust, modern Django RESTful backend built for authentication, panel management, and scalable API development.  
Empowered with JWT authentication, code-based login/registration, and interactive OpenAPI documentation.

---

## 🚀 Features

- **Modern Django REST API**: Built on Django and Django REST Framework for flexible, secure, and fast APIs.
- **JWT Authentication**: Secure, stateless authentication with token refresh support.
- **Phone/Email Code Verification**: Send and verify codes for user login and registration.
- **User Panel Endpoint**: Dedicated endpoint for user dashboard and profile management.
- **Interactive API Docs**: Swagger UI powered by `drf-spectacular`.  
- **OpenAPI Schema**: Easily integrate your frontend or mobile app.
- **Environment-based Static/Media Handling**: Smart static/media configuration in debug/deploy mode.
- **Extensible Structure**: Simple to add new apps, endpoints, and business logic.
- **Production-ready**: Structured for easy deployment, scaling, and environment management.

---

## 🗂️ Project Structure

```
SpaceZone-DjangoPanel/
│
├── SpaceZone/             # Main Django project (global settings, URLs)
│   └── urls.py
│
├── accounts/              # User authentication and panel logic
│   ├── urls.py
│   └── views.py
│
├── manage.py
└── ...
```

---

## 🛣️ API Endpoints & HTTP Methods

All endpoints are prefixed by `/api/`.  
**HTTP methods are based directly on the code implementation.**

| Endpoint                       | Methods             | Description                                  |
|--------------------------------|---------------------|----------------------------------------------|
| `/api/auth/send-code/`         | POST                | Send a verification code to the user (login/register) |
| `/api/auth/verify-code/`       | POST                | Verify the received code for authentication  |
| `/api/panel/`                  | GET, PATCH, DELETE  | GET: Profile info<br>PATCH: Partial update<br>DELETE: Soft delete (deactivate)|
| `/api/refresh/`                | POST                | Refresh JWT token                            |
| `/api/schema/`                 | GET                 | Retrieve OpenAPI schema                      |
| `/api/schema/swagger-ui/`      | GET                 | Interactive API docs (Swagger UI)            |

> **Note:**  
> - No Redoc UI is provided by default (Swagger UI only).
> - In DEBUG mode, static/media routes are served automatically.

---

## 🧰 Quick Start

1. **Clone the repository**
    ```bash
    git clone https://github.com/CNoox/SpaceZone-DjangoPanel.git
    cd SpaceZone-DjangoPanel
    ```

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run migrations**
    ```bash
    python manage.py migrate
    ```

4. **Create a superuser**
    ```bash
    python manage.py createsuperuser
    ```

5. **Run the development server**
    ```bash
    python manage.py runserver
    ```

6. **Access the API**
    - Swagger UI: [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
    - Admin Panel: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 🛡️ Security & Production

- Use a strong, unique secret key (see `.env` or your settings).
- Set `DEBUG = False` in production.
- Configure allowed hosts and secure CORS settings.
- Use HTTPS in deployment.

---

## 🤖 Tech Stack

- **Backend**: Django, Django REST Framework
- **Auth**: SimpleJWT
- **Docs**: drf-spectacular (Swagger UI)
- **Database**: Default SQLite (swap to Postgres/MySQL easily)
- **Python**: 3.10+

---

## 📦 Extending

- Add your own apps in the root directory.
- Register new routes in `SpaceZone/urls.py` and link to your app's `urls.py`.
- Write new API views using DRF's `APIView` or viewsets.

---

## 🙌 Credits & License

Built by [CNoox](https://github.com/CNoox)  
Open to contributions & pull requests.

**License:** MIT

---