# SpaceZone-DjangoPanel

A Django project for managing the **SpaceZone Panel**.  
This project includes a custom authentication system (register/login with email codes), base applications, and initial configurations for quickly setting up an admin panel.

## Features
- Custom authentication system:
  - Unified endpoints for register/login (`/api/auth/send-code/`, `/api/auth/verify-code/`)
  - Secure code verification with expiration & one-time usage
  - Rate limiting (≥30s between requests, max 5 codes per day)
-  Basic admin panel with Django Admin
-  Applications: `accounts` and `SpaceZone`
-  Environment configuration via `.env`
-  Ready for development and future expansion

## Installation

1. Clone the repository:
```bash
git clone https://github.com/CNoox/SpaceZone-DjangoPanel.git
cd SpaceZone-DjangoPanel
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
venv\Scripts\activate   # For Windows
# or: source venv/bin/activate   # For Linux/macOS
pip install -r requirements.txt
```

3. Apply migrations:
```bash
python manage.py migrate
```

4. Run the development server:
```bash
python manage.py runserver
```

Then open your browser and go to [http://127.0.0.1:8000](http://127.0.0.1:8000).

## API Endpoints (Auth)

| Method | Endpoint             | Description                          |
|--------|----------------------|--------------------------------------|
| POST   | `/api/auth/send-code/`   | Send verification code (register/login) |
| POST   | `/api/auth/verify-code/` | Verify code (register/login)         |

## Important Notes
- The `.env` file contains sensitive settings and should **not** be uploaded to GitHub.
- Use a proper Django `.gitignore` to avoid pushing unnecessary or sensitive files.

## Project Structure
```
SpaceZone-DjangoPanel/
│
├─ SpaceZone/       # Main application
├─ accounts/        # Authentication & user management
├─ manage.py
├─ requirements.txt
└─ .env             # Environment settings (sensitive)
```

## License
This project is licensed under the MIT License.

## Partnering Project
Frontend for this project can be found at: https://github.com/AliAbdiDev/SpaceZone-NextPanel
