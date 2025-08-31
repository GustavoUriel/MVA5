"""
Datasets Blueprint
Dataset management functionality
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db, limiter
from models import Dataset, AnalysisJob, UserLog
from utils.logging_config import log_user_activity
from utils.file_utils import allowed_file, save_uploaded_file
from tasks.analysis_tasks import process_dataset_upload
import os
import uuid
from datetime import datetime


datasets_bp = Blueprint('datasets', __name__)


@datasets_bp.route('/dashboard')
@login_required
def dashboard():
  """Main dashboard showing user's datasets"""
  page = request.args.get('page', 1, type=int)
  per_page = 10

  datasets = current_user.datasets.order_by(Dataset.created_at.desc()).paginate(
      page=page, per_page=per_page, error_out=False
  )

  log_user_activity(
      current_user.id,
      'dashboard_viewed',
      {
          'page': page,
          'total_datasets': current_user.datasets.count()
      }
  )

  return render_template('datasets/dashboard.html', datasets=datasets)


@datasets_bp.route('/create', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per hour")
def create_dataset():
  """Create a new dataset"""
  if request.method == 'POST':
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
      flash('Dataset name is required.', 'error')
      return render_template('datasets/create.html')

    # Check if dataset name already exists for this user
    existing = Dataset.query.filter_by(
        user_id=current_user.id, name=name).first()
    if existing:
      flash('A dataset with this name already exists.', 'error')
      return render_template('datasets/create.html')

    try:
      # Create new dataset
      dataset = Dataset(
          name=name,
          description=description,
          user_id=current_user.id,
          uuid=str(uuid.uuid4())
      )

      db.session.add(dataset)
      db.session.commit()

      log_user_activity(
          current_user.id,
          'dataset_created',
          {
              'dataset_id': dataset.id,
              'dataset_name': dataset.name,
              'dataset_uuid': dataset.uuid
          }
      )

      flash(f'Dataset "{name}" created successfully!', 'success')
      return redirect(url_for('datasets.view_dataset', dataset_id=dataset.id))

    except Exception as e:
      db.session.rollback()
      current_app.logger.error(f"Dataset creation error: {str(e)}")
      flash('Error creating dataset. Please try again.', 'error')

  return render_template('datasets/create.html')


@datasets_bp.route('/<int:dataset_id>')
@login_required
def view_dataset(dataset_id):
  """View a specific dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  # Get recent analysis jobs
  analysis_jobs = dataset.analysis_jobs.order_by(
      AnalysisJob.created_at.desc()).limit(10).all()

  log_user_activity(
      current_user.id,
      'dataset_viewed',
      {
          'dataset_id': dataset.id,
          'dataset_name': dataset.name
      }
  )

  return render_template('datasets/view.html', dataset=dataset, analysis_jobs=analysis_jobs)


@datasets_bp.route('/<int:dataset_id>/upload', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per hour")
def upload_file(dataset_id):
  """Upload file to dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  if request.method == 'POST':
    if 'file' not in request.files:
      flash('No file selected.', 'error')
      return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
      flash('No file selected.', 'error')
      return redirect(request.url)

    if not allowed_file(file.filename):
      flash('File type not allowed. Please upload CSV, TXT, TSV, XLSX, or JSON files.', 'error')
      return redirect(request.url)

    try:
      # Save file
      file_path, file_size = save_uploaded_file(
          file, current_user.id, dataset.uuid)

      # Update dataset
      dataset.file_path = file_path
      dataset.file_size = file_size
      dataset.status = 'processing'
      dataset.updated_at = datetime.utcnow()

      db.session.commit()

      # Start background processing
      task = process_dataset_upload.delay(dataset.id, file_path)

      # Create analysis job record
      job = AnalysisJob(
          dataset_id=dataset.id,
          job_type='file_upload_processing',
          status='running',
          celery_task_id=task.id,
          started_at=datetime.utcnow()
      )
      db.session.add(job)
      db.session.commit()

      log_user_activity(
          current_user.id,
          'file_uploaded',
          {
              'dataset_id': dataset.id,
              'filename': file.filename,
              'file_size': file_size,
              'task_id': task.id
          }
      )

      flash('File uploaded successfully and is being processed.', 'success')
      return redirect(url_for('datasets.view_dataset', dataset_id=dataset.id))

    except Exception as e:
      db.session.rollback()
      current_app.logger.error(f"File upload error: {str(e)}")
      flash('Error uploading file. Please try again.', 'error')

  return render_template('datasets/upload.html', dataset=dataset)


@datasets_bp.route('/<int:dataset_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_dataset(dataset_id):
  """Edit dataset details"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  if request.method == 'POST':
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
      flash('Dataset name is required.', 'error')
      return render_template('datasets/edit.html', dataset=dataset)

    # Check if new name conflicts with existing datasets
    if name != dataset.name:
      existing = Dataset.query.filter_by(
          user_id=current_user.id, name=name).first()
      if existing:
        flash('A dataset with this name already exists.', 'error')
        return render_template('datasets/edit.html', dataset=dataset)

    try:
      old_name = dataset.name
      dataset.name = name
      dataset.description = description
      dataset.updated_at = datetime.utcnow()

      db.session.commit()

      log_user_activity(
          current_user.id,
          'dataset_updated',
          {
              'dataset_id': dataset.id,
              'old_name': old_name,
              'new_name': name
          }
      )

      flash('Dataset updated successfully!', 'success')
      return redirect(url_for('datasets.view_dataset', dataset_id=dataset.id))

    except Exception as e:
      db.session.rollback()
      current_app.logger.error(f"Dataset update error: {str(e)}")
      flash('Error updating dataset. Please try again.', 'error')

  return render_template('datasets/edit.html', dataset=dataset)


@datasets_bp.route('/<int:dataset_id>/delete', methods=['POST'])
@login_required
@limiter.limit("10 per hour")
def delete_dataset(dataset_id):
  """Delete a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    dataset_name = dataset.name

    # Delete associated files
    if dataset.file_path and os.path.exists(dataset.file_path):
      os.remove(dataset.file_path)

    # Delete dataset (cascades to analysis jobs)
    db.session.delete(dataset)
    db.session.commit()

    log_user_activity(
        current_user.id,
        'dataset_deleted',
        {
            'dataset_id': dataset_id,
            'dataset_name': dataset_name
        }
    )

    flash(f'Dataset "{dataset_name}" deleted successfully.', 'success')

  except Exception as e:
    db.session.rollback()
    current_app.logger.error(f"Dataset deletion error: {str(e)}")
    flash('Error deleting dataset. Please try again.', 'error')

  return redirect(url_for('datasets.dashboard'))


@datasets_bp.route('/<int:dataset_id>/download')
@login_required
def download_dataset(dataset_id):
  """Download dataset file"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  if not dataset.file_path or not os.path.exists(dataset.file_path):
    flash('Dataset file not found.', 'error')
    return redirect(url_for('datasets.view_dataset', dataset_id=dataset.id))

  log_user_activity(
      current_user.id,
      'dataset_downloaded',
      {
          'dataset_id': dataset.id,
          'dataset_name': dataset.name
      }
  )

  return send_file(
      dataset.file_path,
      as_attachment=True,
      download_name=f"{dataset.name}_{dataset.id}.{dataset.file_path.split('.')[-1]}"
  )


@datasets_bp.route('/api/datasets')
@login_required
def api_datasets():
  """API endpoint to get user's datasets"""
  datasets = current_user.datasets.order_by(Dataset.created_at.desc()).all()

  return jsonify({
      'datasets': [dataset.to_dict() for dataset in datasets],
      'total': len(datasets)
  })


@datasets_bp.route('/api/datasets/<int:dataset_id>')
@login_required
def api_dataset_detail(dataset_id):
  """API endpoint to get dataset details"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  return jsonify(dataset.to_dict())


@datasets_bp.errorhandler(429)
def ratelimit_handler(e):
  """Handle rate limit exceeded"""
  return jsonify({
      'error': 'Rate limit exceeded',
      'message': 'Too many requests. Please try again later.'
  }), 429
