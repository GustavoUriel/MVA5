from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from ...database import db
from ..datasets.dataset_cl import Dataset
from .analysis_cl import Analysis
from ...scripts.logging_config import log_user_action
from datetime import datetime

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analysis/new')
@login_required
def new_analysis():
    """Create a new analysis"""
    # Get user's datasets that are ready for analysis
    # A dataset is ready if it has all required files uploaded (is_complete=True)
    # and is not in error status
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    ready_datasets = [d for d in datasets if d.is_complete and d.status != 'error']
    
    if not ready_datasets:
        flash('You need at least one complete dataset (with all required files uploaded) to create an analysis.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    return render_template('analysis/new_analysis.html', datasets=ready_datasets)

@analysis_bp.route('/analysis/create', methods=['POST'])
@login_required
def create_analysis():
    """Create a new analysis"""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    dataset_id = request.form.get('dataset_id')
    analysis_type = request.form.get('analysis_type', 'univariate_cox')
    
    # Validate required fields
    if not name:
        flash('Analysis name is required.', 'error')
        return redirect(url_for('analysis.new_analysis'))
    
    if not dataset_id:
        flash('Please select a dataset.', 'error')
        return redirect(url_for('analysis.new_analysis'))
    
    # Verify dataset belongs to user and is ready for analysis
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first()
    if not dataset or not dataset.is_complete or dataset.status == 'error':
        flash('Selected dataset is not available for analysis. Please ensure all required files are uploaded.', 'error')
        return redirect(url_for('analysis.new_analysis'))
    
    # Check if analysis name already exists for this user
    existing_analysis = Analysis.query.filter_by(
        name=name, 
        user_id=current_user.id
    ).first()
    
    if existing_analysis:
        flash('An analysis with this name already exists. Please choose a different name.', 'error')
        return redirect(url_for('analysis.new_analysis'))
    
    try:
        # Create new analysis
        analysis = Analysis(
            name=name,
            description=description,
            analysis_type=analysis_type,
            user_id=current_user.id,
            dataset_id=dataset_id,
            status='draft'
        )
        
        # Set default configuration
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
        
        flash(f'Analysis "{name}" created successfully!', 'success')
        return redirect(url_for('analysis.view_analysis', analysis_id=analysis.id))
        
    except Exception as e:
        db.session.rollback()
        log_user_action("analysis_creation_failed", f"Analysis: {name}", success=False)
        flash(f'Error creating analysis: {str(e)}', 'error')
        return redirect(url_for('analysis.new_analysis'))

@analysis_bp.route('/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    """View analysis details"""
    analysis = Analysis.query.filter_by(
        id=analysis_id, 
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('analysis/view_analysis.html', analysis=analysis)

@analysis_bp.route('/analysis/<int:analysis_id>/edit')
@login_required
def edit_analysis(analysis_id):
    """Edit analysis"""
    analysis = Analysis.query.filter_by(
        id=analysis_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # Get user's datasets that are ready for analysis
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    ready_datasets = [d for d in datasets if d.is_complete and d.status != 'error']
    
    return render_template('analysis/edit_analysis.html', 
                         analysis=analysis, 
                         datasets=ready_datasets)

@analysis_bp.route('/analysis/<int:analysis_id>/update', methods=['POST'])
@login_required
def update_analysis(analysis_id):
    """Update analysis"""
    analysis = Analysis.query.filter_by(
        id=analysis_id, 
        user_id=current_user.id
    ).first_or_404()
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    dataset_id = request.form.get('dataset_id')
    analysis_type = request.form.get('analysis_type', 'univariate_cox')
    
    # Validate required fields
    if not name:
        flash('Analysis name is required.', 'error')
        return redirect(url_for('analysis.edit_analysis', analysis_id=analysis_id))
    
    if not dataset_id:
        flash('Please select a dataset.', 'error')
        return redirect(url_for('analysis.edit_analysis', analysis_id=analysis_id))
    
    # Verify dataset belongs to user and is ready for analysis
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first()
    if not dataset or not dataset.is_complete or dataset.status == 'error':
        flash('Selected dataset is not available for analysis. Please ensure all required files are uploaded.', 'error')
        return redirect(url_for('analysis.edit_analysis', analysis_id=analysis_id))
    
    # Check if analysis name already exists for this user (excluding current analysis)
    existing_analysis = Analysis.query.filter(
        Analysis.name == name,
        Analysis.user_id == current_user.id,
        Analysis.id != analysis_id
    ).first()
    
    if existing_analysis:
        flash('An analysis with this name already exists. Please choose a different name.', 'error')
        return redirect(url_for('analysis.edit_analysis', analysis_id=analysis_id))
    
    try:
        # Update analysis
        old_name = analysis.name
        analysis.name = name
        analysis.description = description
        analysis.analysis_type = analysis_type
        analysis.dataset_id = dataset_id
        analysis.updated_at = datetime.utcnow()
        
        # Update configuration
        config = analysis.get_configuration()
        config['analysis_type'] = analysis_type
        config['updated_at'] = datetime.utcnow().isoformat()
        analysis.set_configuration(config)
        
        db.session.commit()
        
        log_user_action(
            "analysis_updated",
            f"Analysis: {old_name} -> {name}",
            success=True
        )
        
        flash(f'Analysis "{name}" updated successfully!', 'success')
        return redirect(url_for('analysis.view_analysis', analysis_id=analysis.id))
        
    except Exception as e:
        db.session.rollback()
        log_user_action("analysis_update_failed", f"Analysis: {analysis.name}", success=False)
        flash(f'Error updating analysis: {str(e)}', 'error')
        return redirect(url_for('analysis.edit_analysis', analysis_id=analysis_id))

@analysis_bp.route('/analysis/<int:analysis_id>/delete', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    """Delete analysis"""
    analysis = Analysis.query.filter_by(
        id=analysis_id, 
        user_id=current_user.id
    ).first_or_404()
    
    try:
        analysis_name = analysis.name
        db.session.delete(analysis)
        db.session.commit()
        
        log_user_action(
            "analysis_deleted",
            f"Analysis: {analysis_name}",
            success=True
        )
        
        return jsonify({
            'success': True,
            'message': f'Analysis "{analysis_name}" deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        log_user_action("analysis_deletion_failed", f"Analysis: {analysis.name}", success=False)
        return jsonify({
            'success': False,
            'message': f'Error deleting analysis: {str(e)}'
        }), 500

@analysis_bp.route('/analysis/<int:analysis_id>/run', methods=['POST'])
@login_required
def run_analysis(analysis_id):
    """Run analysis"""
    analysis = Analysis.query.filter_by(
        id=analysis_id, 
        user_id=current_user.id
    ).first_or_404()
    
    if not analysis.can_run:
        return jsonify({
            'success': False,
            'message': 'Analysis cannot be run in its current state'
        }), 400
    
    try:
        # Update analysis status
        analysis.status = 'running'
        analysis.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_user_action(
            "analysis_started",
            f"Analysis: {analysis.name}",
            success=True
        )
        
        # TODO: Implement actual analysis execution
        # For now, simulate completion after a delay
        import threading
        import time
        
        def simulate_analysis():
            time.sleep(5)  # Simulate analysis time
            analysis.status = 'completed'
            analysis.completed_at = datetime.utcnow()
            analysis.execution_time = 5.0
            analysis.set_results({'status': 'completed', 'message': 'Analysis completed successfully'})
            db.session.commit()
        
        thread = threading.Thread(target=simulate_analysis)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Analysis "{analysis.name}" started successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        analysis.status = 'failed'
        analysis.error_message = str(e)
        db.session.commit()
        
        log_user_action("analysis_run_failed", f"Analysis: {analysis.name}", success=False)
        return jsonify({
            'success': False,
            'message': f'Error running analysis: {str(e)}'
        }), 500

@analysis_bp.route('/analysis/<int:analysis_id>/report')
@login_required
def view_report(analysis_id):
    """View analysis report"""
    analysis = Analysis.query.filter_by(
        id=analysis_id, 
        user_id=current_user.id
    ).first_or_404()
    
    if not analysis.can_view_report:
        flash('Analysis report is not available yet.', 'warning')
        return redirect(url_for('analysis.view_analysis', analysis_id=analysis_id))
    
    return render_template('analysis/view_report.html', analysis=analysis)
