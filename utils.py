def risk_color(r):
    return {'Low Risk':'#15803d','Moderate Risk':'#b45309','High Risk':'#b91c1c'}.get(r,'#475569')

def recommendations(v):
    result=[]
    if v.get('sleep_hours',7)<6: result.append('Consider a consistent sleep schedule and a wind-down routine.')
    if v.get('stress_level',5)>=7: result.append('Consider short breaks, slow breathing, or planning smaller tasks.')
    if v.get('exercise_frequency',2)<2 or v.get('physical_activity')=='Low': result.append('Consider gradually increasing regular physical activity.')
    if v.get('screen_time',5)>=8: result.append('Consider regular screen breaks and a screen-free period before sleep.')
    if v.get('social_interaction',5)<=3: result.append('Consider checking in with a trusted friend, family member, or mentor.')
    return result or ['Keep noticing which routines support your wellbeing.']

def safe_float(value,default=0.0):
    try:return float(value)
    except (TypeError,ValueError):return default

def safe_int(value,default=0):
    try:return int(value)
    except (TypeError,ValueError):return default
