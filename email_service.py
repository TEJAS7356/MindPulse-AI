import smtplib
import os
from email.message import EmailMessage
def send_otp(to,otp):
 try:
  get=lambda k,d=None:os.getenv(k,d);u=get('SMTP_USERNAME');pw=get('SMTP_APP_PASSWORD')
  if not u or not pw:return False,'SMTP is not configured in Streamlit Secrets.'
  m=EmailMessage();m['Subject']='Mental Wellbeing Predictor password reset OTP';m['From']=get('SMTP_FROM_EMAIL',u);m['To']=to;m.set_content(f'Your OTP is {otp}. It expires in 5 minutes.')
  with smtplib.SMTP(get('SMTP_HOST','smtp.gmail.com'),int(get('SMTP_PORT',587)),timeout=20) as s:s.starttls();s.login(u,pw);s.send_message(m)
  return True,'OTP sent.'
 except Exception as e:return False,f'Email failed: {e}'
