import os

FALLBACK = 'Gemini is not configured. Add GEMINI_API_KEY to your environment. For now, consider writing down what you feel and contacting someone you trust.'

def reply(message, context=''):
    """Make one stateless Gemini request for the companion.

    A fresh client is intentionally created per request and closed in finally.
    No tools are supplied, and AFC is explicitly disabled because the companion
    only needs text generation.
    """
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        return FALLBACK
    prompt = f'''You are an empathetic AI Wellbeing Companion, not a therapist, doctor, or medical professional. Never diagnose, prescribe, or claim to provide therapy. Give concise general wellbeing guidance. If there is self-harm or immediate danger, encourage local emergency services, a trusted person, and qualified professional help. Message: {message}\nContext: {context}'''
    client = None
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
        config = types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=500,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        response = client.models.generate_content(
            model=os.getenv('GEMINI_MODEL', 'gemini-3.6-flash'),
            contents=prompt,
            config=config,
        )
        text = getattr(response, 'text', None)
        return text.strip() if text else 'I could not generate a response just now. Please try again.'
    except Exception as exc:
        return f'Gemini is unavailable right now ({exc}). Please try again later or contact someone you trust.'
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass
