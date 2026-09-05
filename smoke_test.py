import database, auth, model
email='test-viva@example.com'
if not database.find_user(email):
    ok,msg=auth.register('Test User',email,'Password1','Password1'); assert ok,msg
u,msg=auth.login(email,'Password1'); assert u,msg
v={'age':21,'sleep_hours':5.0,'sleep_quality':4,'stress_level':8,'mood_rating':4,'physical_activity':'Low','exercise_frequency':1,'screen_time':9.0,'study_hours':8.0,'social_interaction':3,'anxiety_level':8,'satisfaction':4}
r,p,probs=model.predict(v); assert r in {'Low Risk','Moderate Risk','High Risk'} and 0<=p<=1
before=len(database.get_predictions(u['id']));database.save_prediction(u['id'],v,r,p);assert len(database.get_predictions(u['id']))==before+1
assert auth.login(email,'wrong')[0] is None
print('PASS: syntax, auth, invalid login, model prediction, persistence, user-scoped history')
print('risk=',r,'confidence=',round(p,3),'probabilities=',{k:round(x,3) for k,x in probs.items()})
