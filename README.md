# Portfolio CMS

A personal portfolio website with a protected content-management area. It lets the site owner keep portfolio content current without editing HTML for every update.

**Live site:** [abduladhil10.pythonanywhere.com](https://abduladhil10.pythonanywhere.com/)

## Overview

This project is a server-rendered Flask application backed by SQLite. The public site presents projects, skills, experience, education, certifications, a resume link, and a contact form. Authenticated administrators use the `/admin` area to manage the portfolio content.


## Features

- Protected administrator login and logout using Flask-Login; passwords are stored as hashes.
- Project management: create, view, edit, and delete projects with descriptions, technologies, features, categories, status, repository/demo links, and optional images.
- Skill management with categories, plus management pages for experience, education, and certifications.
- Site settings for profile details, contact information, social links, and portfolio copy.
- PDF resume upload and replacement, with PDF signature validation and a 5 MB request-size limit.
- Contact form that stores visitor messages for review in the admin area.
- CSRF protection with Flask-WTF and CSRF tokens in forms.
- Responsive public and admin interfaces, including mobile breakpoints in the stylesheet.
- Version-controlled with Git and hosted on GitHub; deployed on PythonAnywhere.

## Tech stack

| Area | Technology |
| --- | --- |
| Backend | Python, Flask |
| Data | SQLite |
| Authentication | Flask-Login, Werkzeug password hashing |
| Form security | Flask-WTF / CSRFProtect |
| Templates and UI | Jinja, HTML, CSS, JavaScript |
| Configuration | python-dotenv environment variables |
| Production server dependency | Gunicorn |
| Hosting | PythonAnywhere |
| Version control | Git and GitHub |

## Application structure

```text
Portfolio/
├── app.py                 # Flask routes, authentication, upload handling
├── database.py            # SQLite schema creation and connections
├── create_admin.py        # Interactive administrator-account creation script
├── seed_skills.py         # Optional starter-skill seeding script
├── requirements.txt       # Python dependencies
├── templates/             # Public and admin Jinja templates
└── static/
    ├── css/               # Responsive stylesheets
    ├── images/projects/   # Uploaded project images
    └── resume/            # Uploaded resume PDFs
```

The application initializes its SQLite schema at startup. Portfolio data is stored in tables for projects, settings, skills, experience, education, certifications, administrators, and contact messages.

## Run locally on Windows with VS Code

1. Clone the repository and open its folder in VS Code.

   ```powershell
   git clone https://github.com/abduladhill/Portfolio.git
   cd Portfolio
   code .
   ```

2. Create and activate a virtual environment.

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the dependencies.

   ```powershell
   py -m pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root. Generate your own unpredictable value for `SECRET_KEY`; do not commit this file.

   ```env
   SECRET_KEY=replace-with-a-long-random-secret
   FLASK_DEBUG=1
   SESSION_COOKIE_SECURE=0
   ```

   Set `SESSION_COOKIE_SECURE=1` when serving the app over HTTPS in production. `.env` files are already excluded by `.gitignore`.

5. Start the application.

   ```powershell
   py app.py
   ```

   Open the local address shown in the terminal, then visit `/admin/login` to access the administration area.

6. Create the first admin account when needed.

   ```powershell
   py create_admin.py
   ```

   The script prompts for the username and password and saves only a password hash in the SQLite database.

## Deployment

The deployed portfolio is available at [https://abduladhil10.pythonanywhere.com/](https://abduladhil10.pythonanywhere.com/). Configure `SECRET_KEY` (and, for HTTPS, `SESSION_COOKIE_SECURE=1`) in the deployment environment rather than adding secrets to the repository.

## Featured Project: Phishing URL Detection

A machine-learning web application that analyzes URL-based features to estimate whether a URL may be phishing. It uses an Extra Trees classifier and a Streamlit interface.

- **Live demo:** [Try the phishing URL detector](https://phishing-url-detection-a8whjsyefcrze4ykhdevec.streamlit.app/)
- **Source code:** [GitHub repository](https://github.com/abduladhill/phishing-url-detection)
- **Reported evaluation:** 96.66% accuracy and 94.31% phishing recall on a hostname-grouped held-out test split.

The model uses URL-string features only. Its predictions are not a guarantee that a link is safe or malicious.

## Portfolio Screenshots

This section is reserved for screenshots of the portfolio website itself. Phishing detector screenshots belong in the phishing detector repository.

## License

No license file is currently included in this repository.
