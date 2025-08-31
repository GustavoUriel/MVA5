"""
WSGI Configuration for PythonAnywhere Deployment
"""

from app import create_app
import sys
import os

# Add your project directory to the Python path
project_home = '/home/yourusername/microbiome_app'
if project_home not in sys.path:
  sys.path = [project_home] + sys.path

application = create_app()

if __name__ == "__main__":
  application.run()
