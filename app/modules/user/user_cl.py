from flask_login import UserMixin
from datetime import datetime
from app.database import db


class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(100), unique=True, nullable=False)
  name = db.Column(db.String(100), nullable=False)
  google_id = db.Column(db.String(100), unique=True, nullable=False)
  profile_pic = db.Column(db.String(200))
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  last_login = db.Column(db.DateTime)

  # Relationship with datasets
  datasets = db.relationship(
      'Dataset', backref='owner', lazy=True, cascade='all, delete-orphan')

  def __repr__(self):
    return f'<User {self.email}>'
