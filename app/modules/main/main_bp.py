from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from ...scripts.logging_config import log_user_action
from ...database import db
from .. import Dataset

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
  """Home page"""
  return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
  """User dashboard"""
  # Fetch user's datasets
  datasets = Dataset.query.filter_by(user_id=current_user.id).all()

  # Calculate total size across all datasets
  total_size = sum(dataset.total_size or 0 for dataset in datasets)

  return render_template('dashboard.html', datasets=datasets, total_size=total_size)
