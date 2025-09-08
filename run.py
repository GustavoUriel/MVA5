"""
Main Flask application entry point for MVA5
Author: MVA5 Development Team
Date: 2025
"""

from app.app import create_app
import sys
sys.path.insert(0, '.')


app = create_app()

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5005, debug=True)
