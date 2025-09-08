from flask import Blueprint, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from ...scripts.logging_config import log_user_action, ErrorLogger, PerformanceTracker
from .. import User, db
from datetime import datetime
import requests

auth_bp = Blueprint('auth', __name__)

# OAuth setup - google OAuth client is available as current_app.google


@auth_bp.route('/auth/login')
def login():
  """Initiate Google OAuth login"""
  if current_user.is_authenticated:
    return redirect(url_for('main.dashboard'))

  # Check if OAuth is properly configured
  if (current_app.config['GOOGLE_CLIENT_ID'] == 'dummy-client-id' or
          current_app.config['GOOGLE_CLIENT_SECRET'] == 'dummy-client-secret'):
    ErrorLogger.log_warning(
        "OAuth not configured - using dummy credentials",
        context="Google OAuth login attempt",
        user_action="User trying to log in with Google",
        extra_data={
            'oauth_provider': 'google',
            'client_id_configured': current_app.config['GOOGLE_CLIENT_ID'] != 'dummy-client-id',
            'client_secret_configured': current_app.config['GOOGLE_CLIENT_SECRET'] != 'dummy-client-secret'
        }
    )
    log_user_action("oauth_config_error",
                    "OAuth not properly configured", success=False)
    flash('Google OAuth is not configured. Please set up GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your environment variables.', 'error')
    return redirect(url_for('main.index'))

  try:
    with PerformanceTracker("oauth_initiate", "Google OAuth redirect"):
      redirect_uri = url_for('auth.auth_callback', _external=True)
      result = current_app.google.authorize_redirect(redirect_uri)
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
    current_app.logger.error(f'OAuth configuration error: {e}')
    flash('Authentication service is not available. Please try again later.', 'error')
    return redirect(url_for('main.index'))


@auth_bp.route('/auth/login/authorized')
def auth_callback():
  """Handle Google OAuth callback"""
  # Check if OAuth is properly configured first
  if (current_app.config['GOOGLE_CLIENT_ID'] == 'dummy-client-id' or
          current_app.config['GOOGLE_CLIENT_SECRET'] == 'dummy-client-secret'):
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
    return redirect(url_for('main.index'))

  try:
    with PerformanceTracker("oauth_callback", "Google OAuth token exchange"):
      # Get the authorization code from the request
      code = request.args.get('code')
      if not code:
        raise ValueError("No authorization code received")

      # Exchange code for access token manually
      token_url = 'https://oauth2.googleapis.com/token'
      token_data = {
          'client_id': current_app.config['GOOGLE_CLIENT_ID'],
          'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
          'code': code,
          'grant_type': 'authorization_code',
          'redirect_uri': url_for('auth.auth_callback', _external=True)
      }
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
      return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
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
    current_app.logger.error(f'OAuth error: {e}')
    flash('Authentication failed. Please try again.', 'error')

  return redirect(url_for('main.index'))


@auth_bp.route('/auth/logout')
@login_required
def logout():
  """Logout user"""
  try:
    user_email = current_user.email if current_user.is_authenticated else 'unknown'
    logout_user()
    log_user_action(
        "user_logout", f"User logged out: {user_email}", success=True)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
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
    return redirect(url_for('main.index'))
