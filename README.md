# MindPulse AI

**AI-Powered Mental Wellbeing Intelligence Platform** built as a polished Flask web application. This refactor reuses the existing ML model, SQLite database, authentication, Gemini integration, Gmail OTP flow, and OpenCV expression analysis while replacing Streamlit widgets with a responsive HTML/CSS/JavaScript product experience.

## What the project does

MindPulse AI provides an educational wellbeing risk estimate from self-reported lifestyle information. It combines a saved scikit-learn Random Forest model, model explanations, personalized non-medical recommendations, a what-if simulator, private history and trends, browser camera expression analysis, and an optional Gemini AI Wellbeing Companion.

## Features

- Premium responsive landing page
- Registration, login, logout, PBKDF2 password hashing, and Flask sessions
- Gmail SMTP OTP password recovery
- Multi-step assessment with progress indicator
- Low, Moderate, and High Risk educational estimates
- Prediction probabilities, key factor analysis, and recommendations
- What-if simulator
- User-isolated prediction history and trend view
- Analytics and ML concepts/viva page
- Browser camera permission flow and OpenCV expression analysis
- Supportive expression messages
- Gemini AI Wellbeing Companion with crisis-aware safety wording
- Local-storage light/dark theme persistence
- Responsive desktop, tablet, and mobile layouts

## Safety disclaimer

> This application is an educational AI/ML project that provides a wellbeing risk estimate based on self-reported lifestyle information and optional facial-expression analysis. It is not a medical diagnostic tool and should not be used as a substitute for professional mental-health advice.

Facial analysis describes visible expression only. It does not detect mental illness. The AI companion is not a therapist, doctor, or medical professional. If someone may be in immediate danger, they should contact local emergency services, a trusted person, and qualified professional support.

## Architecture

```text
Browser HTML/CSS/JavaScript
          ↓
      Flask routes
          ↓
  Existing auth/database services
          ↓
SQLite + saved Random Forest model
          ↓
Optional Gmail SMTP / Gemini API
```

The Flask entry point is `app.py`. Reusable modules are `auth.py`, `database.py`, `model.py`, `email_service.py`, `ai_service.py`, and `face_emotion.py`. Jinja templates are under `templates/`; custom CSS and JavaScript are under `static/`.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`.

For a production-style local run:

```bash
gunicorn app:app
```

The existing dataset is `data/wellbeing_dataset.csv` and the saved model is `models/wellbeing_model.pkl`. The first model access trains the model if the model file is absent. SQLite is stored in `wellbeing.db` for the college demo.

## Environment variables

Create a `.env` locally if you use a dotenv loader or export variables in your shell. Never commit it.

```text
SECRET_KEY=replace-with-a-long-random-value
GEMINI_API_KEY=your-gemini-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=yourgmail@gmail.com
SMTP_APP_PASSWORD=your-gmail-app-password
SMTP_FROM_EMAIL=yourgmail@gmail.com
ADMIN_EMAIL=optional-admin-email
```

The Flask app reads environment variables directly. Gmail requires a Google App Password, not your normal Gmail password.

## Render deployment

1. Push the project to GitHub.
2. Create an account at [Render](https://render.com/).
3. Select **New → Web Service**.
4. Connect the GitHub repository.
5. Select the Python environment.
6. Use this build command:

```bash
pip install -r requirements.txt
```

7. Use this start command:

```bash
gunicorn app:app
```

8. Add `SECRET_KEY`, `GEMINI_API_KEY`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_APP_PASSWORD`, and `SMTP_FROM_EMAIL` under Render environment variables.
9. Deploy the service.
10. Open the public Render URL.

### Render SQLite limitation

SQLite and local filesystem storage are retained for the college demo as requested. Render’s free service has an ephemeral filesystem, so local SQLite data is **not suitable for permanent production persistence** and may be lost after a restart or redeploy. A production system should later migrate to a managed database, but this project intentionally keeps SQLite for the academic requirement.

## ML methodology

The model uses a synthetic educational dataset with features including age, sleep, sleep quality, stress, mood, physical activity, exercise frequency, screen time, study hours, social interaction, anxiety, and satisfaction. Numeric inputs are imputed, physical activity is one-hot encoded, and a Random Forest classifier is evaluated on a held-out test split. Metrics are shown on the Analytics page. These metrics are not clinical validation.

## Testing

The Flask app was checked for Python syntax, application import, route rendering with Flask’s test client, model loading, prediction generation, user-scoped database access, and Gunicorn startup compatibility.

## Future scope

Possible future work includes a managed database, a validated consented wellbeing dataset, SHAP-based explainability, stronger trained facial-expression models, role-based administration, automated test coverage, and a clinician-reviewed safety design.

## Additional wellbeing suite

The authenticated product sidebar now exposes the complete extended feature set: downloadable personal HTML reports, Explainable AI, profile and settings, private journaling, daily mood check-ins, habit tracking, guided breathing, personalized weekly goals, protected admin analytics, and dataset-range outlier warnings. All personal records use `user_id` isolation in SQLite. Admin analytics requires the signed-in email to match the `ADMIN_EMAIL` environment variable.

The report download is intentionally HTML so it remains dependency-light and printable from any browser. Use the browser’s Print command to save it as PDF.
