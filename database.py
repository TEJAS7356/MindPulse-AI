from pathlib import Path
import sqlite3
from datetime import datetime, timezone
DB_PATH=Path(__file__).parent/'wellbeing.db'
def conn():
 c=sqlite3.connect(DB_PATH,check_same_thread=False); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
def now(): return datetime.now(timezone.utc).isoformat()
def init_db():
 with conn() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL COLLATE NOCASE,password_hash TEXT NOT NULL,created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS predictions(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,timestamp TEXT NOT NULL,age INTEGER,sleep_hours REAL,sleep_quality INTEGER,stress_level INTEGER,mood_rating INTEGER,physical_activity TEXT,exercise_frequency INTEGER,screen_time REAL,study_hours REAL,social_interaction INTEGER,anxiety_level INTEGER,satisfaction INTEGER,predicted_risk TEXT NOT NULL,probability REAL NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE); CREATE TABLE IF NOT EXISTS password_resets(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,otp_hash TEXT NOT NULL,expires_at TEXT NOT NULL,attempts INTEGER DEFAULT 0,last_sent_at TEXT NOT NULL,used INTEGER DEFAULT 0,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE); CREATE TABLE IF NOT EXISTS journals(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,entry TEXT NOT NULL,mood INTEGER,created_at TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE); CREATE TABLE IF NOT EXISTS checkins(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,mood INTEGER,energy INTEGER,stress INTEGER,sleep_quality INTEGER,note TEXT,created_at TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE); CREATE TABLE IF NOT EXISTS habits(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,habit_date TEXT NOT NULL,sleep_goal INTEGER,exercise INTEGER,water INTEGER,screen_break INTEGER,breathing INTEGER,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);''')
def find_user(email):
 with conn() as c:return c.execute('SELECT * FROM users WHERE email=?',(email.strip().lower(),)).fetchone()
def get_user_by_id(uid):
 with conn() as c:return c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
def create_user(name,email,password_hash):
 with conn() as c:return c.execute('INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)',(name.strip(),email.strip().lower(),password_hash,now())).lastrowid
def save_prediction(uid,v,risk,prob):
 keys=['age','sleep_hours','sleep_quality','stress_level','mood_rating','physical_activity','exercise_frequency','screen_time','study_hours','social_interaction','anxiety_level','satisfaction']
 with conn() as c:c.execute('INSERT INTO predictions(user_id,timestamp,age,sleep_hours,sleep_quality,stress_level,mood_rating,physical_activity,exercise_frequency,screen_time,study_hours,social_interaction,anxiety_level,satisfaction,predicted_risk,probability) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(uid,now(),*[v[k] for k in keys],risk,prob))
def get_predictions(uid):
 with conn() as c:return c.execute('SELECT * FROM predictions WHERE user_id=? ORDER BY timestamp DESC',(uid,)).fetchall()
def delete_prediction(uid,pid):
 with conn() as c:c.execute('DELETE FROM predictions WHERE id=? AND user_id=?',(pid,uid))
def save_reset(uid,oh,exp,sent):
 with conn() as c:c.execute('UPDATE password_resets SET used=1 WHERE user_id=?',(uid,)); c.execute('INSERT INTO password_resets(user_id,otp_hash,expires_at,last_sent_at) VALUES(?,?,?,?)',(uid,oh,exp,sent))
def get_reset(uid):
 with conn() as c:return c.execute('SELECT * FROM password_resets WHERE user_id=? AND used=0 ORDER BY id DESC LIMIT 1',(uid,)).fetchone()
def increment_attempt(rid):
 with conn() as c:c.execute('UPDATE password_resets SET attempts=attempts+1 WHERE id=?',(rid,))
def use_reset(rid):
 with conn() as c:c.execute('UPDATE password_resets SET used=1 WHERE id=?',(rid,))
def update_password(uid,h):
 with conn() as c:c.execute('UPDATE users SET password_hash=? WHERE id=?',(h,uid))
def get_all_predictions():
 with conn() as c:return c.execute('SELECT * FROM predictions ORDER BY timestamp').fetchall()

def add_journal(uid,entry,mood):
 with conn() as c:c.execute('INSERT INTO journals(user_id,entry,mood,created_at) VALUES(?,?,?,?)',(uid,entry,mood,now()))
def get_journals(uid):
 with conn() as c:return c.execute('SELECT * FROM journals WHERE user_id=? ORDER BY created_at DESC',(uid,)).fetchall()
def add_checkin(uid,mood,energy,stress,sleep_quality,note):
 with conn() as c:c.execute('INSERT INTO checkins(user_id,mood,energy,stress,sleep_quality,note,created_at) VALUES(?,?,?,?,?,?,?)',(uid,mood,energy,stress,sleep_quality,note,now()))
def get_checkins(uid):
 with conn() as c:return c.execute('SELECT * FROM checkins WHERE user_id=? ORDER BY created_at',(uid,)).fetchall()
def save_habit(uid,day,values):
 with conn() as c:
  c.execute('DELETE FROM habits WHERE user_id=? AND habit_date=?',(uid,day));c.execute('INSERT INTO habits(user_id,habit_date,sleep_goal,exercise,water,screen_break,breathing) VALUES(?,?,?,?,?,?,?)',(uid,day,*values))
def get_habits(uid):
 with conn() as c:return c.execute('SELECT * FROM habits WHERE user_id=? ORDER BY habit_date DESC',(uid,)).fetchall()
def update_user_name(uid,name):
 with conn() as c:c.execute('UPDATE users SET name=? WHERE id=?',(name.strip(),uid))
def delete_all_user_data(uid):
 with conn() as c:
  for table in ('predictions','journals','checkins','habits'):c.execute(f'DELETE FROM {table} WHERE user_id=?',(uid,))
init_db()


def add_goal(uid,title,target,unit):
 with conn() as c:return c.execute('INSERT INTO goals(user_id,title,target,unit,progress,created_at) VALUES(?,?,?,?,0,?)',(uid,title,target,unit,now())).lastrowid

def get_goals(uid):
 with conn() as c:return c.execute('SELECT * FROM goals WHERE user_id=? ORDER BY created_at DESC',(uid,)).fetchall()

def update_goal(uid,gid,progress):
 with conn() as c:c.execute('UPDATE goals SET progress=? WHERE id=? AND user_id=?',(max(0,min(100,int(progress))),gid,uid))

def delete_journal(uid,jid):
 with conn() as c:c.execute('DELETE FROM journals WHERE id=? AND user_id=?',(jid,uid))

def delete_checkin(uid,cid):
 with conn() as c:c.execute('DELETE FROM checkins WHERE id=? AND user_id=?',(cid,uid))


def ensure_extra_tables():
 with conn() as c:c.execute('CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,title TEXT NOT NULL,target INTEGER NOT NULL,unit TEXT NOT NULL,progress INTEGER DEFAULT 0,created_at TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)')
ensure_extra_tables()
