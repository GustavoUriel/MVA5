"""
Celery Tasks for Analysis and Background Processing
"""
from celery import Celery
from extensions import celery_app, db
from models import Dataset, AnalysisJob
from datetime import datetime
import pandas as pd
import os
import json


@celery_app.task(bind=True)
def process_dataset_upload(self, dataset_id, file_path):
  """Process uploaded dataset file"""
  try:
    # Update task status
    job = AnalysisJob.query.filter_by(celery_task_id=self.request.id).first()
    if job:
      job.status = 'running'
      db.session.commit()

    # Get dataset
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
      raise ValueError(f"Dataset {dataset_id} not found")

    # Process file based on extension
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == '.csv':
      df = pd.read_csv(file_path)
    elif file_ext == '.tsv':
      df = pd.read_csv(file_path, sep='\t')
    elif file_ext == '.xlsx':
      df = pd.read_excel(file_path)
    elif file_ext == '.json':
      df = pd.read_json(file_path)
    else:
      # Try to read as text file
      with open(file_path, 'r') as f:
        content = f.read()
      df = pd.DataFrame({'content': [content]})

    # Generate basic metadata
    metadata = {
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'file_size': os.path.getsize(file_path),
        'processed_at': datetime.utcnow().isoformat(),
        'summary': {
            'numeric_columns': len(df.select_dtypes(include=['number']).columns),
            'text_columns': len(df.select_dtypes(include=['object']).columns),
            'missing_values': df.isnull().sum().to_dict()
        }
    }

    # Update dataset
    dataset.status = 'ready'
    dataset.metadata_info = metadata
    dataset.updated_at = datetime.utcnow()

    # Update job
    if job:
      job.status = 'completed'
      job.completed_at = datetime.utcnow()
      job.results = {'metadata': metadata}

    db.session.commit()

    return {
        'status': 'success',
        'dataset_id': dataset_id,
        'metadata': metadata
    }

  except Exception as e:
    # Update dataset and job status on error
    dataset = Dataset.query.get(dataset_id)
    if dataset:
      dataset.status = 'error'
      db.session.commit()

    job = AnalysisJob.query.filter_by(celery_task_id=self.request.id).first()
    if job:
      job.status = 'failed'
      job.completed_at = datetime.utcnow()
      job.error_message = str(e)
      db.session.commit()

    # Re-raise the exception to mark task as failed
    raise


@celery_app.task(bind=True)
def perform_analysis(self, dataset_id, analysis_type, parameters=None):
  """Perform various types of analysis on dataset"""
  try:
    # Get dataset
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
      raise ValueError(f"Dataset {dataset_id} not found")

    if not dataset.file_path or not os.path.exists(dataset.file_path):
      raise ValueError("Dataset file not found")

    # Create analysis job
    job = AnalysisJob(
        dataset_id=dataset_id,
        job_type=analysis_type,
        status='running',
        celery_task_id=self.request.id,
        started_at=datetime.utcnow(),
        parameters=parameters
    )
    db.session.add(job)
    db.session.commit()

    # Load data
    file_ext = os.path.splitext(dataset.file_path)[1].lower()

    if file_ext == '.csv':
      df = pd.read_csv(dataset.file_path)
    elif file_ext == '.tsv':
      df = pd.read_csv(dataset.file_path, sep='\t')
    elif file_ext == '.xlsx':
      df = pd.read_excel(dataset.file_path)
    else:
      raise ValueError(f"Unsupported file format: {file_ext}")

    # Perform analysis based on type
    results = {}

    if analysis_type == 'basic_stats':
      results = {
          'shape': df.shape,
          'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
          'missing_values': df.isnull().sum().to_dict(),
          'numeric_summary': df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {},
          'unique_values': {col: df[col].nunique() for col in df.columns}
      }

    elif analysis_type == 'correlation_analysis':
      numeric_df = df.select_dtypes(include=['number'])
      if len(numeric_df.columns) > 1:
        correlation_matrix = numeric_df.corr()
        results = {
            'correlation_matrix': correlation_matrix.to_dict(),
            'high_correlations': []
        }

        # Find high correlations
        for i in range(len(correlation_matrix.columns)):
          for j in range(i+1, len(correlation_matrix.columns)):
            corr_value = correlation_matrix.iloc[i, j]
            if abs(corr_value) > 0.7:  # High correlation threshold
              results['high_correlations'].append({
                  'var1': correlation_matrix.columns[i],
                  'var2': correlation_matrix.columns[j],
                  'correlation': corr_value
              })
      else:
        results = {'error': 'Not enough numeric columns for correlation analysis'}

    # Add more analysis types here as needed

    # Update job
    job.status = 'completed'
    job.completed_at = datetime.utcnow()
    job.results = results
    db.session.commit()

    return {
        'status': 'success',
        'job_id': job.id,
        'results': results
    }

  except Exception as e:
    # Update job status on error
    job = AnalysisJob.query.filter_by(celery_task_id=self.request.id).first()
    if job:
      job.status = 'failed'
      job.completed_at = datetime.utcnow()
      job.error_message = str(e)
      db.session.commit()

    raise


@celery_app.task
def cleanup_old_files():
  """Clean up old uploaded files and logs"""
  try:
    from datetime import timedelta

    # Clean up datasets older than 30 days with no activity
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    old_datasets = Dataset.query.filter(
        Dataset.updated_at < cutoff_date,
        Dataset.status == 'ready'
    ).all()

    for dataset in old_datasets:
      if dataset.file_path and os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
      dataset.file_path = None
      dataset.status = 'archived'

    db.session.commit()

    return f"Cleaned up {len(old_datasets)} old datasets"

  except Exception as e:
    return f"Error during cleanup: {str(e)}"


@celery_app.task
def send_notification_email(user_email, subject, message):
  """Send notification email to user"""
  # This is a placeholder for email functionality
  # In a real application, you would integrate with an email service
  try:
    # Log the email instead of sending for now
    with open('email_log.txt', 'a') as f:
      f.write(
          f"{datetime.utcnow()}: TO={user_email}, SUBJECT={subject}, MESSAGE={message}\n")

    return f"Email notification logged for {user_email}"

  except Exception as e:
    return f"Error sending email: {str(e)}"
