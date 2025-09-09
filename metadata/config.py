# Flask Application Configuration
import os
from datetime import timedelta


class Config:
  # Basic Flask settings
  SECRET_KEY = os.environ.get('SECRET_KEY')
  WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')

  # Database settings
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_ENGINE_OPTIONS = {
      'pool_pre_ping': True,
      'pool_recycle': 300,
      'pool_timeout': 20,
      'max_overflow': 0
  }

  # Session settings
  PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
  SESSION_COOKIE_SECURE = os.environ.get(
      'SESSION_COOKIE_SECURE', 'False').lower() == 'true'
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SAMESITE = 'Lax'

  # File upload settings
  MAX_CONTENT_LENGTH = int(os.environ.get(
      'MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
  UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
  ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}

  # OAuth settings
  GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
  GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
  GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')

  # Redis settings
  REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

  # Celery settings
  CELERY_BROKER_URL = os.environ.get(
      'CELERY_BROKER_URL', 'redis://localhost:6379/0')
  CELERY_RESULT_BACKEND = os.environ.get(
      'CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

  # Mail settings
  MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
  MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
  MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

  # Logging settings
  LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
  LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
  # Toggle detailed per-function logging (set True for debug/testing)
  LOG_VERBOSE_FUNCTIONS = os.environ.get(
      'LOG_VERBOSE_FUNCTIONS', 'False').lower() == 'true'
  # Maximum characters per log entry (sanitization truncates longer entries)
  LOG_MAX_ENTRY_LENGTH = int(os.environ.get('LOG_MAX_ENTRY_LENGTH', 2000))
  # Per-user log rotation settings
  LOG_ROTATE_BYTES = int(os.environ.get(
      'LOG_ROTATE_BYTES', 10 * 1024 * 1024))  # 10MB
  LOG_ROTATE_BACKUP_COUNT = int(os.environ.get('LOG_ROTATE_BACKUP_COUNT', 5))

  # Rate limiting
  RATELIMIT_STORAGE_URL = os.environ.get(
      'RATELIMIT_STORAGE_URL', 'redis://localhost:6379/1')

  # API settings
  API_VERSION = os.environ.get('API_VERSION', 'v1')
  API_PREFIX = os.environ.get('API_PREFIX', '/api/v1')

  # Data Processing settings
  CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', 1000))
  MAX_WORKERS = int(os.environ.get('MAX_WORKERS', 4))
  CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 3600))

  # Security settings
  ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
  JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
  AUDIT_LOG_ENABLED = os.environ.get(
      'AUDIT_LOG_ENABLED', 'True').lower() == 'true'

  # Performance settings
  MAX_CONCURRENT_USERS = int(os.environ.get('MAX_CONCURRENT_USERS', 100))
  DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', 10))
  DB_MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', 20))


class DevelopmentConfig(Config):
  DEBUG = True
  TESTING = False

  # Allow default secrets for development only
  SECRET_KEY = os.environ.get(
      'SECRET_KEY') or 'dev-secret-key-change-in-production'
  WTF_CSRF_SECRET_KEY = os.environ.get(
      'WTF_CSRF_SECRET_KEY') or 'csrf-secret-key'


class ProductionConfig(Config):
  DEBUG = False
  TESTING = False

  # Require environment variables in production
  def __init__(self):
    if not self.SECRET_KEY:
      raise ValueError(
          "SECRET_KEY environment variable must be set in production")
    if not self.WTF_CSRF_SECRET_KEY:
      raise ValueError(
          "WTF_CSRF_SECRET_KEY environment variable must be set in production")

  SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
  TESTING = True
  SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
  WTF_CSRF_ENABLED = False



# Data Quality Thresholds
DATA_QUALITY_THRESHOLDS = {
    'missing_data_threshold': 0.3,  # 30% missing data threshold
    'outlier_std_threshold': 3,     # 3 standard deviations for outlier detection
    'correlation_threshold': 0.8,   # High correlation threshold
    'variance_threshold': 0.01      # Low variance threshold
}

# User Roles and Permissions
USER_ROLES = {
    'admin': {
        'permissions': ['read', 'write', 'delete', 'admin', 'manage_users'],
        'description': 'Full system access'
    },
    'researcher': {
        'permissions': ['read', 'write', 'share'],
        'description': 'Can create and share analyses'
    },
    'analyst': {
        'permissions': ['read', 'write'],
        'description': 'Can perform analyses'
    },
    'viewer': {
        'permissions': ['read'],
        'description': 'Read-only access'
    }
}


# Data Processing Configuration
DATA_PROCESSING_CONFIG = {
    'missing_value_strategies': {
        'numerical': ['mean', 'median', 'mode', 'interpolation', 'knn'],
        'categorical': ['mode', 'constant', 'unknown']
    },
    'outlier_detection_methods': ['iqr', 'zscore', 'isolation_forest', 'local_outlier_factor'],
    'normalization_methods': ['standardization', 'min_max', 'robust', 'quantile'],
    'feature_selection_methods': ['univariate', 'recursive', 'lasso', 'random_forest']
}

# Visualization Configuration
VISUALIZATION_CONFIG = {
    'color_palettes': {
        'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
        'colorblind_friendly': ['#0173b2', '#de8f05', '#029e73', '#cc78bc', '#ca9161'],
        'grayscale': ['#000000', '#444444', '#888888', '#bbbbbb', '#eeeeee']
    },
    'plot_dimensions': {
        'default_width': 800,
        'default_height': 600,
        'thumbnail_width': 200,
        'thumbnail_height': 150
    }
}

# identification_fields
in_patients_table = ['age', 'gender', 'race', 'ethnicity']
# identification_fields
in_taxonomy_table = ['taxonomy', 'domain', 'phylum']


# field_names
# duration_field_in_patients_table = 'Duration_PFSDuration_Survival'



# Advanced Statistical Configuration
SURVIVAL_ANALYSIS_CONFIG = {
    'default_confidence_level': 0.95,
    'default_alpha': 0.05,
    'rmst_tau_options': [12, 24, 36, 60],  # months
    'cox_penalizer_range': [0.01, 0.1, 1.0],
    'bootstrap_iterations': 1000
}

# Microbiome Analysis Configuration
MICROBIOME_CONFIG = {
    'alpha_diversity_metrics': ['shannon', 'simpson', 'chao1', 'observed_otus'],
    'beta_diversity_metrics': ['bray_curtis', 'jaccard', 'weighted_unifrac', 'unweighted_unifrac'],
    'differential_abundance_methods': ['deseq2', 'edger', 'ancom', 'aldex2'],
    'normalization_methods': ['tss', 'css', 'tmm', 'rle'],
    'minimum_prevalence': 0.1,  # 10% prevalence threshold
    'minimum_abundance': 0.001  # 0.1% abundance threshold
}

# File Processing Configuration
FILE_PROCESSING_CONFIG = {
    'excel_sheet_names': {
        'patients': ['patients', 'patient_data', 'clinical_data'],
        'taxonomy': ['taxonomy', 'taxa', 'taxonomies'],
        'bracken': ['bracken', 'abundance', 'counts']
    },
    'date_formats': ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S'],
    'encoding_options': ['utf-8', 'latin-1', 'cp1252'],
    'delimiter_options': [',', ';', '\t', '|']
}

# Validation Rules Configuration
VALIDATION_RULES = {
    'patient_id': {
        'pattern': r'^[A-Za-z0-9_-]+$',
        'min_length': 3,
        'max_length': 50
    },
    'age': {
        'min_value': 0,
        'max_value': 120
    },
    'duration_pfs': {
        'min_value': 0,
        'max_value': 3650  # 10 years in days
    },
    'laboratory_values': {
        'creatinine': {'min': 0.1, 'max': 20.0},  # mg/dL
        'albumin': {'min': 1.0, 'max': 6.0},  # g/dL
        'beta2microglobulin': {'min': 0.5, 'max': 50.0}  # mg/L
    }
}

# Export Configuration
EXPORT_CONFIG = {
    'report_formats': ['pdf', 'html', 'docx'],
    'data_formats': ['csv', 'xlsx', 'json', 'parquet'],
    'figure_formats': ['png', 'svg', 'pdf', 'jpg'],
    'figure_dpi': 300,
    'max_export_rows': 100000
}

# Notification Configuration
NOTIFICATION_CONFIG = {
    'email_templates': {
        'analysis_complete': 'analysis_complete.html',
        'error_notification': 'error_notification.html',
        'shared_result': 'shared_result.html'
    },
    'notification_types': ['email', 'in_app', 'webhook'],
    'retry_attempts': 3,
    'retry_delay': 300  # 5 minutes
}

# Cache Configuration
CACHE_CONFIG = {
    'analysis_results_ttl': 86400,  # 24 hours
    'data_preview_ttl': 3600,  # 1 hour
    'user_preferences_ttl': 604800,  # 1 week
    'statistical_models_ttl': 43200  # 12 hours
}

# Audit Trail Configuration
AUDIT_CONFIG = {
    'tracked_events': [
        'user_login', 'user_logout', 'data_upload', 'data_delete',
        'analysis_run', 'result_export', 'settings_change', 'user_created'
    ],
    'retention_days': 2555,  # 7 years for compliance
    'sensitive_fields': ['password', 'secret_key', 'token'],
    'log_format': 'json'
}

# Statistical Power Analysis Configuration
POWER_ANALYSIS_CONFIG = {
    'default_power': 0.80,
    'default_alpha': 0.05,
    'effect_sizes': {
        'small': 0.2,
        'medium': 0.5,
        'large': 0.8
    },
    'sample_size_methods': ['cox_regression', 'log_rank', 'rmst'],
    'power_calculation_methods': ['analytic', 'simulation', 'bootstrap'],
    'minimum_events_per_variable': 10,
    'recommended_events_per_variable': 15
}

# Model Validation Configuration
MODEL_VALIDATION_CONFIG = {
    'cross_validation': {
        'method': 'time_aware_cv',
        'folds': 5,
        'stratify_by': 'event_status'
    },
    'bootstrap': {
        'iterations': 1000,
        'confidence_level': 0.95,
        'bias_correction': True
    },
    'performance_metrics': {
        'discrimination': ['c_index', 'auc_roc', 'auc_pr'],
        'calibration': ['brier_score', 'calibration_slope', 'calibration_intercept'],
        'clinical_utility': ['decision_curve_analysis', 'net_benefit'],
        'reclassification': ['idi', 'nri', 'categorical_nri']
    },
    'assumption_tests': {
        'proportional_hazards': ['schoenfeld_test', 'scaled_schoenfeld'],
        'linearity': ['martingale_residuals', 'deviance_residuals'],
        'independence': ['dfbeta', 'influence_measures']
    }
}

# Publication Quality Standards
PUBLICATION_CONFIG = {
    'figure_standards': {
        'dpi': 300,
        'formats': ['pdf', 'svg', 'png'],
        'color_scheme': 'colorblind_friendly',
        'font_family': 'Arial',
        'font_sizes': {
            'title': 14,
            'axis_labels': 12,
            'tick_labels': 10,
            'legend': 10
        }
    },
    'table_standards': {
        'decimal_places': 3,
        'p_value_threshold': 0.001,
        'confidence_intervals': True,
        'effect_size_reporting': True
    },
    'reproducibility': {
        'random_seed': 42,
        'software_versions': True,
        'parameter_logging': True,
        'code_generation': True
    },
    'reporting_guidelines': {
        'strobe': True,
        'consort': True,
        'spirit': True,
        'tripod': True
    }
}




# Group Analysis Reporting Configuration
GROUP_REPORTING_CONFIG = {
    'report_types': {
        'individual_group': {
            'sections': ['group_composition', 'descriptive_stats', 'univariate_analysis',
                         'multivariate_analysis', 'survival_curves', 'forest_plots', 'interpretation'],
            'format': 'detailed_scientific'
        },
        'cross_group_comparison': {
            'sections': ['group_summaries', 'effect_size_comparison', 'significance_testing',
                         'model_performance', 'clinical_ranking', 'recommendations'],
            'format': 'comparative_analysis'
        },
        'integrated_report': {
            'sections': ['executive_summary', 'methodology', 'individual_results',
                         'comparative_analysis', 'clinical_implications', 'limitations', 'conclusions'],
            'format': 'comprehensive_scientific'
        },
        'executive_summary': {
            'sections': ['key_findings', 'clinical_recommendations', 'risk_stratification', 'actionable_insights'],
            'format': 'clinical_decision_support'
        }
    },
    'visualization_types': {
        'group_specific': ['survival_curves', 'forest_plots', 'variable_importance', 'correlation_heatmaps'],
        'cross_group': ['comparison_plots', 'effect_size_plots', 'model_performance_comparison', 'clinical_impact_ranking'],
        'integrated': ['comprehensive_forest_plot', 'risk_stratification_plot', 'decision_tree', 'clinical_algorithm']
    }
}
