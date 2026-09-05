# Mental Wellbeing Predictor

A complete Streamlit college AIML project with secure registration/login, SQLite user isolation, Gmail OTP password reset, Random Forest wellbeing-risk classification, Plotly analytics, history/trends, what-if simulation, OpenCV facial-expression analysis, and optional Gemini AI Wellbeing Companion.

## Safety
This is **not a medical diagnostic tool**. It does not diagnose depression, anxiety, mental illness, or any medical condition. Facial analysis describes visible expression only. The companion is not a therapist, doctor, or medical professional.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```
The first run creates the synthetic educational dataset, trains and saves the model, and initializes SQLite.

## Optional secrets
Create `.streamlit/secrets.toml` locally and never commit it:
```toml
GEMINI_API_KEY = "your-key"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "yourgmail@gmail.com"
SMTP_APP_PASSWORD = "your-16-character-app-password"
SMTP_FROM_EMAIL = "yourgmail@gmail.com"
ADMIN_EMAIL = "your-admin-email@example.com"
```
For Gmail, enable 2-Step Verification and create an App Password. Never use your normal Gmail password. `ADMIN_EMAIL` is optional; when configured, only that account sees aggregate Admin Analytics. Without these secrets the core application works and optional features show safe configuration messages.

## Streamlit Community Cloud
Push this folder to GitHub, choose `app.py` as the main file, then add the values above under **Settings → Secrets**. Do not upload the secrets file, database, or credentials.

## Project structure
`app.py` is the UI and navigation. `model.py` creates the documented synthetic dataset and model. `database.py` performs SQLite and user-scoped queries. `auth.py` handles PBKDF2 password hashing and OTP verification. `face_emotion.py` uses OpenCV face detection plus a transparent lightweight visual heuristic; it is not a clinical emotion detector. `ai_service.py` and `email_service.py` integrate Gemini and Gmail only when configured. `utils.py` contains theme styling and input-based recommendations.

## Viva summary
This is supervised three-class classification. Numeric inputs are median-imputed, physical activity is one-hot encoded, and a Random Forest is trained with an 80/20 stratified split. Metrics are computed on a held-out test split and feature importances come from the saved model. Recommendations use actual user values. History queries always filter by logged-in `user_id`.

## Limitations
The dataset is synthetic and educational, not clinically validated. The face component can be affected by lighting, pose, camera quality, and bias. Future work could use a consented validated dataset, calibration, accessibility testing, and professional safety review.

## Added wellbeing tools

The current version also includes downloadable assessment reports, an Explainable AI page with global feature importance and directional local explanations, profile and privacy settings, private journaling, daily mood/energy/stress check-ins, habit tracking, personalized weekly goals, an offline breathing-exercise guide, anonymous aggregate admin analytics, and warnings when an input is outside the common range of the educational dataset. These features are wellness-support tools only and do not provide clinical conclusions.
