import cv2
import numpy as np

EXPRESSIONS = ('Happy', 'Neutral', 'Sad', 'Angry', 'Surprised', 'Fearful')


def analyze(uploaded):
    if not uploaded:
        return None, 'Capture or upload an image first.'
    try:
        raw = uploaded.getvalue() if hasattr(uploaded, 'getvalue') else uploaded.read()
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return None, 'Image could not be read.'
        if not hasattr(cv2, 'CascadeClassifier'):
            return None, 'Expression model could not load on this server. Reinstall opencv-python-headless below version 5.'
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        if face_cascade.empty() or smile_cascade.empty():
            return None, 'Expression model could not load on this server.'
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(70, 70))
        if len(faces) == 0:
            return None, 'No face detected. Try a front-facing image with good lighting.'

        x, y, w, h = max(faces, key=lambda z: z[2] * z[3])
        roi = gray[y:y + h, x:x + w]
        contrast = float(roi.std())
        brightness = float(roi.mean())
        edges = cv2.Canny(roi, 80, 160)
        edge_density = float(np.count_nonzero(edges)) / max(1, edges.size)
        lower = roi[int(h * .48):, :]
        smiles = smile_cascade.detectMultiScale(lower, scaleFactor=1.7, minNeighbors=18, minSize=(max(20, int(w * .18)), max(10, int(h * .08)))
        )

        # This is a lightweight visible-expression heuristic, not a clinical or
        # emotion-recognition model. It deliberately describes expression only.
        if len(smiles):
            expression = 'Happy'
        elif edge_density > .24 and contrast > 58:
            expression = 'Surprised'
        elif brightness < 62 and contrast > 48:
            expression = 'Fearful'
        elif edge_density > .19 and brightness < 105:
            expression = 'Angry'
        elif brightness < 82:
            expression = 'Sad'
        else:
            expression = 'Neutral'

        confidence = min(.94, max(.52, .55 + min(.35, contrast / 220) + (0.08 if len(smiles) else 0)))
        return {'expression': expression, 'confidence': float(confidence), 'face_count': len(faces), 'image': img}, None
    except cv2.error:
        return None, 'Expression analysis could not process this frame.'
    except Exception as exc:
        return None, f'Expression analysis failed: {exc}'


def supportive(expression):
    return {
        'Happy': 'You appear to be showing a positive expression. Keep engaging in activities that make you feel good.',
        'Neutral': 'Your expression appears neutral. Take a moment to check in with how you are feeling.',
        'Sad': 'It looks like you may be having a difficult moment. It is okay to pause and talk to someone you trust.',
        'Angry': 'Your expression appears tense. Consider pausing, breathing slowly, and giving yourself space.',
        'Surprised': 'Your expression appears surprised. Take a moment to notice what you need.',
        'Fearful': 'Your expression appears concerned. Move to a place where you feel safe and consider talking to someone you trust.',
    }.get(expression, 'Take a gentle moment to check in with yourself.')
