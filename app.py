"""
Microbiome Analysis Flask Web Application
Main application entry point
"""

from flask_login import UserMixin
import os
import uuid
import time
import json
import shutil
from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify, g, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from datetime import datetime
# import redis  # Commented out since we're using filesystem sessions
from celery import Celery
from dotenv import load_dotenv
from scripts.logging_config import setup_logging, ErrorLogger, log_user_action, log_performance, PerformanceTracker
from scripts.smart_table import build_schema, build_table_data, save_table
# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)


# Configuration
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///microbiome_analysis.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'microbiome:'
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get(
    'MAX_CONTENT_LENGTH', 100 * 1024 * 1024))  # 100MB

# Google OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.environ.get(
    'GOOGLE_CLIENT_ID', 'dummy-client-id')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get(
    'GOOGLE_CLIENT_SECRET', 'dummy-client-secret')
app.config['GOOGLE_REDIRECT_URI'] = os.environ.get(
    'GOOGLE_REDIRECT_URI', 'http://127.0.0.1:5005/auth/login/authorized')

# Celery Configuration
app.config['CELERY_BROKER_URL'] = os.environ.get(
    'CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get(
    'CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
Session(app)
oauth = OAuth(app)

# Configure Google OAuth
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Initialize Celery


def make_celery(app):
  celery = Celery(
      app.import_name,
      backend=app.config['CELERY_RESULT_BACKEND'],
      broker=app.config['CELERY_BROKER_URL']
  )
  celery.conf.update(app.config)

  class ContextTask(celery.Task):
    """Make celery tasks work with Flask app context."""

    def __call__(self, *args, **kwargs):
      with app.app_context():
        return self.run(*args, **kwargs)

  celery.Task = ContextTask
  return celery


celery = make_celery(app)

# User loader for Flask-Login


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


def get_user_folder(user_id):
  """Get the user folder path for a specific user"""
  if user_id:
    # Get user email for folder naming
    user = User.query.get(user_id)
    if user:
      # Create safe folder name from email (replace special chars)
      safe_email = user.email.replace(
          '@', '_at_').replace('.', '_dot_').replace('-', '_')
      user_dir = os.path.join(app.instance_path, 'users', safe_email)
      os.makedirs(user_dir, exist_ok=True)
      return user_dir
  return None


def get_user_upload_folder(user_id):
  """Get the upload folder path for a specific user"""
  if user_id:
    user_dir = get_user_folder(user_id)
    if user_dir:
      upload_dir = os.path.join(user_dir, 'uploads')
      os.makedirs(upload_dir, exist_ok=True)
      return upload_dir
  # Fallback to global upload folder for anonymous users
  return app.config['UPLOAD_FOLDER']


def get_user_log_folder(user_id):
  """Get the log folder path for a specific user"""
  if user_id:
    user_dir = get_user_folder(user_id)
    if user_dir:
      log_dir = os.path.join(user_dir, 'logs')
      os.makedirs(log_dir, exist_ok=True)
      return log_dir
  return None


# Models


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
  def is_complete(self):
    """Check if all required files are uploaded"""
    return (self.patients_file_uploaded and
            self.taxonomy_file_uploaded and
            self.bracken_file_uploaded)

  @property
  def completion_percentage(self):
    """Calculate completion percentage based on uploaded files"""
    uploaded = sum([self.patients_file_uploaded,
                   self.taxonomy_file_uploaded,
                   self.bracken_file_uploaded])
    return int((uploaded / 3) * 100)


class DatasetFile(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  dataset_id = db.Column(
      db.Integer, db.ForeignKey('dataset.id'), nullable=False)
  # patients, taxonomy, bracken
  file_type = db.Column(db.String(50), nullable=False)
  filename = db.Column(db.String(255), nullable=False)
  original_filename = db.Column(db.String(255), nullable=False)
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
    return f'<DatasetFile {self.original_filename} ({self.file_type})>'

  def update_modified_timestamp(self):
    """Update the modified_at timestamp to current time"""
    self.modified_at = datetime.utcnow()
    return self

# Routes


@app.route('/')
def index():
  """Welcome page"""
  if current_user.is_authenticated:
    return redirect(url_for('dashboard'))
  return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
  """User dashboard showing datasets"""
  datasets = Dataset.query.filter_by(
      user_id=current_user.id).order_by(Dataset.updated_at.desc()).all()

  # Calculate total size of all datasets
  total_size = sum(dataset.total_size or 0 for dataset in datasets)

  return render_template('dashboard.html', datasets=datasets, user=current_user, total_size=total_size)


@app.route('/dataset/new', methods=['GET', 'POST'])
@login_required
def new_dataset():
  """Create a new dataset"""
  if request.method == 'POST':
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
      flash('Dataset name is required.', 'error')
      return render_template('new_dataset.html')

    # Check if dataset name already exists for this user
    existing = Dataset.query.filter_by(
        user_id=current_user.id, name=name).first()
    if existing:
      flash('A dataset with this name already exists.', 'error')
      return render_template('new_dataset.html')

    # Create new dataset
    dataset = Dataset(
        name=name,
        description=description,
        user_id=current_user.id
    )

    try:
      with PerformanceTracker("dataset_creation", f"Dataset: {name}"):
        db.session.add(dataset)
        db.session.commit()

      log_user_action("dataset_created", f"Dataset: {name}", success=True)
      flash(f'Dataset "{name}" created successfully!', 'success')
      return redirect(url_for('dashboard'))
    except Exception as e:
      db.session.rollback()
      ErrorLogger.log_exception(
          e,
          context="Creating new dataset",
          user_action=f"User trying to create dataset '{name}'",
          extra_data={
              'dataset_name': name,
              'dataset_description': description,
              'user_id': current_user.id if current_user.is_authenticated else None
          }
      )
      log_user_action("dataset_creation_failed",
                      f"Dataset: {name}", success=False)
      flash('Error creating dataset. Please try again.', 'error')
      app.logger.error(f'Error creating dataset: {e}')

  return render_template('new_dataset.html')


@app.route('/dataset/<int:dataset_id>')
@login_required
def view_dataset(dataset_id):
  """View a specific dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  return render_template('dataset.html', dataset=dataset)


@app.route('/dataset/<int:dataset_id>/upload', methods=['POST'])
@login_required
def upload_dataset_file(dataset_id):
  """Upload a file to a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    file_type = request.form.get('file_type')
    upload_method = request.form.get('upload_method', 'file')

    if file_type not in ['patients', 'taxonomy', 'bracken']:
      raise ValueError("Invalid file type")

    if upload_method != 'file':
      raise ValueError("Invalid upload method")

    # Handle file upload
    if 'file' not in request.files:
      raise ValueError("No file provided")

    file = request.files['file']
    if file.filename == '':
      raise ValueError("No file selected")

    # Get file extension (no validation)
    if file.filename:
      file_ext = os.path.splitext(file.filename)[1].lower()
    else:
      file_ext = '.csv'  # Default extension

    # Save file
    timestamp = datetime.utcnow().strftime('%y%m%d-%H%M%S')
    filename = f"{dataset.id}_{file_type}_{timestamp}{file_ext}"
    file_path = os.path.join(
        get_user_upload_folder(current_user.id), filename)
    file.save(file_path)

    # Get file size
    file_size = os.path.getsize(file_path)

    # Create database record
    dataset_file = DatasetFile(
        dataset_id=dataset.id,
        file_type=file_type,
        filename=filename,
        original_filename=file.filename or f"{file_type}_data.csv",
        file_size=file_size,
        upload_method='file',
        processing_status='completed'  # Mark as completed since no processing needed
    )

    # Save to database
    db.session.add(dataset_file)
    db.session.commit()

    # Update dataset status immediately (no processing needed)
    if file_type == 'patients':
      dataset.patients_file_uploaded = True
    elif file_type == 'taxonomy':
      dataset.taxonomy_file_uploaded = True
    elif file_type == 'bracken':
      dataset.bracken_file_uploaded = True

    dataset.updated_at = datetime.utcnow()

    # Update status to ready if all files are uploaded
    if dataset.is_complete:
      dataset.status = 'ready'

    # Update file count and total size
    dataset.file_count = len(dataset.files)
    dataset.total_size = sum(f.file_size for f in dataset.files)
    db.session.commit()

    # Show success message
    flash(f'✅ {file_type.title()} file uploaded successfully!', 'success')

    log_user_action(
        f"file_uploaded",
        f"{file_type} file uploaded successfully: {dataset_file.original_filename}",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'{file_type.title()} file uploaded successfully',
        'dataset_status': {
            'completion_percentage': dataset.completion_percentage,
            'is_complete': dataset.is_complete,
            'status': dataset.status,
            'patients_uploaded': dataset.patients_file_uploaded,
            'taxonomy_uploaded': dataset.taxonomy_file_uploaded,
            'bracken_uploaded': dataset.bracken_file_uploaded,
            'file_count': dataset.file_count,
            'total_size': dataset.total_size
        }
    })

  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context="File upload",
        user_action=f"Uploading {file_type} file to dataset '{dataset.name}'",
        extra_data={'file_type': file_type}
    )
    log_user_action("file_upload_failed",
                    f"Dataset: {dataset.name}, Type: {file_type}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error uploading file: {str(e)}'
    }), 500


@app.route('/dataset/<int:dataset_id>/processing-status', methods=['GET'])
@login_required
def get_processing_status(dataset_id):
  """Get processing status for all files in a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  processing_status = {}
  for file in dataset.files:
    processing_status[file.file_type] = {
        'status': file.processing_status,
        'started_at': file.processing_started_at.isoformat() if file.processing_started_at else None,
        'completed_at': file.processing_completed_at.isoformat() if file.processing_completed_at else None,
        'error': file.processing_error,
        'summary': json.loads(file.processing_summary) if file.processing_summary else None
    }

  return jsonify({
      'success': True,
      'processing_status': processing_status,
      'dataset_status': {
          'completion_percentage': dataset.completion_percentage,
          'is_complete': dataset.is_complete,
          'status': dataset.status,
          'patients_uploaded': dataset.patients_file_uploaded,
          'taxonomy_uploaded': dataset.taxonomy_file_uploaded,
          'bracken_uploaded': dataset.bracken_file_uploaded,
          'file_count': dataset.file_count,
          'total_size': dataset.total_size
      }
  })


@app.route('/dataset/<int:dataset_id>/delete', methods=['POST'])
@login_required
def delete_dataset(dataset_id):
  """Delete a dataset and all its files"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    # Get dataset info for logging
    dataset_name = dataset.name
    file_count = len(dataset.files)
    total_size = sum(f.file_size for f in dataset.files)

    # Delete all associated files from filesystem
    for file in dataset.files:
      file_path = os.path.join(
          get_user_upload_folder(current_user.id), file.filename)
      if os.path.exists(file_path):
        try:
          os.remove(file_path)
        except OSError as e:
          ErrorLogger.log_warning(
              f"Could not delete file {file.filename}: {e}",
              context="Dataset deletion",
              user_action=f"User deleting dataset '{dataset_name}'",
              extra_data={'file_path': file_path, 'error': str(e)}
          )

    # Delete dataset from database (cascade will delete files)
    db.session.delete(dataset)
    db.session.commit()

    log_user_action(
        "dataset_deleted",
        f"Dataset: {dataset_name} (files: {file_count}, size: {total_size} bytes)",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'Dataset "{dataset_name}" deleted successfully',
        'redirect_url': url_for('dashboard')
    })

  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Deleting dataset {dataset_id}",
        user_action=f"User trying to delete dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'dataset_name': dataset.name,
            'file_count': len(dataset.files)
        }
    )
    log_user_action("dataset_deletion_failed",
                    f"Dataset: {dataset.name}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error deleting dataset: {str(e)}'
    }), 500


@app.route('/dataset/<int:dataset_id>/files')
@login_required
def get_dataset_files(dataset_id):
  """Get files for a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  files = []
  for file in dataset.files:
    files.append({
        'id': file.id,
        'file_type': file.file_type,
        'filename': file.original_filename,
        'size': file.file_size,
        'cure_status': file.cure_status,
        'cure_validation_status': file.cure_validation_status,
        'uploaded_at': file.uploaded_at.isoformat(),
        'modified_at': file.modified_at.isoformat()
    })

  return jsonify({
      'files': files,
      'dataset_status': {
          'completion_percentage': dataset.completion_percentage,
          'is_complete': dataset.is_complete,
          'status': dataset.status,
          'patients_uploaded': dataset.patients_file_uploaded,
          'taxonomy_uploaded': dataset.taxonomy_file_uploaded,
          'bracken_uploaded': dataset.bracken_file_uploaded,
          'file_count': dataset.file_count,
          'total_size': dataset.total_size
      }
  })


@app.route('/dataset/<int:dataset_id>/data-stats')
@login_required
def get_dataset_data_stats(dataset_id):
  """Get data statistics and analysis for a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    stats = {
        'patients': {},
        'taxonomy': {},
        'bracken': {},
        'cross_references': {},
        'sanitization_needed': []
    }

    # Analyze patients data
    if dataset.patients_file_uploaded:
      patients_file = next(
          (f for f in dataset.files if f.file_type == 'patients'), None)
      if patients_file and patients_file.processed_file_path and os.path.exists(patients_file.processed_file_path):
        try:
          import pandas as pd
          df = pd.read_csv(patients_file.processed_file_path)

          stats['patients'] = {
              'total_rows': int(len(df)),
              'total_columns': int(len(df.columns)),
              'patient_id_column': 'patient_id' if 'patient_id' in df.columns else None,
              'unique_patients': int(df['patient_id'].nunique()) if 'patient_id' in df.columns else 0,
              'missing_patient_ids': int(df['patient_id'].isna().sum()) if 'patient_id' in df.columns else 0,
              'duplicate_patient_ids': int(df['patient_id'].duplicated().sum()) if 'patient_id' in df.columns else 0,
              'columns': list(df.columns)
          }

          if stats['patients']['duplicate_patient_ids'] > 0:
            stats['sanitization_needed'].append('remove_duplicates')
          if stats['patients']['missing_patient_ids'] > 0:
            stats['sanitization_needed'].append('remove_missing_ids')

        except Exception as e:
          stats['patients']['error'] = str(e)

    # Analyze taxonomy data
    if dataset.taxonomy_file_uploaded:
      taxonomy_file = next(
          (f for f in dataset.files if f.file_type == 'taxonomy'), None)
      if taxonomy_file and taxonomy_file.processed_file_path and os.path.exists(taxonomy_file.processed_file_path):
        try:
          import pandas as pd
          df = pd.read_csv(taxonomy_file.processed_file_path)

          stats['taxonomy'] = {
              'total_rows': int(len(df)),
              'total_columns': int(len(df.columns)),
              'taxonomy_id_column': 'taxonomy_id' if 'taxonomy_id' in df.columns else None,
              'unique_taxonomies': int(df['taxonomy_id'].nunique()) if 'taxonomy_id' in df.columns else 0,
              'missing_taxonomy_ids': int(df['taxonomy_id'].isna().sum()) if 'taxonomy_id' in df.columns else 0,
              'duplicate_taxonomy_ids': int(df['taxonomy_id'].duplicated().sum()) if 'taxonomy_id' in df.columns else 0,
              'columns': list(df.columns)
          }

          if stats['taxonomy']['duplicate_taxonomy_ids'] > 0:
            stats['sanitization_needed'].append('remove_duplicates')
          if stats['taxonomy']['missing_taxonomy_ids'] > 0:
            stats['sanitization_needed'].append('remove_missing_ids')

        except Exception as e:
          stats['taxonomy']['error'] = str(e)

    # Analyze bracken results
    if dataset.bracken_file_uploaded:
      bracken_file = next(
          (f for f in dataset.files if f.file_type == 'bracken'), None)
      if bracken_file and bracken_file.processed_file_path and os.path.exists(bracken_file.processed_file_path):
        try:
          import pandas as pd
          df = pd.read_csv(bracken_file.processed_file_path)

          # Identify patient_id columns (columns ending with time suffixes)
          patient_columns = [col for col in df.columns if col !=
                             'taxonomy_id' and col != 'taxonomy']
          time_suffixes = []
          for col in patient_columns:
            # Extract time suffix (e.g., "_T1", "_T2", "_baseline", etc.)
            if '_' in col:
              suffix = col.split('_', 1)[1]
              if suffix not in time_suffixes:
                time_suffixes.append(suffix)

          stats['bracken'] = {
              'total_rows': int(len(df)),
              'total_columns': int(len(df.columns)),
              'taxonomy_id_column': 'taxonomy_id' if 'taxonomy_id' in df.columns else None,
              'patient_columns': patient_columns,
              'time_suffixes': time_suffixes,
              'unique_taxonomies': int(df['taxonomy_id'].nunique()) if 'taxonomy_id' in df.columns else 0,
              'missing_taxonomy_ids': int(df['taxonomy_id'].isna().sum()) if 'taxonomy_id' in df.columns else 0,
              'duplicate_taxonomy_ids': int(df['taxonomy_id'].duplicated().sum()) if 'taxonomy_id' in df.columns else 0,
              'columns': list(df.columns)
          }

          if stats['bracken']['missing_taxonomy_ids'] > 0:
            stats['sanitization_needed'].append('remove_missing_ids')
          if stats['bracken']['duplicate_taxonomy_ids'] > 0:
            stats['sanitization_needed'].append('remove_duplicates')

        except Exception as e:
          stats['bracken']['error'] = str(e)

    # Cross-reference analysis
    if stats['patients'] and stats['taxonomy'] and stats['bracken']:
      try:
        # Check if patient IDs in bracken match patients table
        if 'patient_id' in stats['patients'] and stats['patients']['unique_patients'] > 0:
          stats['cross_references'] = {
              'patients_in_bracken': len(stats['bracken']['patient_columns']),
              'potential_mismatch': len(stats['bracken']['patient_columns']) != stats['patients']['unique_patients']
          }

          if stats['cross_references']['potential_mismatch']:
            stats['sanitization_needed'].append('patient_id_mismatch')

      except Exception as e:
        stats['cross_references']['error'] = str(e)

    return jsonify({
        'success': True,
        'stats': stats
    })

  except Exception as e:
    ErrorLogger.log_exception(
        e,
        context=f"Getting data stats for dataset {dataset_id}",
        user_action=f"User requesting data statistics",
        extra_data={'dataset_id': dataset_id}
    )
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@app.route('/dataset/<int:dataset_id>/sanitize', methods=['POST'])
@login_required
def sanitize_dataset_data(dataset_id):
  """Sanitize dataset data based on identified issues"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    sanitization_type = request.json.get('type')
    file_type = request.json.get('file_type')

    if not sanitization_type or not file_type:
      return jsonify({
          'success': False,
          'error': 'Missing sanitization type or file type'
      }), 400

    # Find the file to sanitize
    file_to_sanitize = next(
        (f for f in dataset.files if f.file_type == file_type), None)
    if not file_to_sanitize or not file_to_sanitize.processed_file_path:
      return jsonify({
          'success': False,
          'error': f'No processed {file_type} file found'
      }), 404

    if not os.path.exists(file_to_sanitize.processed_file_path):
      return jsonify({
          'success': False,
          'error': f'Processed {file_type} file not found on disk'
      }), 404

    import pandas as pd
    df = pd.read_csv(file_to_sanitize.processed_file_path)
    original_rows = len(df)

    # Apply sanitization based on type
    if sanitization_type == 'remove_duplicates':
      if file_type == 'patients' and 'patient_id' in df.columns:
        df = df.drop_duplicates(subset=['patient_id'])
      elif file_type == 'taxonomy' and 'taxonomy_id' in df.columns:
        df = df.drop_duplicates(subset=['taxonomy_id'])
      elif file_type == 'bracken' and 'taxonomy_id' in df.columns:
        df = df.drop_duplicates(subset=['taxonomy_id'])
      else:
        return jsonify({
            'success': False,
            'error': f'Cannot remove duplicates for {file_type} file'
        }), 400

    elif sanitization_type == 'remove_missing_ids':
      if file_type == 'patients' and 'patient_id' in df.columns:
        df = df.dropna(subset=['patient_id'])
      elif file_type == 'taxonomy' and 'taxonomy_id' in df.columns:
        df = df.dropna(subset=['taxonomy_id'])
      elif file_type == 'bracken' and 'taxonomy_id' in df.columns:
        df = df.dropna(subset=['taxonomy_id'])
      else:
        return jsonify({
            'success': False,
            'error': f'Cannot remove missing IDs for {file_type} file'
        }), 400

    elif sanitization_type == 'fill_missing_ids':
      if file_type == 'patients' and 'patient_id' in df.columns:
        # Generate unique IDs for missing values
        missing_mask = df['patient_id'].isna()
        if missing_mask.any():
          max_id = df['patient_id'].dropna().max()
          if pd.isna(max_id):
            max_id = 0
          for idx in df[missing_mask].index:
            max_id += 1
            df.loc[idx, 'patient_id'] = f"P{max_id:06d}"
      elif file_type == 'taxonomy' and 'taxonomy_id' in df.columns:
        # Generate unique taxonomy IDs for missing values
        missing_mask = df['taxonomy_id'].isna()
        if missing_mask.any():
          max_id = df['taxonomy_id'].dropna().max()
          if pd.isna(max_id):
            max_id = 0
          for idx in df[missing_mask].index:
            max_id += 1
            df.loc[idx, 'taxonomy_id'] = f"T{max_id:06d}"
      elif file_type == 'bracken' and 'taxonomy_id' in df.columns:
        # Generate unique taxonomy IDs for missing values
        missing_mask = df['taxonomy_id'].isna()
        if missing_mask.any():
          max_id = df['taxonomy_id'].dropna().max()
          if pd.isna(max_id):
            max_id = 0
          for idx in df[missing_mask].index:
            max_id += 1
            df.loc[idx, 'taxonomy_id'] = f"T{max_id:06d}"
      else:
        return jsonify({
            'success': False,
            'error': f'Cannot fill missing IDs for {file_type} file'
        }), 400
    else:
      return jsonify({
          'success': False,
          'error': f'Unknown sanitization type: {sanitization_type}'
      }), 400

    # Save sanitized data
    sanitized_path = file_to_sanitize.processed_file_path.replace(
        '.csv', '_sanitized.csv')
    df.to_csv(sanitized_path, index=False)

    # Update the file record
    file_to_sanitize.processed_file_path = sanitized_path
    file_to_sanitize.processing_summary = json.dumps({
        'sanitization_applied': sanitization_type,
        'original_rows': original_rows,
        'final_rows': len(df),
        'rows_removed': original_rows - len(df),
        'sanitized_at': datetime.utcnow().isoformat()
    })

    db.session.commit()

    log_user_action(
        "data_sanitized",
        f"Dataset: {dataset.name}, File: {file_type}, Type: {sanitization_type}",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'{file_type.title()} data sanitized successfully',
        'details': {
            'original_rows': original_rows,
            'final_rows': len(df),
            'rows_removed': original_rows - len(df),
            'sanitization_type': sanitization_type
        }
    })

  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Sanitizing {file_type} data for dataset {dataset_id}",
        user_action=f"User sanitizing data in dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_type': file_type,
            'sanitization_type': sanitization_type
        }
    )
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@app.route('/dataset/<int:dataset_id>/file/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_dataset_file(dataset_id, file_id):
  """Delete a specific file from a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()

  try:
    # Get file info for logging
    file_type = dataset_file.file_type
    filename = dataset_file.original_filename
    file_size = dataset_file.file_size

    # Delete the physical file
    file_path = os.path.join(get_user_upload_folder(
        current_user.id), dataset_file.filename)
    if os.path.exists(file_path):
      try:
        os.remove(file_path)
      except OSError as e:
        ErrorLogger.log_warning(
            f"Could not delete file {dataset_file.filename}: {e}",
            context="Individual file deletion",
            user_action=f"User deleting file '{filename}' from dataset '{dataset.name}'",
            extra_data={'file_path': file_path, 'error': str(e)}
        )

    # Also delete processed file if it exists
    if dataset_file.processed_file_path and os.path.exists(dataset_file.processed_file_path):
      try:
        os.remove(dataset_file.processed_file_path)
      except OSError as e:
        ErrorLogger.log_warning(
            f"Could not delete processed file {dataset_file.processed_file_path}: {e}",
            context="Individual file deletion",
            user_action=f"User deleting file '{filename}' from dataset '{dataset.name}'",
            extra_data={
                'file_path': dataset_file.processed_file_path, 'error': str(e)}
        )

    # Update dataset file status flags - only reset if no files of this type remain
    remaining_files_of_type = [
        f for f in dataset.files if f.id != file_id and f.file_type == file_type]
    if not remaining_files_of_type:
      if file_type == 'patients':
        dataset.patients_file_uploaded = False
      elif file_type == 'taxonomy':
        dataset.taxonomy_file_uploaded = False
      elif file_type == 'bracken':
        dataset.bracken_file_uploaded = False

    # Update dataset status
    if not dataset.is_complete:
      dataset.status = 'draft'

    dataset.updated_at = datetime.utcnow()

    # Delete the database record
    db.session.delete(dataset_file)
    db.session.commit()

    # Refresh the dataset to get updated file count and total size
    db.session.refresh(dataset)

    # Update file count and total size
    dataset.file_count = len(dataset.files)
    dataset.total_size = sum(f.file_size for f in dataset.files)
    db.session.commit()

    log_user_action(
        "file_deleted",
        f"File deleted: {filename} ({file_type}) from dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'{file_type.title()} file "{filename}" deleted successfully',
        'dataset_status': {
            'completion_percentage': dataset.completion_percentage,
            'is_complete': dataset.is_complete,
            'status': dataset.status,
            'patients_uploaded': dataset.patients_file_uploaded,
            'taxonomy_uploaded': dataset.taxonomy_file_uploaded,
            'bracken_uploaded': dataset.bracken_file_uploaded,
            'file_count': dataset.file_count,
            'total_size': dataset.total_size
        }
    })

  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Deleting file {file_id} from dataset {dataset_id}",
        user_action=f"User trying to delete file from dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_id': file_id,
            'file_type': dataset_file.file_type,
            'filename': dataset_file.original_filename
        }
    )
    log_user_action("file_deletion_failed",
                    f"File: {dataset_file.original_filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error deleting file: {str(e)}'
    }), 500


@app.route('/dataset/<int:dataset_id>/file/<int:file_id>/duplicate', methods=['POST'])
@login_required
def duplicate_dataset_file(dataset_id, file_id):
  """Duplicate a specific file in a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()

  try:
    # Get file info
    original_filename = dataset_file.original_filename
    filename = dataset_file.filename
    file_type = dataset_file.file_type
    file_size = dataset_file.file_size

    # Generate new filename with "_copy" suffix
    name_parts = original_filename.rsplit('.', 1)
    if len(name_parts) == 2:
      base_name, extension = name_parts
      new_original_filename = f"{base_name}_copy.{extension}"
    else:
      new_original_filename = f"{original_filename}_copy"

    # Generate new internal filename
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{dataset.id}_{file_type}_{timestamp}_copy{os.path.splitext(filename)[1]}"

    # Copy the physical file (handle missing file gracefully)
    user_upload_folder = get_user_upload_folder(current_user.id)
    original_file_path = os.path.join(user_upload_folder, filename)
    new_file_path = os.path.join(user_upload_folder, new_filename)

    if not os.path.exists(original_file_path):
      # Return 404 instead of raising so callers get a clean response
      ErrorLogger.log_warning(
          f"Original file not found when duplicating: {original_file_path}",
          context="File duplication",
          user_action=f"User trying to duplicate file '{original_filename}' in dataset '{dataset.name}'",
          extra_data={'dataset_id': dataset_id, 'file_id': file_id}
      )
      return jsonify({'success': False, 'message': 'Original file not found'}), 404

    try:
      shutil.copy2(original_file_path, new_file_path)
    except Exception as e:
      db.session.rollback()
      ErrorLogger.log_exception(
          e,
          context="Copying file during duplication",
          user_action=f"User duplicating file '{original_filename}' in dataset '{dataset.name}'",
          extra_data={'src': original_file_path, 'dst': new_file_path}
      )
      log_user_action("file_duplication_failed",
                      f"File copy failed: {original_filename}", success=False)
      return jsonify({'success': False, 'message': f'Error copying file: {str(e)}'}), 500

    # Also copy processed file if it exists
    processed_file_path = None
    if dataset_file.processed_file_path and os.path.exists(dataset_file.processed_file_path):
      try:
        processed_ext = os.path.splitext(
            dataset_file.processed_file_path)[1] or '.csv'
        processed_filename = f"{os.path.splitext(new_filename)[0]}_processed{processed_ext}"
        processed_file_path = os.path.join(
            user_upload_folder, processed_filename)
        shutil.copy2(dataset_file.processed_file_path, processed_file_path)
      except Exception as e:
        # Log and continue; duplication of processed file is not critical
        ErrorLogger.log_warning(
            f"Could not copy processed file during duplication: {e}",
            context="File duplication - processed file",
            user_action=f"User duplicating file '{original_filename}'",
            extra_data={'processed_src': dataset_file.processed_file_path,
                        'intended_dst': processed_file_path, 'error': str(e)}
        )
        processed_file_path = None

    # Create new database entry
    new_dataset_file = DatasetFile(
        dataset_id=dataset_id,
        file_type=file_type,
        filename=new_filename,
        original_filename=new_original_filename,
        file_size=file_size,
        upload_method='duplicate',
        processed_file_path=processed_file_path,
        processing_status=dataset_file.processing_status,
        processing_summary=dataset_file.processing_summary
    )

    db.session.add(new_dataset_file)
    db.session.commit()

    # Update dataset statistics
    dataset.updated_at = datetime.utcnow()
    dataset.file_count = len(dataset.files)
    dataset.total_size = sum(f.file_size for f in dataset.files)
    db.session.commit()

    log_user_action(
        "file_duplicated",
        f"File duplicated: {original_filename} -> {new_original_filename} in dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'File "{original_filename}" duplicated successfully as "{new_original_filename}"',
        'file_type': file_type,
        'original_filename': original_filename,
        'new_filename': new_original_filename,
        'dataset_status': {
            'completion_percentage': dataset.completion_percentage,
            'is_complete': dataset.is_complete,
            'status': dataset.status,
            'patients_uploaded': dataset.patients_file_uploaded,
            'taxonomy_uploaded': dataset.taxonomy_file_uploaded,
            'bracken_uploaded': dataset.bracken_file_uploaded,
            'file_count': dataset.file_count,
            'total_size': dataset.total_size
        }
    })

  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Duplicating file {file_id} from dataset {dataset_id}",
        user_action=f"User trying to duplicate file from dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_id': file_id,
            'file_type': dataset_file.file_type,
            'filename': dataset_file.original_filename
        }
    )
    log_user_action("file_duplication_failed",
                    f"File: {dataset_file.original_filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error duplicating file: {str(e)}'
    }), 500


@app.route('/dataset/<int:dataset_id>/file/<int:file_id>/cure', methods=['POST'])
@login_required
def cure_dataset_file(dataset_id, file_id):
  """Cure (process and validate) a specific file in a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()

  try:
    # Update cure status to curing
    dataset_file.cure_status = 'curing'
    db.session.commit()

    # Simulate curing process (in a real implementation, this would be more complex)
    # For now, we'll just mark it as cured with OK validation
    import time
    time.sleep(1)  # Simulate processing time

    # Update cure status
    dataset_file.cure_status = 'cured'
    dataset_file.cure_validation_status = 'ok'  # or 'warnings', 'errors'
    dataset_file.cured_at = datetime.utcnow()
    db.session.commit()

    # Update dataset statistics
    dataset.updated_at = datetime.utcnow()
    db.session.commit()

    log_user_action(
        "file_cured",
        f"File cured: {dataset_file.original_filename} in dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'File "{dataset_file.original_filename}" cured successfully',
        'file_type': dataset_file.file_type,
        'cure_status': dataset_file.cure_status,
        'validation_status': dataset_file.cure_validation_status
    })

  except Exception as e:
    db.session.rollback()
    # Reset cure status on error
    dataset_file.cure_status = 'not_cured'
    dataset_file.cure_validation_status = 'pending'
    db.session.commit()

    ErrorLogger.log_exception(
        e,
        context=f"Curing file {file_id} from dataset {dataset_id}",
        user_action=f"User trying to cure file from dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_id': file_id,
            'file_type': dataset_file.file_type,
            'filename': dataset_file.original_filename
        }
    )
    log_user_action("file_cure_failed",
                    f"File: {dataset_file.original_filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error curing file: {str(e)}'
    }), 500


@app.route('/dataset/<int:dataset_id>/file/<int:file_id>/rename', methods=['POST'])
@login_required
def rename_dataset_file(dataset_id, file_id):
  """Rename a specific file in a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()

  try:
    data = request.get_json()
    new_filename = data.get('new_filename', '').strip()

    if not new_filename:
      return jsonify({
          'success': False,
          'message': 'New filename cannot be empty'
      }), 400

    # Validate filename (basic validation)
    if '/' in new_filename or '\\' in new_filename:
      return jsonify({
          'success': False,
          'message': 'Filename cannot contain path separators'
      }), 400

    # Get the original filename for comparison
    old_filename = dataset_file.filename
    old_original_filename = dataset_file.original_filename

    # Check if the new filename already exists in the same dataset
    existing_file = DatasetFile.query.filter_by(
        dataset_id=dataset_id,
        filename=new_filename
    ).first()

    if existing_file and existing_file.id != file_id:
      # Generate a unique name with 4-digit number
      base_name = new_filename
      extension = ''
      if '.' in new_filename:
        parts = new_filename.rsplit('.', 1)
        base_name = parts[0]
        extension = '.' + parts[1]

      # Find the next available number
      counter = 1
      while counter < 10000:
        numbered_filename = f"{base_name}_{counter:04d}{extension}"
        existing_numbered = DatasetFile.query.filter_by(
            dataset_id=dataset_id,
            filename=numbered_filename
        ).first()
        if not existing_numbered:
          new_filename = numbered_filename
          break
        counter += 1

      if counter >= 10000:
        return jsonify({
            'success': False,
            'message': 'Could not generate unique filename'
        }), 400

    # Rename the physical file
    user_folder = get_user_upload_folder(current_user.id)
    old_file_path = os.path.join(user_folder, old_filename)
    new_file_path = os.path.join(user_folder, new_filename)

    if os.path.exists(old_file_path):
      try:
        os.rename(old_file_path, new_file_path)
      except OSError as e:
        ErrorLogger.log_exception(
            e,
            context=f"Renaming file {old_filename} to {new_filename}",
            user_action=f"User renaming file in dataset '{dataset.name}'",
            extra_data={
                'old_path': old_file_path,
                'new_path': new_file_path,
                'error': str(e)
            }
        )
        return jsonify({
            'success': False,
            'message': f'Error renaming file: {str(e)}'
        }), 500

    # Update the database record
    dataset_file.filename = new_filename
    dataset_file.original_filename = new_filename  # Update original filename too
    dataset_file.modified_at = datetime.utcnow()
    db.session.commit()

    log_user_action(
        "file_renamed",
        f"File renamed: '{old_original_filename}' → '{new_filename}' in dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'File renamed to "{new_filename}" successfully',
        'old_filename': old_original_filename,
        'new_filename': new_filename,
        'file_type': dataset_file.file_type
    })

  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Renaming file {file_id} in dataset {dataset_id}",
        user_action=f"User trying to rename file in dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_id': file_id,
            'new_filename': data.get('new_filename') if 'data' in locals() else None
        }
    )
    log_user_action("file_rename_failed",
                    f"File ID: {file_id}, New name: {data.get('new_filename') if 'data' in locals() else 'unknown'}",
                    success=False)

    return jsonify({
        'success': False,
        'message': f'Error renaming file: {str(e)}'
    }), 500

# Authentication routes


@app.route('/auth/login')
def login():
  """Initiate Google OAuth login"""
  if current_user.is_authenticated:
    return redirect(url_for('dashboard'))

  # Check if OAuth is properly configured
  if (app.config['GOOGLE_CLIENT_ID'] == 'dummy-client-id' or
          app.config['GOOGLE_CLIENT_SECRET'] == 'dummy-client-secret'):
    ErrorLogger.log_warning(
        "OAuth not configured - using dummy credentials",
        context="Google OAuth login attempt",
        user_action="User trying to log in with Google",
        extra_data={
            'oauth_provider': 'google',
            'client_id_configured': app.config['GOOGLE_CLIENT_ID'] != 'dummy-client-id',
            'client_secret_configured': app.config['GOOGLE_CLIENT_SECRET'] != 'dummy-client-secret'
        }
    )
    log_user_action("oauth_config_error",
                    "OAuth not properly configured", success=False)
    flash('Google OAuth is not configured. Please set up GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your environment variables.', 'error')
    return redirect(url_for('index'))

  try:
    with PerformanceTracker("oauth_initiate", "Google OAuth redirect"):
      redirect_uri = url_for('auth_callback', _external=True)
      result = google.authorize_redirect(redirect_uri)
    log_user_action("oauth_initiate",
                    "Google OAuth redirect initiated", success=True)
    return result
  except Exception as e:
    ErrorLogger.log_exception(
        e,
        context="Initiating Google OAuth login",
        user_action="User trying to log in with Google",
        extra_data={
            'oauth_provider': 'google',
            'redirect_uri': request.url,
            'error_type': 'oauth_initiation_error'
        }
    )
    log_user_action("oauth_initiate_failed",
                    "Google OAuth redirect failed", success=False)
    app.logger.error(f'OAuth configuration error: {e}')
    flash('Authentication service is not available. Please try again later.', 'error')
    return redirect(url_for('index'))


@app.route('/auth/login/authorized')
def auth_callback():
  """Handle Google OAuth callback"""
  # Check if OAuth is properly configured first
  if (app.config['GOOGLE_CLIENT_ID'] == 'dummy-client-id' or
          app.config['GOOGLE_CLIENT_SECRET'] == 'dummy-client-secret'):
    ErrorLogger.log_warning(
        "OAuth callback with dummy credentials",
        context="Google OAuth callback processing",
        user_action="User completing OAuth login",
        extra_data={
            'oauth_provider': 'google',
            'callback_url': request.url,
            'error_type': 'oauth_not_configured'
        }
    )
    log_user_action("oauth_callback_error",
                    "OAuth not configured for callback", success=False)
    flash('Google OAuth is not configured. Please set up OAuth credentials.', 'error')
    return redirect(url_for('index'))

  try:
    with PerformanceTracker("oauth_callback", "Google OAuth token exchange"):
      # Get the authorization code from the request
      code = request.args.get('code')
      if not code:
        raise ValueError("No authorization code received")

      # Exchange code for access token manually
      token_url = 'https://oauth2.googleapis.com/token'
      token_data = {
          'client_id': app.config['GOOGLE_CLIENT_ID'],
          'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
          'code': code,
          'grant_type': 'authorization_code',
          'redirect_uri': url_for('auth_callback', _external=True)
      }

      import requests
      token_response = requests.post(token_url, data=token_data)
      token_response.raise_for_status()
      token_info = token_response.json()

      # Get user info using the access token
      userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
      headers = {'Authorization': f"Bearer {token_info['access_token']}"}
      userinfo_response = requests.get(userinfo_url, headers=headers)
      userinfo_response.raise_for_status()
      user_info = userinfo_response.json()

    if user_info:
      with PerformanceTracker("user_login_process", f"User: {user_info.get('email')}"):
        # Check if user exists
        user = User.query.filter_by(google_id=user_info['id']).first()

        if not user:
          # Create new user
          user = User(
              email=user_info['email'],
              name=user_info['name'],
              google_id=user_info['id'],
              profile_pic=user_info.get('picture'),
              last_login=datetime.utcnow()
          )
          db.session.add(user)
          log_user_action(
              "user_created", f"New user: {user_info['email']}", success=True)
        else:
          # Update existing user
          user.last_login = datetime.utcnow()
          user.name = user_info['name']
          user.profile_pic = user_info.get('picture')

        db.session.commit()
        login_user(user, remember=True)

      log_user_action(
          "user_login", f"Successful login: {user.email}", success=True)
      flash(f'Welcome, {user.name}!', 'success')

      # Redirect to next page or dashboard
      next_page = request.args.get('next')
      return redirect(next_page) if next_page else redirect(url_for('dashboard'))
    else:
      ErrorLogger.log_exception(
          ValueError("No user info received from Google API"),
          context="OAuth callback processing",
          user_action="User completing OAuth login",
          extra_data={'token_info': str(
              token_info) if 'token_info' in locals() else None}
      )
      log_user_action("oauth_callback_failed",
                      "No user info from API", success=False)

  except Exception as e:
    ErrorLogger.log_exception(
        e,
        context="Processing Google OAuth callback",
        user_action="User completing OAuth login",
        extra_data={
            'oauth_provider': 'google',
            'callback_url': request.url,
            'user_agent': request.headers.get('User-Agent'),
            'error_type': 'oauth_callback_error'
        }
    )
    log_user_action("oauth_callback_failed",
                    f"OAuth callback error: {str(e)}", success=False)
    app.logger.error(f'OAuth error: {e}')
    flash('Authentication failed. Please try again.', 'error')

  return redirect(url_for('index'))


@app.route('/auth/logout')
@login_required
def logout():
  """Logout user"""
  try:
    user_email = current_user.email if current_user.is_authenticated else 'unknown'
    logout_user()
    log_user_action(
        "user_logout", f"User logged out: {user_email}", success=True)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))
  except Exception as e:
    ErrorLogger.log_exception(
        e,
        context="User logout process",
        user_action="User trying to logout",
        extra_data={
            'user_id': current_user.id if current_user.is_authenticated else None}
    )
    log_user_action("logout_failed", "Logout process failed", success=False)
    flash('Logout encountered an error, but you have been logged out.', 'warning')
    return redirect(url_for('index'))

# API routes


@app.route('/api/config')
def api_config():
  """API endpoint to get application configuration"""
  user_upload_folder = get_user_upload_folder(
      current_user.id if current_user.is_authenticated else None)
  return jsonify({
      'maxFileSize': app.config['MAX_CONTENT_LENGTH'],
      'maxFileSizeMB': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024),
      'allowedFileTypes': ['.csv', '.tsv', '.txt'],
      'uploadFolder': user_upload_folder
  })


@app.route('/api/datasets')
@login_required
def api_datasets():
  """API endpoint to get user's datasets"""
  datasets = Dataset.query.filter_by(user_id=current_user.id).all()
  return jsonify([{
      'id': d.id,
      'name': d.name,
      'description': d.description,
      'status': d.status,
      'file_count': d.file_count,
      'created_at': d.created_at.isoformat(),
      'updated_at': d.updated_at.isoformat()
  } for d in datasets])

# Editor endpoints for per-file custom component


@app.route('/api/editor/file/<int:file_id>', methods=['GET'])
@login_required
def editor_route(file_id):
  """Editor entry endpoint for a specific dataset file. Enforce ownership: only dataset owner may access these endpoints. Returns 404 if file does not exist. """
  dataset_file = DatasetFile.query.filter_by(id=file_id).first_or_404()
  dataset = Dataset.query.filter_by(id=dataset_file.dataset_id).first()
  if not dataset or dataset.user_id != current_user.id:
    return jsonify({'error': 'Forbidden: You do not have access to this file'}), 403

  # Prefer processed file if present and exists on disk; otherwise use uploaded file
  preferred_path = None
  if getattr(dataset_file, 'processed_file_path', None) and os.path.exists(dataset_file.processed_file_path):
    preferred_path = dataset_file.processed_file_path
  else:
    preferred_path = os.path.join(get_user_upload_folder(
        current_user.id), dataset_file.filename)

  if not os.path.exists(preferred_path):
    return jsonify({'error': 'File not found'}), 404

  # Build apiBase and options for the client-side table component
  # Determine table type for title
  table_type = dataset_file.file_type if hasattr(
      dataset_file, 'file_type') else 'file'
  # For the editor, use the basename of the preferred file
  filename = os.path.basename(preferred_path)
  title = f'Smart-table editor for {table_type.title()} table'
  api_base = request.url_root.rstrip('/') + request.path
  options = {
      "showDebug": True,
      "pageSize": 10,
      "filename": filename,
      "columnConfig": {
          "gender": {
              "displayType": "label",
              "colorScheme": "custom",
              "customColors": {
                  "Male": "#007bff",
                  "Female": "#e83e8c",
                  "Other": "#6c757d",
              },
          },
      },
  }
  return render_template("smart_table.html", apiBase=api_base, options=options, title=title)


@app.route('/api/editor/file/<int:file_id>/data', methods=['GET'])
@login_required
def editor_data(file_id):
  dataset_file = DatasetFile.query.filter_by(id=file_id).first_or_404()
  dataset = Dataset.query.filter_by(id=dataset_file.dataset_id).first()
  if not dataset or dataset.user_id != current_user.id:
    return jsonify({'error': 'Forbidden: You do not have access to this file'}), 403

  # Prefer processed file if present
  if getattr(dataset_file, 'processed_file_path', None) and os.path.exists(dataset_file.processed_file_path):
    file_path = dataset_file.processed_file_path
  else:
    file_path = os.path.join(get_user_upload_folder(
        current_user.id), dataset_file.filename)

  if not os.path.exists(file_path):
    return jsonify({'error': 'File not found'}), 404

  return jsonify(build_table_data(csv_file=file_path))


@app.route('/api/editor/file/<int:file_id>/schema', methods=['GET'])
@login_required
def editor_schema(file_id):
  dataset_file = DatasetFile.query.filter_by(id=file_id).first_or_404()
  dataset = Dataset.query.filter_by(id=dataset_file.dataset_id).first()
  if not dataset or dataset.user_id != current_user.id:
    return jsonify({'error': 'Forbidden: You do not have access to this file'}), 403

  # Prefer processed file if present
  if getattr(dataset_file, 'processed_file_path', None) and os.path.exists(dataset_file.processed_file_path):
    file_path = dataset_file.processed_file_path
  else:
    file_path = os.path.join(get_user_upload_folder(
        current_user.id), dataset_file.filename)

  if not os.path.exists(file_path):
    return jsonify({'error': 'File not found'}), 404

  return jsonify(build_schema(csv_file=file_path))


@app.route('/api/editor/file/<int:file_id>/save', methods=['POST'])
@login_required
def editor_save(file_id):
  dataset_file = DatasetFile.query.filter_by(id=file_id).first_or_404()
  dataset = Dataset.query.filter_by(id=dataset_file.dataset_id).first()
  if not dataset or dataset.user_id != current_user.id:
    return jsonify({'error': 'Forbidden: You do not have access to this file'}), 403

  # Prefer processed file if present when saving edits, otherwise save to uploaded file
  if getattr(dataset_file, 'processed_file_path', None) and os.path.exists(dataset_file.processed_file_path):
    file_path = dataset_file.processed_file_path
  else:
    file_path = os.path.join(get_user_upload_folder(
        current_user.id), dataset_file.filename)

  if not os.path.exists(file_path):
    return jsonify({'error': 'File not found'}), 404

  try:
    data = request.get_json()
    if not data:
      return jsonify({"status": "error", "message": "No data received"}), 400
    save_table(data=data, csv_file=file_path)
    return jsonify({"status": "success", "message": "Data saved successfully"}), 200
  except Exception as e:
    print(f"Error processing request: {str(e)}")
    return jsonify({"status": "error", "message": f"Error processing request: {str(e)}"}), 500


@app.errorhandler(400)
def bad_request(error):
  """Handle bad request errors"""
  ErrorLogger.log_exception(
      error,
      context="Bad request error (400)",
      user_action=f"User accessing {request.url}",
      extra_data={
          'error_description': str(error.description) if hasattr(error, 'description') else None,
          'request_method': request.method,
          'request_data': dict(request.form) if request.form else None
      }
  )
  log_user_action("error_400", f"Bad request: {request.url}", success=False)
  return render_template('error.html', error='Bad request', code=400), 400


@app.errorhandler(401)
def unauthorized(error):
  """Handle unauthorized access errors"""
  ErrorLogger.log_exception(
      error,
      context="Unauthorized access error (401)",
      user_action=f"User trying to access {request.url}",
      extra_data={
          'requires_login': True,
          'requested_endpoint': request.endpoint
      }
  )
  log_user_action(
      "error_401", f"Unauthorized access: {request.url}", success=False)
  return render_template('error.html', error='Unauthorized access', code=401), 401


@app.errorhandler(403)
def forbidden(error):
  """Handle forbidden access errors"""
  ErrorLogger.log_exception(
      error,
      context="Forbidden access error (403)",
      user_action=f"User trying to access {request.url}",
      extra_data={
          'user_has_permission': False,
          'requested_endpoint': request.endpoint
      }
  )
  log_user_action(
      "error_403", f"Forbidden access: {request.url}", success=False)
  return render_template('error.html', error='Access forbidden', code=403), 403


@app.errorhandler(404)
def not_found(error):
  """Handle page not found errors"""
  ErrorLogger.log_warning(
      f"Page not found: {request.url}",
      context="404 error - page not found",
      user_action=f"User trying to access non-existent page",
      extra_data={
          'referrer': request.referrer,
          'user_agent': request.headers.get('User-Agent')
      }
  )
  log_user_action("error_404", f"Page not found: {request.url}", success=False)
  return render_template('error.html', error='Page not found', code=404), 404


@app.errorhandler(413)
def file_too_large(error):
  """Handle file too large errors"""
  max_size_mb = app.config.get(
      'MAX_CONTENT_LENGTH', 16 * 1024 * 1024) // (1024 * 1024)
  ErrorLogger.log_exception(
      error,
      context="File upload too large (413)",
      user_action="User trying to upload file",
      extra_data={
          'max_content_length': app.config.get('MAX_CONTENT_LENGTH'),
          'max_size_mb': max_size_mb,
          'content_length': request.content_length
      }
  )
  log_user_action(
      "error_413", f"File upload too large (max: {max_size_mb}MB)", success=False)
  return render_template('error.html',
                         error=f'File too large. Maximum file size is {max_size_mb}MB.',
                         code=413), 413


@app.errorhandler(429)
def rate_limit_exceeded(error):
  """Handle rate limit exceeded errors"""
  ErrorLogger.log_exception(
      error,
      context="Rate limit exceeded (429)",
      user_action=f"User making too many requests to {request.url}",
      extra_data={
          'rate_limit_info': str(error.description) if hasattr(error, 'description') else None
      }
  )
  log_user_action("error_429", "Rate limit exceeded", success=False)
  return render_template('error.html', error='Too many requests', code=429), 429


@app.errorhandler(500)
def internal_error(error):
  """Handle internal server errors"""
  db.session.rollback()

  ErrorLogger.log_exception(
      error,
      context="Internal server error (500)",
      user_action=f"User accessing {request.url}",
      extra_data={
          'error_type': type(error).__name__ if error else 'Unknown',
          'database_rollback': True
      }
  )
  log_user_action(
      "error_500", f"Internal server error: {request.url}", success=False)
  return render_template('error.html', error='Internal server error', code=500), 500


@app.errorhandler(502)
def bad_gateway(error):
  """Handle bad gateway errors"""
  ErrorLogger.log_exception(
      error,
      context="Bad gateway error (502)",
      user_action=f"User accessing {request.url}",
      extra_data={'upstream_service_error': True}
  )
  log_user_action("error_502", "Bad gateway error", success=False)
  return render_template('error.html', error='Service temporarily unavailable', code=502), 502


@app.errorhandler(503)
def service_unavailable(error):
  """Handle service unavailable errors"""
  ErrorLogger.log_exception(
      error,
      context="Service unavailable error (503)",
      user_action=f"User accessing {request.url}",
      extra_data={'service_maintenance': True}
  )
  log_user_action("error_503", "Service unavailable", success=False)
  return render_template('error.html', error='Service unavailable', code=503), 503


@app.errorhandler(Exception)
def handle_unexpected_error(error):
  """Handle any unexpected errors"""
  db.session.rollback()

  ErrorLogger.log_exception(
      error,
      context="Unexpected error - Global exception handler",
      user_action=f"User accessing {request.url}",
      extra_data={
          'unexpected_error': True,
          'error_class': error.__class__.__name__,
          'database_rollback': True
      }
  )
  log_user_action("error_unexpected",
                  f"Unexpected error: {type(error).__name__}", success=False)

  # Return appropriate error response based on request type
  if request.path.startswith('/api/'):
    return jsonify({
        'error': 'An unexpected error occurred',
        'code': 500,
        'request_id': getattr(request, 'request_id', 'unknown')
    }), 500
  else:
    return render_template('error.html',
                           error='An unexpected error occurred',
                           code=500), 500


# Set up comprehensive logging
setup_logging(app)

# Request tracking middleware


@app.before_request
def before_request():
  """Track request start time and assign request ID"""
  g.start_time = time.time()
  g.request_id = str(uuid.uuid4())[:8]
  request.request_id = g.request_id

  # Log request start for audit trail
  if request.endpoint not in ['static', None]:
    log_user_action(
        f"REQUEST_START",
        f"{request.method} {request.path}",
        success=True
    )


@app.after_request
def after_request(response):
  """Log request completion and performance"""
  if hasattr(g, 'start_time') and request.endpoint not in ['static', None]:
    duration = time.time() - g.start_time

    # Log performance
    log_performance(
        f"{request.method} {request.endpoint or request.path}",
        duration,
        f"Status: {response.status_code}"
    )

    # Log request completion
    log_user_action(
        f"REQUEST_END",
        f"{request.method} {request.path} - Status: {response.status_code}",
        success=response.status_code < 400,
        duration=duration
    )

  return response


# Create directory structure
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Global fallback
os.makedirs(os.path.join(app.instance_path, 'users'),
            exist_ok=True)  # User folders
os.makedirs(os.path.join(app.instance_path, 'logs', 'notLogged'),
            exist_ok=True)  # Anonymous logs

# Create database tables
with app.app_context():
  db.create_all()

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5005, debug=True)
