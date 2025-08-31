"""
Database Models
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
import uuid


class User(UserMixin, db.Model):
  """User model for authentication"""
  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), unique=True, nullable=False, index=True)
  name = db.Column(db.String(100), nullable=False)
  google_id = db.Column(db.String(50), unique=True, nullable=True)
  profile_picture = db.Column(db.String(200), nullable=True)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  last_login = db.Column(db.DateTime, nullable=True)
  is_active = db.Column(db.Boolean, default=True)

  # Relationships
  datasets = db.relationship(
      'Dataset', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
  logs = db.relationship('UserLog', backref='user',
                         lazy='dynamic', cascade='all, delete-orphan')

  def __init__(self, email, name, google_id=None, profile_picture=None):
    self.email = email
    self.name = name
    self.google_id = google_id
    self.profile_picture = profile_picture

  def __repr__(self):
    return f'<User {self.email}>'

  def to_dict(self):
    return {
        'id': self.id,
        'email': self.email,
        'name': self.name,
        'created_at': self.created_at.isoformat() if self.created_at else None,
        'last_login': self.last_login.isoformat() if self.last_login else None,
        'dataset_count': self.datasets.count()
    }


class Dataset(db.Model):
  """Dataset model for microbiome data"""
  __tablename__ = 'datasets'

  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(db.String(36), unique=True, nullable=False,
                   default=lambda: str(uuid.uuid4()))
  name = db.Column(db.String(200), nullable=False)
  description = db.Column(db.Text, nullable=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(
      db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  file_path = db.Column(db.String(500), nullable=True)
  file_size = db.Column(db.Integer, nullable=True)
  # created, processing, ready, error
  status = db.Column(db.String(50), default='created')
  # Renamed from 'metadata' to avoid SQLAlchemy conflict
  metadata_info = db.Column(db.JSON, nullable=True)

  # Relationships
  analysis_jobs = db.relationship(
      'AnalysisJob', backref='dataset', lazy='dynamic', cascade='all, delete-orphan')

  def __init__(self, name, user_id, description=None, dataset_uuid=None):
    self.name = name
    self.user_id = user_id
    self.description = description
    self.uuid = dataset_uuid or str(uuid.uuid4())

  def __repr__(self):
    return f'<Dataset {self.name}>'

  def to_dict(self):
    return {
        'id': self.id,
        'uuid': self.uuid,
        'name': self.name,
        'description': self.description,
        'created_at': self.created_at.isoformat() if self.created_at else None,
        'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        'status': self.status,
        'file_size': self.file_size,
        'metadata': self.metadata_info
    }


class AnalysisJob(db.Model):
  """Analysis job model for background processing"""
  __tablename__ = 'analysis_jobs'

  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(db.String(36), unique=True, nullable=False,
                   default=lambda: str(uuid.uuid4()))
  dataset_id = db.Column(
      db.Integer, db.ForeignKey('datasets.id'), nullable=False)
  job_type = db.Column(db.String(100), nullable=False)
  # pending, running, completed, failed
  status = db.Column(db.String(50), default='pending')
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  started_at = db.Column(db.DateTime, nullable=True)
  completed_at = db.Column(db.DateTime, nullable=True)
  celery_task_id = db.Column(db.String(50), nullable=True)
  parameters = db.Column(db.JSON, nullable=True)
  results = db.Column(db.JSON, nullable=True)
  error_message = db.Column(db.Text, nullable=True)

  def __init__(self, dataset_id, job_type, status='pending', celery_task_id=None, started_at=None):
    self.dataset_id = dataset_id
    self.job_type = job_type
    self.status = status
    self.celery_task_id = celery_task_id
    self.started_at = started_at

  def __repr__(self):
    return f'<AnalysisJob {self.job_type}>'

  def to_dict(self):
    return {
        'id': self.id,
        'uuid': self.uuid,
        'job_type': self.job_type,
        'status': self.status,
        'created_at': self.created_at.isoformat() if self.created_at else None,
        'started_at': self.started_at.isoformat() if self.started_at else None,
        'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        'parameters': self.parameters,
        'results': self.results,
        'error_message': self.error_message
    }


class UserLog(db.Model):
  """User activity logging model"""
  __tablename__ = 'user_logs'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  action = db.Column(db.String(100), nullable=False)
  details = db.Column(db.JSON, nullable=True)
  ip_address = db.Column(db.String(45), nullable=True)
  user_agent = db.Column(db.String(500), nullable=True)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)
  session_id = db.Column(db.String(100), nullable=True)

  def __init__(self, user_id, action, details=None, ip_address=None, user_agent=None, session_id=None):
    self.user_id = user_id
    self.action = action
    self.details = details
    self.ip_address = ip_address
    self.user_agent = user_agent
    self.session_id = session_id

  def __repr__(self):
    return f'<UserLog {self.action} by User {self.user_id}>'

  def to_dict(self):
    return {
        'id': self.id,
        'action': self.action,
        'details': self.details,
        'ip_address': self.ip_address,
        'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        'session_id': self.session_id
    }
