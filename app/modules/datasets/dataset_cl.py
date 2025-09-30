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
    # Check actual files in database instead of relying on boolean flags
    total_file_types = 3  # patients, taxonomy, bracken
    
    # Get unique file types that have at least one file
    uploaded_file_types = set()
    for file in self.files:
      if file.file_type in ['patients', 'taxonomy', 'bracken']:
        uploaded_file_types.add(file.file_type)
    
    # Each file type represents 33.33% (100/3)
    percentage_per_type = 100 / total_file_types
    completion = len(uploaded_file_types) * percentage_per_type
    
    return int(completion)

  @property
  def is_complete(self):
    # Check if all three required file types have at least one file
    required_file_types = {'patients', 'taxonomy', 'bracken'}
    uploaded_file_types = set()
    
    for file in self.files:
      if file.file_type in required_file_types:
        uploaded_file_types.add(file.file_type)
    
    return len(uploaded_file_types) == len(required_file_types)

  def update_file_status_flags(self):
    """Update the boolean flags based on actual files in the database"""
    # Reset all flags
    self.patients_file_uploaded = False
    self.taxonomy_file_uploaded = False
    self.bracken_file_uploaded = False
    
    # Set flags based on actual files
    for file in self.files:
      if file.file_type == 'patients':
        self.patients_file_uploaded = True
      elif file.file_type == 'taxonomy':
        self.taxonomy_file_uploaded = True
      elif file.file_type == 'bracken':
        self.bracken_file_uploaded = True
