from datetime import datetime
from app.database import db


class DatasetFile(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  dataset_id = db.Column(
      db.Integer, db.ForeignKey('dataset.id'), nullable=False)
  # patients, taxonomy, bracken
  file_type = db.Column(db.String(50), nullable=False)
  show_filename = db.Column(db.String(255), nullable=False)
  file_path = db.Column(db.String(500), nullable=False)  # Full path to the file
  file_size = db.Column(db.BigInteger, nullable=False)
  upload_method = db.Column(db.String(50), default='file')  # file
  uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
  modified_at = db.Column(
      db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  # Processing status fields
  # 'pending', 'processing', 'completed', 'failed'
  processing_status = db.Column(db.String(50), default='pending')
  processing_started_at = db.Column(db.DateTime)
  processing_completed_at = db.Column(db.DateTime)
  processing_error = db.Column(db.Text)
  processed_file_path = db.Column(db.String(500))  # Path to processed file
  processing_summary = db.Column(db.Text)  # JSON string with processing summary

  # Cure status fields
  # 'not_cured', 'curing', 'cured', 'failed'
  cure_status = db.Column(db.String(50), default='not_cured')
  # 'pending', 'ok', 'warnings', 'errors'
  cure_validation_status = db.Column(db.String(50), default='pending')
  cured_at = db.Column(db.DateTime)

  def __repr__(self):
    return f'<DatasetFile {self.show_filename}>'

  def update_modified_timestamp(self):
    self.modified_at = datetime.utcnow()
