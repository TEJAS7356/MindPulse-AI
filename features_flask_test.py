from app import app
import database
app.config['TESTING']=True
c=app.test_client();email='all-features@example.com';u=database.find_user(email)
if u:
 database.delete_all_user_data(u['id'])
 with database.conn() as db: db.execute('DELETE FROM users WHERE id=?',(u['id'],))
c.post('/register',data={'name':'All Features','email':email,'password':'Password1','confirm_password':'Password1'})
c.post('/login',data={'email':email,'password':'Password1'})
# seed prediction for report/explainability
form={'age':'21','sleep_hours':'7','sleep_quality':'7','stress_level':'4','mood_rating':'7','physical_activity':'Moderate','exercise_frequency':'3','screen_time':'5','study_hours':'7','social_interaction':'6','anxiety_level':'4','satisfaction':'7'}
assert c.post('/assessment',data=form).status_code==200
for path in ['/report','/report?download=1','/explainability','/profile','/journal','/check-ins','/habits','/breathing','/goals']:
 assert c.get(path).status_code==200,path
assert c.post('/journal',data={'entry':'A useful reflection','mood':'7'}).status_code==200
assert c.post('/check-ins',data={'mood':'7','energy':'6','stress':'4','sleep_quality':'7','note':'Okay'}).status_code==200
assert c.post('/habits',data={'habit_date':'2026-09-05','sleep_goal':'1','exercise':'1','water':'1'}).status_code==200
assert c.post('/goals',data={'title':'Walk outside','target':'3','unit':'times'}).status_code==200
goals=database.get_goals(database.find_user(email)['id']);assert goals
assert c.post(f"/goals/{goals[0]['id']}/progress",json={'progress':50}).status_code==200
assert c.get('/admin-analytics').status_code in (200,403)
u=database.find_user(email);database.delete_all_user_data(u['id'])
with database.conn() as db:db.execute('DELETE FROM users WHERE id=?',(u['id'],))
print('PASS: report, explainability, profile, journal, check-ins, habits, breathing, goals, and admin routes')
