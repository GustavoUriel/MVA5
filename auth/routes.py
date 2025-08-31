"""
Authentication Blueprint
Google OAuth integration and user management
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from extensions import db, limiter
from models import User, UserLog
from utils.logging_config import log_user_activity
from datetime import datetime
import requests
import secrets


auth_bp = Blueprint('auth', __name__)

# Initialize OAuth
oauth = OAuth()


def init_oauth(app):
  """Initialize OAuth with app configuration"""
  oauth.init_app(app)

  client_id = app.config.get('GOOGLE_CLIENT_ID')
  client_secret = app.config.get('GOOGLE_CLIENT_SECRET')

  if not client_id or not client_secret:
    app.logger.error('Google OAuth client ID/secret not configured')
    return None

  try:
    google = oauth.register(
        name='google',
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    return google
  except Exception as e:
    app.logger.exception('Failed to register Google OAuth client')
    return None


@auth_bp.route('/login')
@limiter.limit("10 per minute")
def login():
  """Login page"""
  if current_user.is_authenticated:
    return redirect(url_for('datasets.dashboard'))
  return render_template('auth/login.html')


@auth_bp.route('/authorize')
@limiter.limit("5 per minute")
def authorize():
  """Initiate Google OAuth flow"""
  from flask import current_app
  # Generate state for CSRF protection and initiate redirect
  state = secrets.token_urlsafe(32)
  session['oauth_state'] = state

  google = init_oauth(current_app)
  redirect_uri = url_for('auth.callback', _external=True)
  if google is None:
    current_app.logger.error(
        'Google OAuth client not configured; cannot start authorization flow')
    flash('Authentication is not configured on this server. Contact the administrator.', 'error')
    return redirect(url_for('auth.login'))

  try:
    return google.authorize_redirect(redirect_uri=redirect_uri, state=state)
  except Exception as e:
    current_app.logger.error(f"OAuth authorization error: {str(e)}")
    flash('Authentication error. Please try again.', 'error')
    return redirect(url_for('auth.login'))


@auth_bp.route('/callback')
@limiter.limit("5 per minute")
def callback():
  """Handle Google OAuth callback"""
  from flask import current_app

  # Verify state parameter
  state = request.args.get('state')
  if not state or state != session.pop('oauth_state', None):
    flash('Invalid state parameter. Please try again.', 'error')
    return redirect(url_for('auth.login'))

  google = init_oauth(current_app)

  if google is None:
    current_app.logger.error(
        'Google OAuth client not configured; callback cannot proceed')
    flash('Authentication is not configured on this server. Contact the administrator.', 'error')
    return redirect(url_for('auth.login'))

  try:
    # Get token from Google
    token = google.authorize_access_token()

    # Get user info from Google userinfo endpoint
    try:
      resp = google.get('userinfo')
      user_info = resp.json()
    except Exception:
      # Fallback to token claims if available
      user_info = token.get('userinfo') or token.get('id_token') or {}

    if not user_info or not user_info.get('email'):
      flash('Unable to get user information from Google. Please try again.', 'error')
      return redirect(url_for('auth.login'))

    # Find or create user
    user = User.query.filter_by(email=user_info['email']).first()

    if not user:
      # Create new user
      user = User(
          email=user_info['email'],
          name=user_info.get('name', user_info['email']),
          google_id=user_info.get('sub'),
          profile_picture=user_info.get('picture')
      )
      db.session.add(user)
      db.session.commit()

      log_user_activity(
          user.id,
          'user_registered',
          {
              'email': user.email,
              'name': user.name,
              'google_id': user.google_id
          }
      )
    else:
      # Update existing user info
      user.name = user_info.get('name', user.name)
      user.google_id = user_info.get('sub', user.google_id)
      user.profile_picture = user_info.get('picture', user.profile_picture)

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Log the user in
    login_user(user, remember=True)

    log_user_activity(
        user.id,
        'user_login',
        {
            'email': user.email,
            'login_method': 'google_oauth'
        }
    )

    flash(f'Welcome, {user.name}!', 'success')

    # Redirect to originally requested page or dashboard
    next_page = session.pop('next_page', None)
    return redirect(next_page or url_for('datasets.dashboard'))

  except Exception as e:
    current_app.logger.error(f"OAuth callback error: {str(e)}")
    flash('Authentication failed. Please try again.', 'error')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
  """Logout user"""
  log_user_activity(
      current_user.id,
      'user_logout',
      {'email': current_user.email}
  )

  logout_user()
  session.clear()
  flash('You have been logged out successfully.', 'info')
  return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
  """User profile page"""
  log_user_activity(
      current_user.id,
      'profile_viewed',
      {'email': current_user.email}
  )

  return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/delete_account', methods=['POST'])
@login_required
@limiter.limit("1 per day")
def delete_account():
  """Delete user account and all associated data"""
  user_id = current_user.id
  user_email = current_user.email

  try:
    # Log the account deletion
    log_user_activity(
        user_id,
        'account_deleted',
        {'email': user_email}
    )

    # Delete user (cascades to datasets and logs)
    db.session.delete(current_user)
    db.session.commit()

    logout_user()
    session.clear()

    flash('Your account has been permanently deleted.', 'info')
    return redirect(url_for('auth.login'))

  except Exception as e:
    db.session.rollback()
    current_app.logger.error(f"Account deletion error: {str(e)}")
    flash('Error deleting account. Please try again.', 'error')
    return redirect(url_for('auth.profile'))


@auth_bp.errorhandler(429)
def ratelimit_handler(e):
  """Handle rate limit exceeded"""
  return jsonify({
      'error': 'Rate limit exceeded',
      'message': 'Too many requests. Please try again later.'
  }), 429
