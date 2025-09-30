from datetime import datetime, timedelta
from app.database import db
import json


class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Status: draft, running, completed, failed, cancelled
    status = db.Column(db.String(50), default='draft', nullable=False)
    
    # Type of analysis: e.g., 'univariate_cox', 'pls_da', 'xgboost', 'mva_model'
    analysis_type = db.Column(db.String(100), nullable=True) 
    
    # Configuration for the analysis (JSON)
    configuration = db.Column(db.Text) 
    
    # Results of the analysis (JSON)
    results = db.Column(db.Text)
    
    # Visualization data (JSON or path to files)
    visualization_data = db.Column(db.Text)
    
    # Report data (JSON or path to file)
    report_data = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Performance metrics
    execution_time = db.Column(db.Float) # in seconds
    
    # Error handling
    error_message = db.Column(db.Text)
    warnings = db.Column(db.Text) # JSON string for multiple warnings
    
    # Sharing and publication
    is_public = db.Column(db.Boolean, default=False)
    publication_ready = db.Column(db.Boolean, default=False)
    tags = db.Column(db.Text) # JSON string for tags

    # Relationships
    user = db.relationship('User', backref='analyses', lazy=True)
    dataset = db.relationship('Dataset', backref='analyses', lazy=True)

    def __repr__(self):
        return f'<Analysis {self.name} (ID: {self.id})>'

    @property
    def duration_display(self):
        if self.execution_time is not None:
            minutes, seconds = divmod(self.execution_time, 60)
            return f"{int(minutes)}m {int(seconds)}s"
        return None

    @property
    def can_run(self):
        return self.status in ['draft', 'failed', 'completed'] # Can re-run if draft, failed, or completed

    @property
    def can_view_report(self):
        return self.status == 'completed' and self.report_data is not None

    def set_configuration(self, config_dict):
        self.configuration = json.dumps(config_dict)

    def get_configuration(self):
        return json.loads(self.configuration) if self.configuration else {}

    def set_results(self, results_dict):
        self.results = json.dumps(results_dict)

    def get_results(self):
        return json.loads(self.results) if self.results else {}

    def set_warnings(self, warnings_list):
        self.warnings = json.dumps(warnings_list)

    def get_warnings(self):
        return json.loads(self.warnings) if self.warnings else []
