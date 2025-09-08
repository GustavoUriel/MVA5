from datetime import datetime
from app.database import db


class Dataset(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(200), nullable=False)
  description = db.Column(db.Text)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(
      db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

  # Dataset metadata
  # draft, processing, ready, error
  status = db.Column(db.String(50), default='draft')
  file_count = db.Column(db.Integer, default=0)
  total_size = db.Column(db.BigInteger, default=0)  # in bytes

  # Table file status
  patients_file_uploaded = db.Column(db.Boolean, default=False)
  taxonomy_file_uploaded = db.Column(db.Boolean, default=False)
  bracken_file_uploaded = db.Column(db.Boolean, default=False)

  # Relationships
  files = db.relationship('DatasetFile', backref='dataset',
                          lazy=True, cascade='all, delete-orphan')

  def __repr__(self):
    return f'<Dataset {self.name}>'

  @property
  def completion_percentage(self):
    total_files = 3  # patients, taxonomy, bracken
    uploaded = sum([self.patients_file_uploaded,
                   self.taxonomy_file_uploaded, self.bracken_file_uploaded])
    return int((uploaded / total_files) * 100)

  @property
  def is_complete(self):
    return self.patients_file_uploaded and self.taxonomy_file_uploaded and self.bracken_file_uploaded
