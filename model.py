from pathlib import Path
import numpy as np,pandas as pd,joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix
ROOT=Path(__file__).parent;DATA=ROOT/'data/wellbeing_dataset.csv';MODEL=ROOT/'models/wellbeing_model.pkl'
FEATURES=['age','sleep_hours','sleep_quality','stress_level','mood_rating','physical_activity','exercise_frequency','screen_time','study_hours','social_interaction','anxiety_level','satisfaction'];NUM=[x for x in FEATURES if x!='physical_activity'];CAT=['physical_activity']
def make_dataset(n=1200,seed=42):
 r=np.random.default_rng(seed);d=pd.DataFrame({'age':r.integers(17,65,n),'sleep_hours':np.clip(r.normal(6.8,1.4,n),3,10).round(1),'sleep_quality':r.integers(1,11,n),'stress_level':r.integers(1,11,n),'mood_rating':r.integers(1,11,n),'physical_activity':r.choice(['Low','Moderate','High'],n,p=[.35,.45,.2]),'exercise_frequency':r.integers(0,8,n),'screen_time':np.clip(r.normal(5.5,2,n),1,14).round(1),'study_hours':np.clip(r.normal(7,2,n),1,14).round(1),'social_interaction':r.integers(1,11,n),'anxiety_level':r.integers(1,11,n),'satisfaction':r.integers(1,11,n)});s=2.4*d.stress_level-1.9*d.mood_rating-1.7*d.sleep_hours-1.4*d.sleep_quality+1.1*d.anxiety_level-.65*d.exercise_frequency-.45*d.social_interaction-.35*d.satisfaction+.35*d.screen_time;d['risk']=pd.cut(s,[-np.inf,10,24,np.inf],labels=['Low Risk','Moderate Risk','High Risk']).astype(str);DATA.parent.mkdir(exist_ok=True);d.to_csv(DATA,index=False);return d
def load_data():return pd.read_csv(DATA) if DATA.exists() else make_dataset()
def train():
 d=load_data();X=d[FEATURES];y=d.risk;xt,xv,yt,yv=train_test_split(X,y,test_size=.2,random_state=42,stratify=y);pre=ColumnTransformer([('num',SimpleImputer(strategy='median'),NUM),('cat',Pipeline([('imp',SimpleImputer(strategy='most_frequent')),('oh',OneHotEncoder(handle_unknown='ignore'))]),CAT)]);p=Pipeline([('preprocess',pre),('classifier',RandomForestClassifier(n_estimators=180,max_depth=10,random_state=42,class_weight='balanced'))]);p.fit(xt,yt);pr=p.predict(xv);m={'accuracy':accuracy_score(yv,pr),'precision':precision_score(yv,pr,average='weighted',zero_division=0),'recall':recall_score(yv,pr,average='weighted',zero_division=0),'f1':f1_score(yv,pr,average='weighted',zero_division=0),'confusion':confusion_matrix(yv,pr,labels=p.classes_),'classes':list(p.classes_)};MODEL.parent.mkdir(exist_ok=True);joblib.dump({'pipeline':p,'metrics':m,'features':FEATURES,'data':d},MODEL);return {'pipeline':p,'metrics':m,'features':FEATURES,'data':d}
def load_model():
    if MODEL.exists():
        try:
            bundle=joblib.load(MODEL)
            # Force a lightweight compatibility check before using the cached artifact.
            if 'pipeline' in bundle and hasattr(bundle['pipeline'],'predict'): return bundle
        except Exception:
            # Pickle files can be incompatible across Python/scikit-learn versions.
            # Retraining from the local educational CSV is the safe recovery path.
            pass
    return train()
def predict(v):
 b=load_model();x=pd.DataFrame([v])[FEATURES];r=b['pipeline'].predict(x)[0];q=b['pipeline'].predict_proba(x)[0];return r,float(max(q)),dict(zip(b['pipeline'].classes_,q))
def importances(b=None):
 b=b or load_model();pre=b['pipeline'].named_steps['preprocess'];names=NUM+list(pre.named_transformers_['cat'].named_steps['oh'].get_feature_names_out(CAT));s=pd.Series(b['pipeline'].named_steps['classifier'].feature_importances_,index=names);return s.groupby(s.index.str.replace('physical_activity_','physical_activity')).sum().sort_values(ascending=False)

def explain(v,b=None):
 """Educational local explanation using directional contribution rules plus global importance."""
 imp=importances(b);out=[]
 for feature,importance in imp.items():
  value=v.get(feature)
  if feature in {'stress_level','anxiety_level','screen_time','study_hours'}: direction='increases concern when high' if value is not None and value>=7 else 'currently not elevated'
  elif feature in {'sleep_hours','sleep_quality','mood_rating','exercise_frequency','social_interaction','satisfaction'}: direction='may be protective when higher' if value is not None and value>=7 else 'currently below a high-support range'
  else: direction=f'current value: {value}'
  out.append({'feature':feature,'importance':float(importance),'value':value,'interpretation':direction})
 return out

def outliers(v,b=None):
 d=(b or load_model())['data'];warnings=[]
 for col in NUM:
  if col not in v:continue
  lo,hi=d[col].quantile(.01),d[col].quantile(.99)
  if v[col]<lo or v[col]>hi:warnings.append(f'{col.replace("_"," ").title()} is outside the common range of this educational dataset ({lo:.1f}–{hi:.1f}).')
 return warnings
