import hashlib,hmac,secrets
from datetime import datetime,timezone,timedelta
import database
def hash_password(p):
 s=secrets.token_bytes(16); d=hashlib.pbkdf2_hmac('sha256',p.encode(),s,120000); return f'pbkdf2_sha256$120000${s.hex()}${d.hex()}'
def verify_password(p,stored):
 try:
  _,it,s,d=stored.split('$'); return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),int(it)).hex(),d)
 except:return False
def valid_password(p):return len(p)>=8 and any(x.isalpha() for x in p) and any(x.isdigit() for x in p)
def register(name,email,password,confirm):
 if not name.strip() or '@' not in email:return False,'Enter a valid name and email.'
 if password!=confirm:return False,'Passwords do not match.'
 if not valid_password(password):return False,'Password must be at least 8 characters and contain a letter and number.'
 if database.find_user(email):return False,'An account with this email already exists.'
 try:database.create_user(name,email,hash_password(password));return True,'Account created. You can log in.'
 except:return False,'Could not create account.'
def login(email,password):
 u=database.find_user(email); return (dict(u), 'Welcome back.') if u and verify_password(password,u['password_hash']) else (None,'Invalid email or password.')
def create_otp():return f'{secrets.randbelow(1000000):06d}'
def otp_hash(o):return hashlib.sha256(o.encode()).hexdigest()
def expiry():return (datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat()
def expired(x):return datetime.now(timezone.utc)>=datetime.fromisoformat(x)
def begin_reset(email):
 u=database.find_user(email); 
 if not u:return None,None
 o=create_otp();database.save_reset(u['id'],otp_hash(o),expiry(),datetime.now(timezone.utc).isoformat());return dict(u),o
def verify_otp(uid,entered):
 r=database.get_reset(uid)
 if not r:return False,'Request a new OTP.'
 if r['attempts']>=5:return False,'Too many incorrect attempts.'
 if expired(r['expires_at']):return False,'OTP expired.'
 if not hmac.compare_digest(otp_hash(entered.strip()),r['otp_hash']):database.increment_attempt(r['id']);return False,'Incorrect OTP.'
 return True,'OTP verified.'
def reset_password(uid,p):
 if not valid_password(p):return False,'Password must be at least 8 characters and contain a letter and number.'
 database.update_password(uid,hash_password(p));r=database.get_reset(uid)
 if r:database.use_reset(r['id'])
 return True,'Password updated.'
