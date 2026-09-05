import os
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
import database, auth, model, ai_service, email_service, face_emotion

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-only-change-me')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

FEATURES = model.FEATURES

def current_user():
    uid = session.get('user_id')
    if not uid: return None
    u = database.get_user_by_id(uid)
    return dict(u) if u else None

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash('Please log in to continue.', 'info')
            return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return wrapped

def user_rows(): return [dict(x) for x in database.get_predictions(session['user_id'])]
def input_from_form(source):
    def number(key, cast=float, default=0):
        try: return cast(source.get(key, default))
        except (TypeError, ValueError): return default
    return {'age':number('age',int,21),'sleep_hours':number('sleep_hours'),'sleep_quality':number('sleep_quality',int,6),'stress_level':number('stress_level',int,5),'mood_rating':number('mood_rating',int,6),'physical_activity':source.get('physical_activity','Moderate'),'exercise_frequency':number('exercise_frequency',int,2),'screen_time':number('screen_time'),'study_hours':number('study_hours'),'social_interaction':number('social_interaction',int,5),'anxiety_level':number('anxiety_level',int,5),'satisfaction':number('satisfaction',int,6)}
def prediction_payload(values):
    risk, probability, probabilities = model.predict(values)
    factors = model.explain(values)
    return {'risk':risk,'probability':probability,'probabilities':probabilities,'factors':factors,'recommendations':__import__('utils').recommendations(values),'outliers':model.outliers(values),'values':values}

def context(**extra): return {'user': current_user(), 'theme': session.get('theme','light'), **extra}

@app.context_processor
def inject_globals(): return {'logged_in': bool(current_user()), 'app_name':'MindPulse AI'}

@app.route('/')
def index(): return render_template('index.html', **context())

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        ok, msg = auth.register(request.form.get('name',''), request.form.get('email',''), request.form.get('password',''), request.form.get('confirm_password',''))
        flash(msg, 'success' if ok else 'error')
        if ok: return redirect(url_for('login'))
    return render_template('register.html', **context())

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user, msg = auth.login(request.form.get('email',''), request.form.get('password',''))
        if user:
            session.clear(); session['user_id']=user['id']; session['theme']=request.form.get('theme','light'); flash('Welcome back, '+user['name']+'.','success'); return redirect(request.args.get('next') or url_for('dashboard'))
        flash(msg,'error')
    return render_template('login.html', **context())

@app.route('/logout')
def logout(): session.clear(); flash('You have been logged out.','info'); return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET','POST'])
def forgot_password():
    if request.method=='POST':
        user, otp = auth.begin_reset(request.form.get('email',''))
        if user:
            ok,msg=email_service.send_otp(user['email'],otp); flash(msg,'success' if ok else 'error')
            if ok: session['reset_uid']=user['id']; return redirect(url_for('verify_otp'))
        else: flash('If that account exists, an OTP has been sent.','info')
    return render_template('forgot_password.html', **context())

@app.route('/verify-otp', methods=['GET','POST'])
def verify_otp():
    if not session.get('reset_uid'): return redirect(url_for('forgot_password'))
    if request.method=='POST':
        ok,msg=auth.verify_otp(session['reset_uid'],request.form.get('otp',''))
        if ok: session['otp_verified']=True; return redirect(url_for('reset_password'))
        flash(msg,'error')
    return render_template('verify_otp.html', **context())

@app.route('/reset-password', methods=['GET','POST'])
def reset_password():
    if not session.get('reset_uid') or not session.get('otp_verified'): return redirect(url_for('forgot_password'))
    if request.method=='POST':
        ok,msg=auth.reset_password(session['reset_uid'],request.form.get('password',''))
        flash(msg,'success' if ok else 'error')
        if ok: session.pop('reset_uid',None);session.pop('otp_verified',None);return redirect(url_for('login'))
    return render_template('reset_password.html', **context())

@app.route('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html', **context(rows=user_rows()[:5], latest=user_rows()[0] if user_rows() else None))

@app.route('/assessment', methods=['GET','POST'])
@login_required
def assessment():
    result=None
    if request.method=='POST':
        values=input_from_form(request.form); result=prediction_payload(values);database.save_prediction(session['user_id'],values,result['risk'],result['probability']);session['latest']=result;flash('Assessment saved to your private history.','success')
        return render_template('prediction.html', **context(result=result))
    return render_template('assessment.html', **context())

@app.route('/prediction')
@login_required
def prediction(): return render_template('prediction.html', **context(result=session.get('latest')))

@app.route('/what-if', methods=['GET','POST'])
@login_required
def what_if():
    rows=user_rows(); base=rows[0] if rows else None; result=None
    if request.method=='POST' and base:
        values={k:base[k] for k in FEATURES};values.update(input_from_form(request.form));result={'current':prediction_payload({k:base[k] for k in FEATURES}),'simulated':prediction_payload(values)}
    return render_template('what_if.html', **context(base=base,result=result))

@app.route('/history')
@login_required
def history(): return render_template('history.html', **context(rows=user_rows()))

@app.route('/trends')
@login_required
def trends():
    rows=user_rows(); direction=None
    if len(rows)>=3:
        score={'Low Risk':1,'Moderate Risk':2,'High Risk':3}; ordered=list(reversed(rows)); delta=score[ordered[-1]['predicted_risk']]-score[ordered[0]['predicted_risk']];direction='Improving' if delta<0 else 'Declining' if delta>0 else 'Stable'
    return render_template('trends.html', **context(rows=rows,direction=direction))

@app.route('/analytics')
@login_required
def analytics():
    rows=user_rows(); d=pd.DataFrame(rows); metrics=model.load_model()['metrics']; summary={'assessments':len(rows),'average_sleep':round(float(d.sleep_hours.mean()),1) if not d.empty else 0,'average_stress':round(float(d.stress_level.mean()),1) if not d.empty else 0,'average_exercise':round(float(d.exercise_frequency.mean()),1) if not d.empty else 0}
    return render_template('analytics.html', **context(summary=summary, rows=rows, metrics=metrics))

@app.route('/ml-concepts')
@login_required
def ml_concepts(): return render_template('ml_concepts.html', **context(bundle=model.load_model()))

@app.route('/facial-expression')
@login_required
def facial_expression(): return render_template('facial_expression.html', **context())

@app.route('/api/analyze-face', methods=['POST'])
@login_required
def analyze_face():
    image=request.files.get('image'); result,error=face_emotion.analyze(image)
    if error:
        code='NO_FACE' if error.startswith('No face detected') else 'ANALYSIS_ERROR'
        return jsonify({'ok':False,'code':code,'error':error}),400
    return jsonify({'ok':True,'expression':result['expression'],'confidence':result['confidence'],'message':face_emotion.supportive(result['expression'])})

@app.route('/ai-companion', methods=['GET','POST'])
@login_required
def ai_companion():
    reply=None;message=''
    if request.method=='POST':
        message=request.form.get('message','').strip(); latest=session.get('latest',{});reply=ai_service.reply(message,f"Latest wellbeing estimate: {latest.get('risk','not available')}; expression: {session.get('expression','not available')}") if message else None
    return render_template('ai_companion.html', **context(reply=reply,message=message))

@app.route('/about')
def about(): return render_template('about.html', **context())

@app.route('/report')
@login_required
def report():
    rows=user_rows(); latest=rows[0] if rows else None
    if not latest: return redirect(url_for('assessment'))
    result=prediction_payload({k:latest[k] for k in FEATURES})
    html=render_template('report.html', **context(result=result, rows=rows))
    if request.args.get('download')=='1':
        from flask import Response
        return Response(html, mimetype='text/html', headers={'Content-Disposition':'attachment; filename=mindpulse-report.html'})
    return render_template('report.html', **context(result=result, rows=rows))

@app.route('/explainability')
@login_required
def explainability():
    return render_template('explainability.html', **context(factors=model.explain({k:user_rows()[0][k] for k in FEATURES}) if user_rows() else {}))

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method=='POST':
        name=request.form.get('name','').strip()
        if name: database.update_user_name(session['user_id'],name); flash('Profile updated.','success')
        else: flash('Please enter a name.','error')
        return redirect(url_for('profile'))
    return render_template('profile.html', **context())

@app.route('/journal', methods=['GET','POST'])
@login_required
def journal():
    if request.method=='POST':
        entry=request.form.get('entry','').strip(); mood=int(request.form.get('mood',5))
        if entry: database.add_journal(session['user_id'],entry,mood); flash('Journal entry saved privately.','success')
    return render_template('journal.html', **context(entries=[dict(x) for x in database.get_journals(session['user_id'])]))

@app.route('/check-ins', methods=['GET','POST'])
@login_required
def checkins():
    if request.method=='POST':
        n=lambda k:int(request.form.get(k,5));database.add_checkin(session['user_id'],n('mood'),n('energy'),n('stress'),n('sleep_quality'),request.form.get('note','').strip());flash('Daily check-in saved.','success')
    return render_template('checkins.html', **context(entries=[dict(x) for x in database.get_checkins(session['user_id'])]))

@app.route('/habits', methods=['GET','POST'])
@login_required
def habits():
    if request.method=='POST':
        vals=[int(request.form.get(k,0)) for k in ('sleep_goal','exercise','water','screen_break','breathing')];database.save_habit(session['user_id'],request.form.get('habit_date',datetime.now().date().isoformat()),vals);flash('Habit progress saved.','success')
    return render_template('habits.html', **context(entries=[dict(x) for x in database.get_habits(session['user_id'])]))

@app.route('/breathing')
@login_required
def breathing(): return render_template('breathing.html', **context())

@app.route('/goals', methods=['GET','POST'])
@login_required
def goals():
    if request.method=='POST':
        title=request.form.get('title','').strip();target=int(request.form.get('target',1));unit=request.form.get('unit','times')
        if title: database.add_goal(session['user_id'],title,target,unit);flash('Weekly goal created.','success')
    return render_template('goals.html', **context(entries=[dict(x) for x in database.get_goals(session['user_id'])]))

@app.route('/goals/<int:goal_id>/progress', methods=['POST'])
@login_required
def goal_progress(goal_id): database.update_goal(session['user_id'],goal_id,int((request.get_json() or {}).get('progress',0)));return jsonify({'ok':True})

@app.route('/admin-analytics')
@login_required
def admin_analytics():
    if current_user()['email'].lower()!=os.getenv('ADMIN_EMAIL','').lower(): return render_template('about.html', **context(),),403
    rows=[dict(x) for x in database.get_all_predictions()]
    return render_template('admin_analytics.html', **context(rows=rows, users=len({r['user_id'] for r in rows})))
@app.route('/theme', methods=['POST'])
def theme(): session['theme']=request.json.get('theme','light');return jsonify({'ok':True})
@app.route('/api/predict', methods=['POST'])
@login_required
def api_predict(): return jsonify(prediction_payload(request.get_json() or {}))
@app.route('/api/delete/<int:prediction_id>', methods=['POST'])
@login_required
def delete_prediction(prediction_id): database.delete_prediction(session['user_id'],prediction_id);return jsonify({'ok':True})
@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data=request.get_json() or {};return jsonify({'reply':ai_service.reply(data.get('message',''),'')})

if __name__=='__main__':
    database.init_db();app.run(host='0.0.0.0',port=int(os.getenv('PORT',5000)),debug=os.getenv('FLASK_DEBUG')=='1')
