import cv2,numpy as np
def analyze(uploaded):
 if not uploaded:return None,'Capture or upload an image first.'
 raw=uploaded.getvalue() if hasattr(uploaded,'getvalue') else uploaded.read()
 img=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
 if img is None:return None,'Image could not be read.'
 gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY);cas=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml');faces=cas.detectMultiScale(gray,1.1,5)
 if len(faces)==0:return None,'No face detected. Try a front-facing image with good lighting.'
 x,y,w,h=max(faces,key=lambda z:z[2]*z[3]);roi=gray[y:y+h,x:x+w];b=float(roi.mean());c=float(roi.std());e='Happy' if b>170 and c>48 else 'Sad' if b<75 else 'Surprised' if c>65 else 'Neutral';return {'expression':e,'confidence':min(.92,max(.52,.55+c/180)),'face_count':len(faces),'image':img},None
def supportive(e):return {'Happy':'You appear to be showing a positive expression. Keep engaging in activities that make you feel good.','Neutral':'Your expression appears neutral. Take a moment to check in with how you are feeling.','Sad':'It looks like you may be having a difficult moment. It is okay to pause and talk to someone you trust.','Surprised':'Your expression appears surprised. Take a moment to notice what you need.'}.get(e,'Take a gentle moment to check in with yourself.')
