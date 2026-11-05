from datetime import datetime, date, timedelta
from typing import Optional
import io, os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from sqlalchemy import create_engine, String, Integer, DateTime, Date, ForeignKey, Text, Float, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./tutorly.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
elif DATABASE_URL.startswith('postgresql://') and '+psycopg' not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
SECRET = os.getenv('SECRET_KEY', 'local-development-change-me')
ALGO = 'HS256'
pwd = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
oauth = OAuth2PasswordBearer(tokenUrl='/auth/token')

class Base(DeclarativeBase): pass
class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True)
    name: Mapped[str]=mapped_column(String(120))
    password_hash: Mapped[str]=mapped_column(String(255))
    plan: Mapped[str]=mapped_column(String(20), default='Free')
class Student(Base):
    __tablename__='students'
    id: Mapped[int]=mapped_column(primary_key=True)
    owner_id: Mapped[int]=mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    name: Mapped[str]=mapped_column(String(120)); grade: Mapped[str]=mapped_column(String(40), default='')
    subject: Mapped[str]=mapped_column(String(80), default='Математика'); email: Mapped[str]=mapped_column(String(255), default='')
    phone: Mapped[str]=mapped_column(String(40), default=''); notes: Mapped[str]=mapped_column(Text, default='')
    status: Mapped[str]=mapped_column(String(30), default='Активен'); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class Task(Base):
    __tablename__='tasks'
    id: Mapped[int]=mapped_column(primary_key=True); owner_id: Mapped[int]=mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    title: Mapped[str]=mapped_column(String(220)); topic: Mapped[str]=mapped_column(String(100), default='Алгебра')
    grade: Mapped[str]=mapped_column(String(30), default=''); difficulty: Mapped[str]=mapped_column(String(30), default='Средняя')
    body: Mapped[str]=mapped_column(Text); answer: Mapped[str]=mapped_column(Text, default='')
class Lesson(Base):
    __tablename__='lessons'
    id: Mapped[int]=mapped_column(primary_key=True); owner_id: Mapped[int]=mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    student_id: Mapped[int]=mapped_column(ForeignKey('students.id', ondelete='CASCADE')); title: Mapped[str]=mapped_column(String(180))
    starts_at: Mapped[datetime]=mapped_column(DateTime); duration: Mapped[int]=mapped_column(Integer, default=60)
    status: Mapped[str]=mapped_column(String(30), default='Запланировано'); notes: Mapped[str]=mapped_column(Text, default='')
class Homework(Base):
    __tablename__='homeworks'
    id: Mapped[int]=mapped_column(primary_key=True); owner_id: Mapped[int]=mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    student_id: Mapped[int]=mapped_column(ForeignKey('students.id', ondelete='CASCADE')); title: Mapped[str]=mapped_column(String(180))
    due_date: Mapped[Optional[date]]=mapped_column(Date, nullable=True); task_ids: Mapped[str]=mapped_column(Text, default='')
    status: Mapped[str]=mapped_column(String(30), default='Выдано'); score: Mapped[Optional[float]]=mapped_column(Float, nullable=True)
Base.metadata.create_all(engine)

def db():
    s=SessionLocal()
    try: yield s
    finally: s.close()
class UserOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; email:str; name:str; plan:str
class Register(BaseModel): name:str=Field(min_length=2,max_length=120); email:EmailStr; password:str=Field(min_length=8,max_length=128)
class StudentIn(BaseModel): name:str=Field(min_length=1,max_length=120); grade:str=''; subject:str='Математика'; email:str=''; phone:str=''; notes:str=''; status:str='Активен'
class TaskIn(BaseModel): title:str; topic:str='Алгебра'; grade:str=''; difficulty:str='Средняя'; body:str; answer:str=''
class LessonIn(BaseModel): student_id:int; title:str; starts_at:datetime; duration:int=60; status:str='Запланировано'; notes:str=''
class HomeworkIn(BaseModel): student_id:int; title:str; due_date:Optional[date]=None; task_ids:list[int]=Field(default_factory=list); status:str='Выдано'
class HomeworkUpdate(BaseModel): status:Optional[str]=None; score:Optional[float]=None

def token_for(user):
    return jwt.encode({'sub':str(user.id),'exp':datetime.utcnow()+timedelta(days=14)}, SECRET, algorithm=ALGO)
def current_user(token:str=Depends(oauth), s:Session=Depends(db)):
    try: uid=int(jwt.decode(token, SECRET, algorithms=[ALGO])['sub'])
    except (JWTError, ValueError, KeyError): raise HTTPException(401,'Сессия истекла. Войдите снова.')
    user=s.get(User,uid)
    if not user: raise HTTPException(401,'Пользователь не найден')
    return user

def owned_student(s, uid, sid):
    x=s.query(Student).filter_by(id=sid, owner_id=uid).first()
    if not x: raise HTTPException(404,'Ученик не найден')
    return x

app=FastAPI(title='Tutorly API', version='2.0.0', description='Рабочее пространство репетитора')
origins=[x.strip() for x in os.getenv('CORS_ORIGINS','*').split(',') if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=['*'], allow_headers=['*'])
@app.get('/health')
def health(): return {'status':'ok','product':'Tutorly','version':'2.0.0'}
@app.post('/auth/register')
def register(d:Register,s:Session=Depends(db)):
    email=d.email.lower().strip()
    if s.query(User).filter(func.lower(User.email)==email).first(): raise HTTPException(409,'Этот email уже зарегистрирован')
    u=User(email=email,name=d.name.strip(),password_hash=pwd.hash(d.password)); s.add(u); s.commit(); s.refresh(u)
    starter=[('Квадратные уравнения','Алгебра','9 класс','Средняя','Решите уравнение: x² − 5x + 6 = 0. Найдите корни и проверьте подстановкой.','x = 2; x = 3'),('Теорема Пифагора','Геометрия','8 класс','Лёгкая','Катеты прямоугольного треугольника равны 6 см и 8 см. Найдите гипотенузу.','10 см'),('Производная функции','Анализ','11 класс','Сложная','Найдите производную функции f(x) = 3x³ − 4x² + 7x − 2.','9x² − 8x + 7'),('Проценты и пропорции','Арифметика','7 класс','Лёгкая','Цена товара 2400 рублей. После скидки 15% найдите новую цену.','2040 рублей')]
    for title,topic,grade,difficulty,body,answer in starter: s.add(Task(owner_id=u.id,title=title,topic=topic,grade=grade,difficulty=difficulty,body=body,answer=answer))
    s.commit()
    return {'access_token':token_for(u),'token_type':'bearer','user':UserOut.model_validate(u).model_dump()}
@app.post('/auth/token')
def login(form:OAuth2PasswordRequestForm=Depends(),s:Session=Depends(db)):
    u=s.query(User).filter(func.lower(User.email)==form.username.lower().strip()).first()
    if not u or not pwd.verify(form.password,u.password_hash): raise HTTPException(401,'Неверный email или пароль')
    return {'access_token':token_for(u),'token_type':'bearer','user':UserOut.model_validate(u).model_dump()}
@app.get('/auth/me',response_model=UserOut)
def me(u:User=Depends(current_user)): return u
@app.get('/students')
def get_students(s:Session=Depends(db),u:User=Depends(current_user)): return s.query(Student).filter_by(owner_id=u.id).order_by(Student.name).all()
@app.post('/students')
def add_student(d:StudentIn,s:Session=Depends(db),u:User=Depends(current_user)):
    if u.plan=='Free' and s.query(Student).filter_by(owner_id=u.id).count()>=3: raise HTTPException(403,'В бесплатном тарифе доступно до 3 учеников')
    x=Student(owner_id=u.id,**d.model_dump()); s.add(x); s.commit(); s.refresh(x); return x
@app.put('/students/{sid}')
def edit_student(sid:int,d:StudentIn,s:Session=Depends(db),u:User=Depends(current_user)):
    x=owned_student(s,u.id,sid)
    for k,v in d.model_dump().items(): setattr(x,k,v)
    s.commit(); s.refresh(x); return x
@app.delete('/students/{sid}')
def delete_student(sid:int,s:Session=Depends(db),u:User=Depends(current_user)):
    x=owned_student(s,u.id,sid)
    s.query(Lesson).filter_by(owner_id=u.id,student_id=sid).delete(synchronize_session=False)
    s.query(Homework).filter_by(owner_id=u.id,student_id=sid).delete(synchronize_session=False)
    s.delete(x); s.commit(); return {'ok':True}
@app.get('/tasks')
def get_tasks(q:str='',s:Session=Depends(db),u:User=Depends(current_user)):
    query=s.query(Task).filter_by(owner_id=u.id)
    if q: query=query.filter(Task.title.ilike(f'%{q}%') | Task.body.ilike(f'%{q}%'))
    return query.order_by(Task.id.desc()).all()
@app.post('/tasks')
def add_task(d:TaskIn,s:Session=Depends(db),u:User=Depends(current_user)):
    x=Task(owner_id=u.id,**d.model_dump()); s.add(x); s.commit(); s.refresh(x); return x
@app.put('/tasks/{tid}')
def edit_task(tid:int,d:TaskIn,s:Session=Depends(db),u:User=Depends(current_user)):
    x=s.query(Task).filter_by(id=tid,owner_id=u.id).first()
    if not x: raise HTTPException(404,'Задание не найдено')
    for k,v in d.model_dump().items(): setattr(x,k,v)
    s.commit(); s.refresh(x); return x
@app.delete('/tasks/{tid}')
def delete_task(tid:int,s:Session=Depends(db),u:User=Depends(current_user)):
    x=s.query(Task).filter_by(id=tid,owner_id=u.id).first()
    if not x: raise HTTPException(404,'Задание не найдено')
    s.delete(x); s.commit(); return {'ok':True}
@app.get('/lessons')
def get_lessons(s:Session=Depends(db),u:User=Depends(current_user)): return s.query(Lesson).filter_by(owner_id=u.id).order_by(Lesson.starts_at).all()
@app.post('/lessons')
def add_lesson(d:LessonIn,s:Session=Depends(db),u:User=Depends(current_user)):
    owned_student(s,u.id,d.student_id); x=Lesson(owner_id=u.id,**d.model_dump()); s.add(x); s.commit(); s.refresh(x); return x
@app.put('/lessons/{lid}')
def update_lesson(lid:int,d:LessonIn,s:Session=Depends(db),u:User=Depends(current_user)):
    x=s.query(Lesson).filter_by(id=lid,owner_id=u.id).first()
    if not x: raise HTTPException(404,'Занятие не найдено')
    owned_student(s,u.id,d.student_id)
    for k,v in d.model_dump().items(): setattr(x,k,v)
    s.commit(); s.refresh(x); return x
@app.delete('/lessons/{lid}')
def delete_lesson(lid:int,s:Session=Depends(db),u:User=Depends(current_user)):
    x=s.query(Lesson).filter_by(id=lid,owner_id=u.id).first()
    if not x: raise HTTPException(404,'Занятие не найдено')
    s.delete(x); s.commit(); return {'ok':True}
@app.get('/homeworks')
def get_homeworks(s:Session=Depends(db),u:User=Depends(current_user)): return s.query(Homework).filter_by(owner_id=u.id).order_by(Homework.id.desc()).all()
@app.post('/homeworks')
def add_homework(d:HomeworkIn,s:Session=Depends(db),u:User=Depends(current_user)):
    owned_student(s,u.id,d.student_id)
    ids=list(dict.fromkeys(d.task_ids))
    if ids and s.query(Task).filter(Task.owner_id==u.id,Task.id.in_(ids)).count()!=len(ids): raise HTTPException(400,'Некоторые задания не найдены')
    x=Homework(owner_id=u.id,student_id=d.student_id,title=d.title,due_date=d.due_date,task_ids=','.join(map(str,ids)),status=d.status); s.add(x); s.commit(); s.refresh(x); return x
@app.patch('/homeworks/{hid}')
def update_homework(hid:int,d:HomeworkUpdate,s:Session=Depends(db),u:User=Depends(current_user)):
    x=s.query(Homework).filter_by(id=hid,owner_id=u.id).first()
    if not x: raise HTTPException(404,'Домашняя работа не найдена')
    if d.status is not None: x.status=d.status
    if d.score is not None: x.score=max(0,min(100,d.score))
    s.commit(); s.refresh(x); return x
@app.delete('/homeworks/{hid}')
def delete_homework(hid:int,s:Session=Depends(db),u:User=Depends(current_user)):
    x=s.query(Homework).filter_by(id=hid,owner_id=u.id).first()
    if not x: raise HTTPException(404,'Домашняя работа не найдена')
    s.delete(x); s.commit(); return {'ok':True}
@app.get('/analytics')
def analytics(s:Session=Depends(db),u:User=Depends(current_user)):
    students=s.query(Student).filter_by(owner_id=u.id).count(); tasks=s.query(Task).filter_by(owner_id=u.id).count(); lessons=s.query(Lesson).filter_by(owner_id=u.id).count(); hw=s.query(Homework).filter_by(owner_id=u.id).all()
    scores=[x.score for x in hw if x.score is not None]
    return {'students':students,'tasks':tasks,'lessons':lessons,'homeworks':len(hw),'average_score':round(sum(scores)/len(scores),1) if scores else 0,'completion_rate':round(sum(1 for x in hw if x.status=='Проверено')/len(hw)*100) if hw else 0}
@app.get('/homeworks/{hid}/pdf')
def homework_pdf(hid:int,s:Session=Depends(db),u:User=Depends(current_user)):
    h=s.query(Homework).filter_by(id=hid,owner_id=u.id).first()
    if not h: raise HTTPException(404,'Домашняя работа не найдена')
    student=owned_student(s,u.id,h.student_id); ids=[int(x) for x in h.task_ids.split(',') if x]
    tasks=s.query(Task).filter(Task.owner_id==u.id,Task.id.in_(ids)).all() if ids else []
    buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=A4); w,ht=A4
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    if os.path.exists(font):
        if 'DejaVu' not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont('DejaVu',font))
        fn='DejaVu'
    else: fn='Helvetica'
    c.setFont(fn,16); c.drawString(48,ht-55,h.title[:80]); c.setFont(fn,10); c.drawString(48,ht-78,f'Ученик: {student.name}'); c.drawString(48,ht-94,f'Срок: {h.due_date or "не указан"}')
    y=ht-130
    for i,t in enumerate(tasks,1):
        if y<90: c.showPage(); y=ht-60
        c.setFont(fn,11); c.drawString(48,y,f'{i}. {t.title[:100]}'); y-=18; c.setFont(fn,10)
        for line in (t.body or '').splitlines():
            if y<60: c.showPage(); y=ht-60; c.setFont(fn,10)
            c.drawString(58,y,line[:105]); y-=14
        y-=18
    c.save(); buf.seek(0)
    return StreamingResponse(buf,media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename=homework-{hid}.pdf'})
