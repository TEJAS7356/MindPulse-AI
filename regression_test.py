import model
values={'age':21,'sleep_hours':7.0,'sleep_quality':6,'stress_level':5,'mood_rating':6,'physical_activity':'Moderate','exercise_frequency':2,'screen_time':5.0,'study_hours':7.0,'social_interaction':5,'anxiety_level':5,'satisfaction':6}
risk,confidence,probabilities=model.predict(values)
assert risk in {'Low Risk','Moderate Risk','High Risk'}
assert 0 <= confidence <= 1
assert set(probabilities)
print('Assessment mapping test passed:', risk, confidence)
