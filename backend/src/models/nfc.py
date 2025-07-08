from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class NfcRecord(db.Model):
    __tablename__ = 'nfc_records'
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.String(80), nullable=False)
    nfc_uid = db.Column(db.String(80), nullable=False, unique=True)
    last_location_lat = db.Column(db.Float)
    last_location_lon = db.Column(db.Float)
    last_location_time = db.Column(db.DateTime)
    affection_level = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    conversations = db.relationship('NfcConversation', backref='nfc_record', lazy=True)

class NfcConversation(db.Model):
    __tablename__ = 'nfc_conversations'
    id = db.Column(db.Integer, primary_key=True)
    nfc_record_id = db.Column(db.Integer, db.ForeignKey('nfc_records.id'), nullable=False)
    message = db.Column(db.Text)
    sender = db.Column(db.String(20))  # 'user' or 'character'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) 