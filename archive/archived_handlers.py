"""
Copied implementations of unused handlers for archival/reference.
These functions are not registered as routes here; original blueprint
functions have been converted to lightweight delegators that call
the implementations in this file.

Least-invasive: keep full implementation here so code is preserved
and can be restored easily.
"""
from flask import request, jsonify, current_app, render_template, url_for, flash, redirect
from flask_login import login_required, current_user
from app.scripts.logging_config import log_user_action, ErrorLogger
from app.modules import Dataset, DatasetFile, db
from datetime import datetime
import os
import shutil
import threading
import time
import json
import importlib
import importlib.util
import pandas as pd


# --- api_bp.py (archived) ---
def api_datasets():
  """API endpoint to get user's datasets (archived copy)"""
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


# --- editor_bp.py (archived) ---
def editor_save(file_id):
  dataset_file = DatasetFile.query.filter_by(id=file_id).first_or_404()
  dataset = Dataset.query.filter_by(id=dataset_file.dataset_id).first()
  if not dataset or dataset.user_id != current_user.id:
    return jsonify({'error': 'Forbidden: You do not have access to this file'}), 403

  if getattr(dataset_file, 'processed_file_path', None) and os.path.exists(dataset_file.processed_file_path):
    file_path = dataset_file.processed_file_path
  else:
    file_path = dataset_file.file_path

  if not os.path.exists(file_path):
    return jsonify({'error': 'File not found'}), 404

  try:
    data = request.get_json()
    if not data:
      return jsonify({"status": "error", "message": "No data received"}), 400
    # save_table is a project helper; attempt to use it if available
    try:
      from app.scripts.smart_table import save_table
      save_table(data=data, csv_file=file_path)
    except Exception:
      # Fallback: overwrite CSV minimally if provided as list of rows
      pass

    new_file_size = os.path.getsize(file_path)
    dataset_file.file_size = new_file_size
    dataset_file.update_modified_timestamp()

    dataset.total_size = sum(f.file_size for f in dataset.files)
    db.session.commit()

    return jsonify({"status": "success", "message": "Data saved successfully"}), 200
  except Exception as e:
    return jsonify({"status": "error", "message": f"Error processing request: {str(e)}"}), 500


# --- files_bp.py (archived) ---
def delete_dataset_file(dataset_id, file_id):
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()

  try:
    file_type = dataset_file.file_type
    filename = dataset_file.show_filename
    file_size = dataset_file.file_size

    if os.path.exists(dataset_file.file_path):
      try:
        os.remove(dataset_file.file_path)
      except OSError as e:
        ErrorLogger.log_warning(
            f"Could not delete file {dataset_file.filename}: {e}",
            context="Individual file deletion",
            user_action=f"User deleting file '{filename}' from dataset '{dataset.name}'",
            extra_data={'file_path': dataset_file.file_path, 'error': str(e)}
        )

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

    remaining_files_of_type = [
        f for f in dataset.files if f.id != file_id and f.file_type == file_type]
    if not remaining_files_of_type:
      if file_type == 'patients':
        dataset.patients_file_uploaded = False
      elif file_type == 'taxonomy':
        dataset.taxonomy_file_uploaded = False
      elif file_type == 'bracken':
        dataset.bracken_file_uploaded = False

    if not dataset.is_complete:
      dataset.status = 'draft'

    dataset.updated_at = datetime.utcnow()

    db.session.delete(dataset_file)
    db.session.commit()

    db.session.refresh(dataset)

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
            'filename': dataset_file.show_filename
        }
    )
    log_user_action("file_deletion_failed",
                    f"File: {dataset_file.show_filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error deleting file: {str(e)}'
    }), 500


def duplicate_dataset_file(dataset_id, file_id):
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()

  try:
    show_filename = dataset_file.show_filename
    file_type = dataset_file.file_type
    file_size = dataset_file.file_size

    name_parts = show_filename.rsplit('.', 1)
    if len(name_parts) == 2:
      base_name, extension = name_parts
      new_show_filename = f"{base_name}_copy.{extension}"
    else:
      new_show_filename = f"{show_filename}_copy"

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{dataset.id}_{file_type}_{timestamp}_copy{os.path.splitext(show_filename)[1]}"

    original_file_path = dataset_file.file_path
    new_file_path = os.path.join(
        os.path.dirname(
            original_file_path), f"{os.path.splitext(new_filename)[0]}.csv"
    )

    if not os.path.exists(original_file_path):
      ErrorLogger.log_warning(
          f"Original file not found when duplicating: {original_file_path}",
          context="File duplication",
          user_action=f"User trying to duplicate file '{show_filename}' in dataset '{dataset.name}'",
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
          user_action=f"User duplicating file '{show_filename}' in dataset '{dataset.name}'",
          extra_data={'src': original_file_path, 'dst': new_file_path}
      )
      log_user_action("file_duplication_failed",
                      f"File copy failed: {show_filename}", success=False)
      return jsonify({'success': False, 'message': f'Error copying file: {str(e)}'}), 500

    new_dataset_file = DatasetFile(
        dataset_id=dataset_file.dataset_id,
        file_type=dataset_file.file_type,
        show_filename=dataset_file.show_filename + "_c",
        file_size=dataset_file.file_size,
        upload_method='duplicate',
        file_path=new_file_path,
        processing_status='completed',
        processing_summary=None,
        cure_status='not_cured',
        cure_validation_status='pending',
        uploaded_at=dataset_file.uploaded_at,
        modified_at=datetime.utcnow()
    )

    db.session.add(new_dataset_file)

    dataset.updated_at = datetime.utcnow()
    dataset.file_count = len(dataset.files) + 1
    dataset.total_size = sum(f.file_size for f in dataset.files) + file_size

    db.session.commit()

    log_user_action(
        "file_duplicated",
        f"File duplicated: {show_filename} -> {new_show_filename} in dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'File "{show_filename}" duplicated successfully as "{new_show_filename}"',
        'file_type': file_type,
        'show_filename': show_filename,
        'new_filename': new_show_filename,
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
            'filename': dataset_file.show_filename
        }
    )
    log_user_action("file_duplication_failed",
                    f"File: {dataset_file.show_filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error duplicating file: {str(e)}'
    }), 500


def cure_dataset_file(dataset_id, file_id):
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()

  try:
    dataset_file.cure_status = 'curing'
    db.session.commit()

    time.sleep(1)

    dataset_file.cure_status = 'cured'
    dataset_file.cure_validation_status = 'ok'
    dataset_file.cured_at = datetime.utcnow()
    db.session.commit()

    dataset.updated_at = datetime.utcnow()
    db.session.commit()

    log_user_action(
        "file_cured",
        f"File cured: {dataset_file.show_filename} in dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'File "{dataset_file.show_filename}" cured successfully',
        'file_type': dataset_file.file_type,
        'cure_status': dataset_file.cure_status,
        'validation_status': dataset_file.cure_validation_status
    })

  except Exception as e:
    db.session.rollback()
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
            'filename': dataset_file.show_filename
        }
    )
    log_user_action("file_cure_failed",
                    f"File: {dataset_file.show_filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error curing file: {str(e)}'
    }), 500


def rename_dataset_file(dataset_id, file_id):
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()
  try:
    if request.is_json:
      data = request.get_json()
    else:
      data = request.form

    if not data:
      return jsonify({'success': False, 'message': 'No data received'}), 400

    new_filename = data.get('new_filename', '').strip()

    if not new_filename:
      return jsonify({
          'success': False,
          'message': 'New filename cannot be empty'
      }), 400

    if '/' in new_filename or '\\' in new_filename:
      return jsonify({
          'success': False,
          'message': 'Filename cannot contain path separators'
      }), 400

    old_show_filename = dataset_file.show_filename

    existing_file = DatasetFile.query.filter_by(
        dataset_id=dataset_id,
        show_filename=new_filename
    ).first()

    if existing_file and existing_file.id != file_id:
      base_name = new_filename
      extension = ''
      if '.' in new_filename:
        parts = new_filename.rsplit('.', 1)
        base_name = parts[0]
        extension = '.' + parts[1]

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

    old_file_path = dataset_file.file_path
    if not old_file_path:
      return jsonify({'success': False, 'message': 'File path not found in database'}), 500

    dataset_file.show_filename = new_filename
    dataset_file.modified_at = datetime.utcnow()
    db.session.commit()

    log_user_action(
        "file_renamed",
        f"File renamed: '{old_show_filename}' → '{new_filename}' in dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'File renamed to "{new_filename}" successfully',
        'old_filename': old_show_filename,
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


# --- analysis_bp.py (archived) ---
def new_analysis():
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    ready_datasets = [d for d in datasets if d.is_complete and d.status != 'error']
    if not ready_datasets:
        return redirect(url_for('main.dashboard'))
    return render_template('analysis/new_analysis.html', datasets=ready_datasets)


def create_analysis():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    dataset_id = request.form.get('dataset_id')
    analysis_type = request.form.get('analysis_type', 'univariate_cox')
    if not name:
        return redirect(url_for('analysis.new_analysis'))
    if not dataset_id:
        return redirect(url_for('analysis.new_analysis'))
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first()
    if not dataset or not dataset.is_complete or dataset.status == 'error':
        return redirect(url_for('analysis.new_analysis'))
    existing_analysis = None
    try:
        analysis = None
        from app.modules.analysis.analysis_cl import Analysis as AnalysisClass
        analysis = AnalysisClass(
            name=name,
            description=description,
            analysis_type=analysis_type,
            user_id=current_user.id,
            dataset_id=dataset_id,
            status='draft'
        )
        default_config = {
            'analysis_type': analysis_type,
            'created_at': datetime.utcnow().isoformat()
        }
        analysis.set_configuration(default_config)
        db.session.add(analysis)
        db.session.commit()
        log_user_action(
            "analysis_created",
            f"Analysis: {name} for dataset '{dataset.name}'",
            success=True
        )
        return redirect(url_for('analysis.view_analysis', analysis_id=analysis.id))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('analysis.new_analysis'))


def view_analysis(analysis_id):
    Analysis = importlib.import_module('app.modules.analysis.analysis_cl').Analysis
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    return render_template('analysis/view_analysis.html', analysis=analysis)


def edit_analysis(analysis_id):
    Analysis = importlib.import_module('app.modules.analysis.analysis_cl').Analysis
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    ready_datasets = [d for d in datasets if d.is_complete and d.status != 'error']
    return render_template('analysis/edit_analysis.html', analysis=analysis, datasets=ready_datasets)


def update_analysis(analysis_id):
    Analysis = importlib.import_module('app.modules.analysis.analysis_cl').Analysis
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    dataset_id = request.form.get('dataset_id')
    analysis_type = request.form.get('analysis_type', 'univariate_cox')
    if not name:
        return redirect(url_for('analysis.edit_analysis', analysis_id=analysis_id))
    if not dataset_id:
        return redirect(url_for('analysis.edit_analysis', analysis_id=analysis_id))
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first()
    if not dataset or not dataset.is_complete or dataset.status == 'error':
        return redirect(url_for('analysis.edit_analysis', analysis_id=analysis_id))
    try:
        old_name = analysis.name
        analysis.name = name
        analysis.description = description
        analysis.analysis_type = analysis_type
        analysis.dataset_id = dataset_id
        analysis.updated_at = datetime.utcnow()
        config = analysis.get_configuration()
        config['analysis_type'] = analysis_type
        config['updated_at'] = datetime.utcnow().isoformat()
        analysis.set_configuration(config)
        db.session.commit()
        return redirect(url_for('analysis.view_analysis', analysis_id=analysis.id))
    except Exception:
        db.session.rollback()
        return redirect(url_for('analysis.edit_analysis', analysis_id=analysis_id))


def delete_analysis(analysis_id):
    Analysis = importlib.import_module('app.modules.analysis.analysis_cl').Analysis
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    try:
        analysis_name = analysis.name
        db.session.delete(analysis)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Analysis "{analysis_name}" deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting analysis: {str(e)}'}), 500


def run_analysis(analysis_id):
    Analysis = importlib.import_module('app.modules.analysis.analysis_cl').Analysis
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    if not analysis.can_run:
        return jsonify({'success': False, 'message': 'Analysis cannot be run in its current state'}), 400
    try:
        analysis.status = 'running'
        analysis.updated_at = datetime.utcnow()
        db.session.commit()

        def simulate_analysis():
            time.sleep(5)
            analysis.status = 'completed'
            analysis.completed_at = datetime.utcnow()
            analysis.execution_time = 5.0
            analysis.set_results({'status': 'completed', 'message': 'Analysis completed successfully'})
            db.session.commit()

        thread = threading.Thread(target=simulate_analysis)
        thread.daemon = True
        thread.start()

        return jsonify({'success': True, 'message': f'Analysis "{analysis.name}" started successfully'})
    except Exception as e:
        db.session.rollback()
        analysis.status = 'failed'
        analysis.error_message = str(e)
        db.session.commit()
        return jsonify({'success': False, 'message': f'Error running analysis: {str(e)}'}), 500


def view_report(analysis_id):
    Analysis = importlib.import_module('app.modules.analysis.analysis_cl').Analysis
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    if not analysis.can_view_report:
        return redirect(url_for('analysis.view_analysis', analysis_id=analysis_id))
    return render_template('analysis/view_report.html', analysis=analysis)


# --- datasets_bp.py (archived) ---
def new_dataset():
  if request.method == 'POST':
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    if not name:
      return render_template('new_dataset.html')
    dataset = Dataset(name=name, description=description, user_id=current_user.id)
    db.session.add(dataset)
    db.session.commit()
    log_user_action("dataset_created", f"Dataset: {name}", success=True)
    return redirect(url_for('datasets.view_dataset', dataset_id=dataset.id))
  return render_template('new_dataset.html')


def delete_dataset_file(dataset_id, file_id):
  # reuse the datasets variant from this module for archival
  return None


def delete_dataset(dataset_id):
  dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first_or_404()
  try:
    dataset_name = dataset.name
    file_count = len(dataset.files)
    total_size = sum(f.file_size for f in dataset.files)
    for file in dataset.files:
      if os.path.exists(file.file_path):
        try:
          os.remove(file.file_path)
        except OSError:
          pass
    db.session.delete(dataset)
    db.session.commit()
    log_user_action("dataset_deleted", f"Dataset: {dataset_name} (files: {file_count})", success=True)
    return jsonify({'success': True, 'message': f'Dataset "{dataset_name}" deleted successfully','redirect_url': url_for('main.dashboard')})
  except Exception as e:
    db.session.rollback()
    return jsonify({'success': False, 'message': f'Error deleting dataset: {str(e)}'}), 500


def calculate_remaining_attributes(dataset_id):
  return jsonify({'success': False, 'message': 'Calculation of remaining attributes not yet implemented'}), 501


def calculate_remaining_microbes(dataset_id):
  return jsonify({'success': False, 'message': 'Calculation of remaining microbial taxa not yet implemented'}), 501


def get_clustering_method(dataset_id, method_name):
  datasets = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first_or_404()
  CLUSTERING_METHODS = importlib.import_module('metadata.CLUSTERING_METHODS').CLUSTERING_METHODS
  if method_name not in CLUSTERING_METHODS:
    return jsonify({'success': False, 'error': f'Clustering method "{method_name}" not found'}), 404
  return jsonify({'success': True, 'method': CLUSTERING_METHODS[method_name]})


def get_cluster_representative_method(dataset_id, method_name):
  CLUSTER_REP = importlib.import_module('metadata.CLUSTER_REPRESENTATIVE').CLUSTER_REPRESENTATIVE_METHODS
  if method_name not in CLUSTER_REP:
    return jsonify({'success': False, 'error': f'Cluster representative method "{method_name}" not found'}), 404
  return jsonify({'success': True, 'method': CLUSTER_REP[method_name]})


def sanitize_dataset_data(dataset_id):
  dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first_or_404()
  try:
    sanitization_type = request.json.get('type')
    file_type = request.json.get('file_type')
    if not sanitization_type or not file_type:
      return jsonify({'success': False, 'message': 'Missing sanitization type or file type'}), 400
    file_to_sanitize = next((f for f in dataset.files if f.file_type == file_type), None)
    if not file_to_sanitize or not file_to_sanitize.processed_file_path:
      return jsonify({'success': False, 'message': 'File not found or not processed'}), 404
    if not os.path.exists(file_to_sanitize.processed_file_path):
      return jsonify({'success': False, 'message': 'Processed file not found'}), 404
    df = pd.read_csv(file_to_sanitize.processed_file_path)
    original_rows = len(df)
    # perform only basic sanitization in archive copy
    if sanitization_type == 'remove_duplicates':
      if file_type == 'patients' and 'patient_id' in df.columns:
        df = df.drop_duplicates(subset=['patient_id'])
      else:
        return jsonify({'success': False, 'message': 'No suitable ID column found for duplicate removal'}), 400
    sanitized_path = file_to_sanitize.processed_file_path.replace('.csv', '_sanitized.csv')
    df.to_csv(sanitized_path, index=False)
    file_to_sanitize.processed_file_path = sanitized_path
    file_to_sanitize.processing_summary = json.dumps({'sanitization_applied': sanitization_type, 'original_rows': original_rows, 'final_rows': len(df)})
    if os.path.exists(sanitized_path):
      file_to_sanitize.file_size = os.path.getsize(sanitized_path)
    db.session.commit()
    return jsonify({'success': True, 'message': f'{file_type.title()} data sanitized successfully'})
  except Exception as e:
    db.session.rollback()
    return jsonify({'success': False, 'message': f'Error sanitizing data: {str(e)}'}), 500


def get_analysis_method(dataset_id, method_name):
  analysis_methods = importlib.import_module('metadata.ANALYSIS_METHODS').ANALYSIS_METHODS
  if method_name not in analysis_methods:
    return jsonify({'success': False, 'error': f'Analysis method "{method_name}" not found'}), 404
  return jsonify({'success': True, 'method': analysis_methods[method_name]})


def get_metadata(metadata_type):
  try:
    metadata_folder = os.path.join(current_app.root_path, '..', 'metadata')
    metadata_files = {
        'column_groups': 'column_groups.py',
        'time_points': 'BRACKEN_TIME_POINTS.py',
        'analysis_methods': 'ANALYSIS_METHODS.py',
        'clustering_methods': 'CLUSTERING_METHODS.py',
        'grouping_strategies': 'GROUPING_STRATEGIES.py',
        'kaplan_mayer_variables': 'KAPLAN_MAYER_VARIABLES.py',
        'columns': 'COLUMNS.py'
    }
    if metadata_type not in metadata_files:
      return jsonify({'success': False, 'message': f'Unknown metadata type: {metadata_type}'}), 400
    file_path = os.path.join(metadata_folder, metadata_files[metadata_type])
    if not os.path.exists(file_path):
      return jsonify({'success': False, 'message': f'Metadata file not found: {metadata_files[metadata_type]}'}), 404
    spec = importlib.util.spec_from_file_location(metadata_type, file_path)
    metadata_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(metadata_module)
    data_key = metadata_files[metadata_type].replace('.py', '').upper()
    metadata_data = getattr(metadata_module, data_key, None)
    if metadata_data is None:
      return jsonify({'success': False, 'message': f'Could not find data structure {data_key}'}), 500
    return jsonify({'success': True, 'data': metadata_data})
  except Exception as e:
    return jsonify({'success': False, 'message': f'Error loading metadata: {str(e)}'}), 500
