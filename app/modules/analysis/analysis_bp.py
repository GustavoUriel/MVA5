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
    """Create a new analysis (delegator to archived implementation)"""
    from archive.archived_handlers import new_analysis as _archived_new_analysis
    return _archived_new_analysis()

@analysis_bp.route('/analysis/create', methods=['POST'])
@login_required
def create_analysis():
    """Create a new analysis (delegator to archived implementation)"""
    from archive.archived_handlers import create_analysis as _archived_create_analysis
    return _archived_create_analysis()

@analysis_bp.route('/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    """View analysis details (delegator to archived implementation)"""
    from archive.archived_handlers import view_analysis as _archived_view_analysis
    return _archived_view_analysis(analysis_id)

@analysis_bp.route('/analysis/<int:analysis_id>/edit')
@login_required
def edit_analysis(analysis_id):
    """Edit analysis (delegator to archived implementation)"""
    from archive.archived_handlers import edit_analysis as _archived_edit_analysis
    return _archived_edit_analysis(analysis_id)

@analysis_bp.route('/analysis/<int:analysis_id>/update', methods=['POST'])
@login_required
def update_analysis(analysis_id):
    """Update analysis (delegator to archived implementation)"""
    from archive.archived_handlers import update_analysis as _archived_update_analysis
    return _archived_update_analysis(analysis_id)

@analysis_bp.route('/analysis/<int:analysis_id>/delete', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    """Delete analysis (delegator to archived implementation)"""
    from archive.archived_handlers import delete_analysis as _archived_delete_analysis
    return _archived_delete_analysis(analysis_id)

@analysis_bp.route('/analysis/<int:analysis_id>/run', methods=['POST'])
@login_required
def run_analysis(analysis_id):
    """Run analysis (delegator to archived implementation)"""
    from archive.archived_handlers import run_analysis as _archived_run_analysis
    return _archived_run_analysis(analysis_id)

@analysis_bp.route('/analysis/<int:analysis_id>/report')
@login_required
def view_report(analysis_id):
    """View analysis report (delegator to archived implementation)"""
    from archive.archived_handlers import view_report as _archived_view_report
    return _archived_view_report(analysis_id)
