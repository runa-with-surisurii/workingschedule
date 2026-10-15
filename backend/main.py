from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import date, datetime, timedelta
import sqlite3, secrets, hashlib, os

DB = Path(__file__).with_name('workingschedule.db')
app = FastAPI(title='WorkSchedule Pro API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
TOKENS = {}

def connect():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def pw_hash(p, salt=None):
    salt=salt or secrets.token_hex(16)
    return salt+'$'+hashlib.pbkdf2_hmac('sha256',p.encode(),salt.encode(),150000).hex()

def pw_ok(p, stored):
    salt, expected=stored.split('$',1)
    return secrets.compare_digest(pw_hash(p,salt).split('$',1)[1],expected)

def q(sql,args=()):
    with connect() as c: return [dict(r) for r in c.execute(sql,args).fetchall()]
def init():
    with connect() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS employees(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,department TEXT NOT NULL,position TEXT NOT NULL,hourly_rate REAL NOT NULL DEFAULT 0,status TEXT NOT NULL DEFAULT 'Active');
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL,employee_id INTEGER);
        CREATE TABLE IF NOT EXISTS shifts(id INTEGER PRIMARY KEY,employee_id INTEGER NOT NULL REFERENCES employees(id),shift_date TEXT NOT NULL,start_time TEXT NOT NULL,end_time TEXT NOT NULL,shift_type TEXT NOT NULL,location TEXT NOT NULL DEFAULT 'Main Branch',status TEXT NOT NULL DEFAULT 'Scheduled',notes TEXT NOT NULL DEFAULT '');
        CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY,shift_id INTEGER UNIQUE NOT NULL REFERENCES shifts(id),clock_in TEXT,clock_out TEXT,status TEXT NOT NULL DEFAULT 'Not checked in');
        CREATE TABLE IF NOT EXISTS leave_requests(id INTEGER PRIMARY KEY,employee_id INTEGER NOT NULL REFERENCES employees(id),start_date TEXT NOT NULL,end_date TEXT NOT NULL,leave_type TEXT NOT NULL,reason TEXT NOT NULL DEFAULT '',status TEXT NOT NULL DEFAULT 'Pending',reviewed_by TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE INDEX IF NOT EXISTS ix_shifts_date ON shifts(shift_date);''')
        if c.execute('SELECT COUNT(*) FROM employees').fetchone()[0]==0:
            people=[('Aye Chan','aye@example.com','Operations','Supervisor',18),('Min Khant','min@example.com','Sales','Associate',14),('Su Mon','su@example.com','Support','Specialist',15),('Htet Naing','htet@example.com','Operations','Team Member',13),('May Thiri','may@example.com','Finance','Coordinator',17)]
            for p in people: c.execute('INSERT INTO employees(name,email,department,position,hourly_rate) VALUES(?,?,?,?,?)',p)
            ids=[r[0] for r in c.execute('SELECT id FROM employees').fetchall()]
            for day in range(7):
                d=(date.today()+timedelta(days=day)).isoformat()
                for j,eid in enumerate(ids[:3]):
                    start=['08:00','12:00','16:00'][j]; end=['16:00','20:00','23:00'][j]
                    cur=c.execute('INSERT INTO shifts(employee_id,shift_date,start_time,end_time,shift_type) VALUES(?,?,?,?,?)',(eid,d,start,end,['Morning','Afternoon','Night'][j]))
                    c.execute('INSERT INTO attendance(shift_id) VALUES(?)',(cur.lastrowid,))
            for name,email,password,role,eid in [('Demo Admin','admin@workingschedule.local','Admin123!','admin',None),('Demo Manager','manager@workingschedule.local','Manager123!','manager',ids[0]),('Demo Employee','employee@workingschedule.local','Employee123!','employee',ids[1])]:
                c.execute('INSERT OR IGNORE INTO users(name,email,password_hash,role,employee_id) VALUES(?,?,?,?,?)',(name,email,pw_hash(password),role,eid))
@app.on_event('startup')
def startup(): init()
class Login(BaseModel): email:str; password:str
class Employee(BaseModel): name:str=Field(min_length=2); email:str; department:str='Operations'; position:str='Team Member'; hourly_rate:float=Field(default=0,ge=0); status:str='Active'
class Shift(BaseModel): employee_id:int; shift_date:date; start_time:str; end_time:str; shift_type:str='Morning'; location:str='Main Branch'; notes:str=''
class Leave(BaseModel): employee_id:int; start_date:date; end_date:date; leave_type:str='Annual'; reason:str=''
class Decision(BaseModel): status:str

def auth(authorization:str|None=Header(default=None)):
    token=authorization.replace('Bearer ','',1) if authorization else ''
    if token not in TOKENS: raise HTTPException(401,'Please sign in')
    return TOKENS[token]
def roles(*allowed):
    def check(user=Depends(auth)):
        if user['role'] not in allowed: raise HTTPException(403,'Permission denied')
        return user
    return check

def hours(a,b):
    try: x=datetime.strptime(a,'%H:%M'); y=datetime.strptime(b,'%H:%M')
    except ValueError: raise HTTPException(400,'Use HH:MM for shift times')
    if y<=x: raise HTTPException(400,'End time must be later than start time')
    return (y-x).total_seconds()/3600
@app.get('/api/health')
def health(): return {'status':'ok','service':'WorkSchedule Pro'}
@app.post('/api/auth/login')
def login(data:Login):
    user=next(iter(q('SELECT * FROM users WHERE lower(email)=lower(?)',(data.email,))),None)
    if not user or not pw_ok(data.password,user['password_hash']): raise HTTPException(401,'Invalid email or password')
    token=secrets.token_urlsafe(32); safe={k:user[k] for k in ('id','name','email','role','employee_id')}; TOKENS[token]=safe
    return {'token':token,'user':safe}
@app.get('/api/auth/me')
def me(user=Depends(auth)): return user
@app.get('/api/employees')
def employees(qry:str='',user=Depends(auth)):
    return q('SELECT * FROM employees WHERE name LIKE ? OR email LIKE ? OR department LIKE ? ORDER BY name',(f'%{qry}%',f'%{qry}%',f'%{qry}%'))
@app.post('/api/employees')
def add_employee(data:Employee,user=Depends(roles('admin','manager'))):
    try:
        with connect() as c:
            cur=c.execute('INSERT INTO employees(name,email,department,position,hourly_rate,status) VALUES(?,?,?,?,?,?)',(data.name,data.email,data.department,data.position,data.hourly_rate,data.status))
            return dict(c.execute('SELECT * FROM employees WHERE id=?',(cur.lastrowid,)).fetchone())
    except sqlite3.IntegrityError: raise HTTPException(409,'Email already exists')
@app.get('/api/shifts')
def shifts(start:str='',end:str='',employee_id:int|None=None,user=Depends(auth)):
    sql='SELECT s.*,e.name employee_name,e.department FROM shifts s JOIN employees e ON e.id=s.employee_id WHERE s.status != "Cancelled"'; p=[]
    if start: sql+=' AND s.shift_date>=?'; p.append(start)
    if end: sql+=' AND s.shift_date<=?'; p.append(end)
    if employee_id: sql+=' AND s.employee_id=?'; p.append(employee_id)
    if user['role']=='employee' and user.get('employee_id'): sql+=' AND s.employee_id=?'; p.append(user['employee_id'])
    return q(sql+' ORDER BY s.shift_date,s.start_time',p)
@app.post('/api/shifts')
def add_shift(data:Shift,user=Depends(roles('admin','manager'))):
    if hours(data.start_time,data.end_time)>16: raise HTTPException(400,'Shift cannot exceed 16 hours')
    overlap=q("SELECT id FROM shifts WHERE employee_id=? AND shift_date=? AND status!='Cancelled' AND start_time<? AND end_time>?",(data.employee_id,str(data.shift_date),data.end_time,data.start_time))
    if overlap: raise HTTPException(409,'Scheduling conflict: overlapping shift exists')
    with connect() as c:
        cur=c.execute('INSERT INTO shifts(employee_id,shift_date,start_time,end_time,shift_type,location,notes) VALUES(?,?,?,?,?,?,?)',(data.employee_id,str(data.shift_date),data.start_time,data.end_time,data.shift_type,data.location,data.notes))
        c.execute('INSERT INTO attendance(shift_id) VALUES(?)',(cur.lastrowid,))
        return dict(c.execute('SELECT s.*,e.name employee_name FROM shifts s JOIN employees e ON e.id=s.employee_id WHERE s.id=?',(cur.lastrowid,)).fetchone())
@app.delete('/api/shifts/{sid}')
def cancel_shift(sid:int,user=Depends(roles('admin','manager'))):
    with connect() as c:
        cur=c.execute("UPDATE shifts SET status='Cancelled' WHERE id=?",(sid,))
        if not cur.rowcount: raise HTTPException(404,'Shift not found')
    return {'message':'Shift cancelled'}
@app.get('/api/attendance')
def attendance(user=Depends(auth)):
    return q('SELECT a.*,s.shift_date,s.start_time,s.end_time,s.shift_type,e.name employee_name,s.employee_id FROM attendance a JOIN shifts s ON s.id=a.shift_id JOIN employees e ON e.id=s.employee_id ORDER BY s.shift_date DESC LIMIT 200')
@app.post('/api/attendance/{sid}/{action}')
def mark_attendance(sid:int,action:str,user=Depends(auth)):
    if action not in ('clock-in','clock-out'): raise HTTPException(400,'Unknown attendance action')
    shift=next(iter(q('SELECT * FROM shifts WHERE id=?',(sid,))),None)
    if not shift: raise HTTPException(404,'Shift not found')
    if user['role']=='employee' and user.get('employee_id')!=shift['employee_id']: raise HTTPException(403,'You can only update your own attendance')
    now=datetime.now().isoformat(timespec='minutes')
    with connect() as c:
        c.execute('INSERT OR IGNORE INTO attendance(shift_id) VALUES(?)',(sid,))
        field='clock_in' if action=='clock-in' else 'clock_out'
        att=c.execute('SELECT * FROM attendance WHERE shift_id=?',(sid,)).fetchone()
        if action=='clock-out' and not att['clock_in']: raise HTTPException(400,'Clock in first')
        if att[field]: raise HTTPException(409,'This action has already been recorded')
        c.execute('UPDATE attendance SET '+field+'=?,status=? WHERE shift_id=?',(now,'Checked in' if action=='clock-in' else 'Completed',sid))
        return dict(c.execute('SELECT * FROM attendance WHERE shift_id=?',(sid,)).fetchone())
@app.get('/api/leaves')
def leaves(user=Depends(auth)):
    return q('SELECT l.*,e.name employee_name,e.department FROM leave_requests l JOIN employees e ON e.id=l.employee_id ORDER BY l.created_at DESC')
@app.post('/api/leaves')
def request_leave(data:Leave,user=Depends(auth)):
    if data.end_date<data.start_date: raise HTTPException(400,'End date must not precede start date')
    if user['role']=='employee' and user.get('employee_id')!=data.employee_id: raise HTTPException(403,'You can only request your own leave')
    with connect() as c:
        cur=c.execute('INSERT INTO leave_requests(employee_id,start_date,end_date,leave_type,reason) VALUES(?,?,?,?,?)',(data.employee_id,str(data.start_date),str(data.end_date),data.leave_type,data.reason))
        return dict(c.execute('SELECT l.*,e.name employee_name FROM leave_requests l JOIN employees e ON e.id=l.employee_id WHERE l.id=?',(cur.lastrowid,)).fetchone())
@app.patch('/api/leaves/{lid}')
def review_leave(lid:int,data:Decision,user=Depends(roles('admin','manager'))):
    if data.status not in ('Approved','Rejected'): raise HTTPException(400,'Choose Approved or Rejected')
    with connect() as c:
        cur=c.execute('UPDATE leave_requests SET status=?,reviewed_by=? WHERE id=?',(data.status,user['name'],lid))
        if not cur.rowcount: raise HTTPException(404,'Request not found')
        return {'message':'Leave request updated','status':data.status}
@app.get('/api/analytics/summary')
def summary(user=Depends(auth)):
    today=date.today().isoformat(); month=date.today().strftime('%Y-%m')
    people=q("SELECT COUNT(*) n FROM employees WHERE status='Active'")[0]['n']; shifts=q("SELECT COUNT(*) n FROM shifts WHERE shift_date LIKE ? AND status!='Cancelled'",(month+'%',))[0]['n']
    pending=q("SELECT COUNT(*) n FROM leave_requests WHERE status='Pending'")[0]['n']; complete=q('SELECT COUNT(*) n FROM attendance a JOIN shifts s ON s.id=a.shift_id WHERE s.shift_date=? AND a.status="Completed"',(today,))[0]['n']
    total=round(sum(hours(s['start_time'],s['end_time']) for s in q("SELECT start_time,end_time FROM shifts WHERE shift_date LIKE ? AND status!='Cancelled'",(month+'%',))),1)
    departments=q('SELECT department,COUNT(*) count FROM employees WHERE status="Active" GROUP BY department ORDER BY count DESC')
    return {'active_employees':people,'monthly_shifts':shifts,'pending_leaves':pending,'completed_today':complete,'monthly_scheduled_hours':total,'departments':departments}
