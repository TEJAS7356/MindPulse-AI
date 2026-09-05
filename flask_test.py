from app import app
import database, auth
app.config['TESTING']=True
client=app.test_client()
# Public routes
for path in ['/','/login','/register','/about','/forgot-password']:
    r=client.get(path); assert r.status_code==200,(path,r.status_code)
# Register and login with a unique test user
email='flask-smoke@example.com'
old=database.find_user(email)
if old: database.delete_all_user_data(old['id'])
with database.conn() as c:
    if old: c.execute('DELETE FROM users WHERE id=?',(old['id'],))
r=client.post('/register',data={'name':'Flask Smoke','email':email,'password':'Password1','confirm_password':'Password1'},follow_redirects=True); assert r.status_code==200
r=client.post('/login',data={'email':email,'password':'Password1'},follow_redirects=True); assert r.status_code==200 and b'Good to see you' in r.data
# Authenticated pages
for path in ['/dashboard','/assessment','/history','/trends','/analytics','/ml-concepts','/facial-expression','/ai-companion','/about']:
    r=client.get(path); assert r.status_code==200,(path,r.status_code)
# Assessment post
form={'age':'21','sleep_hours':'5','sleep_quality':'4','stress_level':'8','mood_rating':'4','physical_activity':'Low','exercise_frequency':'1','screen_time':'9','study_hours':'8','social_interaction':'3','anxiety_level':'8','satisfaction':'4'}
r=client.post('/assessment',data=form); assert r.status_code==200 and b'wellbeing' in r.data.lower()
# Cleanup
u=database.find_user(email); database.delete_all_user_data(u['id'])
with database.conn() as c:c.execute('DELETE FROM users WHERE id=?',(u['id'],))
print('PASS: Flask public routes, auth, protected routes, assessment, and cleanup')
