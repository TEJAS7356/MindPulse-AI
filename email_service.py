"""HTTPS email delivery for password-reset OTPs.

The Flask authentication flow calls send_otp(to, otp). This module keeps that
interface unchanged while using Resend's HTTPS API, which works on Render Free
where outbound SMTP connections are blocked.
"""
import json
import os
import urllib.error
import urllib.request


def send_otp(to, otp):
    api_key = os.getenv('RESEND_API_KEY')
    sender = os.getenv('RESEND_FROM_EMAIL') or os.getenv('EMAIL_FROM_EMAIL')

    if not api_key:
        return False, 'Email is not configured: set RESEND_API_KEY.'
    if not sender:
        return False, 'Email is not configured: set RESEND_FROM_EMAIL.'
    if not to:
        return False, 'Email delivery failed: recipient address is missing.'

    payload = {
        'from': sender,
        'to': [to],
        'subject': 'MindPulse AI password reset OTP',
        'text': f'Your MindPulse AI password reset OTP is {otp}. It expires in 5 minutes.',
    }
    request = urllib.request.Request(
        'https://api.resend.com/emails',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'MindPulse-AI/1.0',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if 200 <= response.status < 300:
                return True, 'OTP sent.'
            return False, f'Email API failed with HTTP {response.status}.'
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode('utf-8')).get('message', exc.reason)
        except (ValueError, UnicodeDecodeError):
            detail = exc.reason
        return False, f'Email API failed: {detail}'
    except urllib.error.URLError as exc:
        return False, f'Email API connection failed: {exc.reason}'
    except TimeoutError:
        return False, 'Email API timed out. Please try again.'
    except Exception as exc:
        return False, f'Email API failed: {exc}'
