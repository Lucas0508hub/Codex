import os
import shutil
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import webrtcvad

from .database import Base, engine
from . import models, schemas, auth, vad, utils

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [os.getenv('FRONTEND_URL', 'http://localhost:3000')]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/register', response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail='Username taken')
    db_user = models.User(username=user.username, hashed_password=auth.get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post('/login', response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    access_token = auth.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get('/me', response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post('/upload', response_model=schemas.AudioJobOut)
def upload_audio(language: str = Form(...), file: UploadFile = File(...), db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    upload_dir = 'uploads'
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    audio, sr = vad.read_wave(file_path)
    frames = list(vad.frame_generator(30, audio, sr))
    VAD = webrtcvad.Vad(3)
    segments = list(vad.vad_collector(sr, 30, 300, VAD, frames))

    job = models.AudioJob(user_id=current_user.id, language=language, filename=file.filename)
    db.add(job)
    db.commit()
    db.refresh(job)
    for start, end in segments:
        seg = models.Segment(job_id=job.id, start=start, end=end, transcript='')
        db.add(seg)
    db.commit()
    db.refresh(job)
    return schemas.AudioJobOut(
        id=job.id,
        language=job.language,
        filename=job.filename,
        segments=[schemas.SegmentOut(id=s.id, start=s.start, end=s.end, transcript=s.transcript) for s in job.segments]
    )

@app.patch('/segments/{job_id}/{seg_id}', response_model=schemas.SegmentOut)
def update_segment(job_id: int, seg_id: int, upd: schemas.SegmentUpdate, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    seg = db.query(models.Segment).join(models.AudioJob).filter(models.AudioJob.id==job_id, models.Segment.id==seg_id, models.AudioJob.user_id==current_user.id).first()
    if not seg:
        raise HTTPException(status_code=404, detail='Segment not found')
    if upd.start is not None:
        seg.start = upd.start
    if upd.end is not None:
        seg.end = upd.end
    if upd.transcript is not None:
        seg.transcript = upd.transcript
    db.commit()
    db.refresh(seg)
    return seg

@app.post('/export/{job_id}')
def export(job_id: int, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    job = db.query(models.AudioJob).filter_by(id=job_id, user_id=current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    wav_path = os.path.join('uploads', job.filename)
    segs = db.query(models.Segment).filter_by(job_id=job.id).all()
    with utils.TemporaryDirectory() as tmpdir:
        segments_data = [(s.id, s.start, s.end, s.transcript) for s in segs]
        utils.export_segments(wav_path, segments_data, tmpdir)
        zip_name = shutil.make_archive(f'{job.filename}_export', 'zip', tmpdir)
    return FileResponse(zip_name, filename=os.path.basename(zip_name))
