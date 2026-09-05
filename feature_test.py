import database, auth, model
email='feature-test@example.com'
if database.find_user(email):
    uid=database.find_user(email)['id']
else:
    uid=database.create_user('Feature Test',email,auth.hash_password('Password1'))
v={'age':21,'sleep_hours':5.0,'sleep_quality':4,'stress_level':8,'mood_rating':4,'physical_activity':'Low','exercise_frequency':1,'screen_time':9.0,'study_hours':8.0,'social_interaction':3,'anxiety_level':8,'satisfaction':4}
r,p,_=model.predict(v);assert r in {'Low Risk','Moderate Risk','High Risk'}
assert model.explain(v) and isinstance(model.outliers(v),list)
database.add_journal(uid,'test',5);database.add_checkin(uid,5,5,5,5,'test');database.save_habit(uid,'2099-01-01',[1,0,1,0,1])
assert database.get_journals(uid) and database.get_checkins(uid) and database.get_habits(uid)
database.delete_all_user_data(uid)
with database.conn() as c:c.execute('DELETE FROM users WHERE id=?',(uid,))
print('PASS: new tables, explainability, outlier analysis, journal, check-in, habits')
