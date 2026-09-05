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

```
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

```
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

1. Create an account at [Render](https://render.com/).

1. Select **New → Web Service**.

1. Connect the GitHub repository.

1. Select the Python environment.

1. Use this build command:

```bash
pip install -r requirements.txt
```

1. Use this start command:

```bash
gunicorn app:app
```

1. Add `SECRET_KEY`, `GEMINI_API_KEY`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_APP_PASSWORD`, and `SMTP_FROM_EMAIL` under Render environment variables.

1. Deploy the service.

1. Open the public Render URL.

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

## Gemini integration note

The companion uses the current `google-genai` SDK with a fresh client for each request, explicit client cleanup, no tools, and automatic function calling disabled. The dependency is pinned below major version 3 (`google-genai>=0.3,<3`) to avoid the documented AFC behavior change. If `GEMINI_API_KEY` is absent or the provider is temporarily unavailable, the application returns a safe fallback message instead of crashing.

## Facial Expression Analysis

The Facial Expression Analysis page uses the browser camera only after the user clicks **Enable camera** and grants permission. The browser captures a frame every 1.5 seconds and sends it to the authenticated Flask endpoint `/api/analyze-face`. The backend uses the existing OpenCV Haar cascade implementation in `face_emotion.py` to detect a visible face and return one of six educational expression labels: **Happy, Neutral, Sad, Angry, Surprised, or Fearful**, together with a confidence value and supportive message.

The feature describes visible facial expression only. It is **not a mental-health diagnosis**, and expressions such as Sad are not converted into wellbeing risk. If no face is visible, the interface shows **No face detected**. On Render, use the HTTPS deployment URL because browsers require a secure context for camera access.

The feature files are `static/js/camera.js`, `face_emotion.py`, `app.py`, `templates/facial_expression.html`, `templates/base.html`, and `static/css/expression-colors.css`.

## Password-reset email on Render

Render Free blocks outbound SMTP connections, so password-reset OTP delivery uses the **Resend HTTPS API** instead of Gmail SMTP. The existing flow is unchanged: **Forgot Password → Send OTP → Verify OTP → Reset Password**.

Create a Resend account, create an API key, and configure the sender address in the Resend dashboard. For local development, put the following values in `.env` or export them in PowerShell. For Render, add the same values under **Dashboard → Service → Environment → Environment Variables**:

```
RESEND_API_KEY=re_your_resend_api_key
RESEND_FROM_EMAIL=MindPulse AI <onboarding@resend.dev>
```

For production, verify your own domain with Resend and use a sender such as:

```
RESEND_FROM_EMAIL=MindPulse AI <noreply@yourdomain.com>
```

The sender implementation is in `email_service.py` and uses Python's built-in HTTPS client, so no additional package is required. The old SMTP variables are no longer read and can be removed:

```
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_APP_PASSWORD
SMTP_FROM_EMAIL
```

Never commit `.env`, API keys, or app passwords to GitHub. If the Resend API is unavailable or incorrectly configured, the application returns a clear email-delivery error and does not silently mark the OTP as sent.

## OpenCV compatibility for Facial Expression Analysis

The facial-expression feature requires the OpenCV 4.x Haar Cascade API. The project pins the dependency in `requirements.txt` as:

```
opencv-python-headless>=4.8,<5
```

OpenCV 5 may not expose `cv2.CascadeClassifier`, which causes facial analysis to fail. For local development, using the project virtual environment is recommended:

```
cd "C:\Users\tejas\Downloads\MindPulse-AI-Flask\Mental-Wellbeing-Predictor"
..\.venv\Scripts\Activate.ps1
python -m pip install --upgrade "opencv-python-headless>=4.8,<5"
python -c "import cv2; print(cv2.__version__); print(hasattr(cv2, 'CascadeClassifier'))"
python app.py
```

The verification command should print an OpenCV 4.x version and `True`. A virtual environment is not required by Flask, but it prevents this project’s dependencies from conflicting with other Python projects. Render creates its own environment automatically; commit and push the updated `requirements.txt`, then redeploy. If Render retains OpenCV 5 in its build cache, use **Manual Deploy → Clear build cache & deploy**.