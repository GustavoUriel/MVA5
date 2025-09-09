# Flask Application Route Map

## Application Overview
**Base URL**: `http://127.0.0.1:5005`  
**Authentication**: Google OAuth + Flask-Login  
**Session Management**: Filesystem-based sessions  

---

## 🔐 Authentication Blueprint (`auth_bp`)

| Method | Route | Function | Description | Auth Required |
|--------|-------|----------|-------------|---------------|
| GET | `/auth/login` | `login()` | Initiate Google OAuth login | ❌ |
| GET | `/auth/login/authorized` | `auth_callback()` | Handle Google OAuth callback | ❌ |
| GET | `/auth/logout` | `logout()` | Logout user and clear session | ✅ |

---

## 🏠 Main Blueprint (`main_bp`)

| Method | Route | Function | Description | Auth Required |
|--------|-------|----------|-------------|---------------|
| GET | `/` | `index()` | Home page (redirects to dashboard if logged in) | ❌ |
| GET | `/dashboard` | `dashboard()` | User dashboard with datasets overview | ✅ |

---

## 📊 Datasets Blueprint (`datasets_bp`)

### Dataset Management
| Method | Route | Function | Description | Auth Required |
|--------|-------|----------|-------------|---------------|
| GET, POST | `/dataset/new` | `new_dataset()` | Create new dataset | ✅ |
| GET | `/dataset/<int:dataset_id>` | `view_dataset()` | View dataset (default: files tab) | ✅ |
| GET | `/dataset/<int:dataset_id>/<tab>` | `view_dataset()` | View dataset with specific tab | ✅ |
| POST | `/dataset/<int:dataset_id>/upload` | `upload_dataset_file()` | Upload file to dataset | ✅ |
| POST | `/dataset/<int:dataset_id>/delete` | `delete_dataset()` | Delete dataset and all files | ✅ |

### Dataset Data & Processing
| Method | Route | Function | Description | Auth Required |
|--------|-------|----------|-------------|---------------|
| GET | `/dataset/<int:dataset_id>/processing-status` | `get_processing_status()` | Get file processing status | ✅ |
| GET | `/dataset/<int:dataset_id>/files/api` | `get_dataset_files()` | Get dataset files (API) | ✅ |
| GET | `/dataset/<int:dataset_id>/data-stats` | `get_dataset_data_stats()` | Get data statistics and analysis | ✅ |
| POST | `/dataset/<int:dataset_id>/sanitize` | `sanitize_dataset_data()` | Sanitize dataset data | ✅ |

### Metadata API Endpoints
| Method | Route | Function | Description | Auth Required |
|--------|-------|----------|-------------|---------------|
| GET | `/dataset/<int:dataset_id>/metadata/column-groups` | `get_column_groups()` | Get column groups metadata | ✅ |
| GET | `/dataset/<int:dataset_id>/metadata/bracken-time-points` | `get_bracken_time_points()` | Get Bracken time points metadata | ✅ |
| GET | `/dataset/<int:dataset_id>/metadata/stratifications` | `get_stratifications()` | Get stratifications metadata | ✅ |
| GET | `/dataset/<int:dataset_id>/metadata/clustering-methods` | `get_clustering_methods()` | Get clustering methods metadata | ✅ |
| GET | `/dataset/<int:dataset_id>/metadata/clustering-methods/<method_name>` | `get_clustering_method()` | Get specific clustering method | ✅ |
| GET | `/dataset/<int:dataset_id>/metadata/cluster-representative-methods` | `get_cluster_representative_methods()` | Get cluster representative methods | ✅ |
| GET | `/dataset/<int:dataset_id>/metadata/cluster-representative-methods/<method_name>` | `get_cluster_representative_method()` | Get specific cluster representative method | ✅ |
| GET | `/metadata/<metadata_type>` | `get_metadata()` | Get metadata configuration dynamically | ✅ |

---

## 📁 Files Blueprint (`files_bp`)

| Method | Route | Function | Description | Auth Required |
|--------|-------|----------|-------------|---------------|
| POST | `/dataset/<int:dataset_id>/file/<int:file_id>/delete` | `delete_dataset_file()` | Delete specific file from dataset | ✅ |
| POST | `/dataset/<int:dataset_id>/file/<int:file_id>/duplicate` | `duplicate_dataset_file()` | Duplicate file in dataset | ✅ |
| POST | `/dataset/<int:dataset_id>/file/<int:file_id>/cure` | `cure_dataset_file()` | Cure/fix file issues | ✅ |
| POST | `/dataset/<int:dataset_id>/file/<int:file_id>/rename` | `rename_dataset_file()` | Rename file in dataset | ✅ |

---

## 🔧 Editor Blueprint (`editor_bp`)

| Method | Route | Function | Description | Auth Required |
|--------|-------|----------|-------------|---------------|
| GET | `/file/<int:file_id>` | `editor_route()` | Open file in editor | ✅ |
| GET | `/file/<int:file_id>/data` | `editor_data()` | Get file data for editor | ✅ |
| GET | `/file/<int:file_id>/schema` | `editor_schema()` | Get file schema for editor | ✅ |
| POST | `/file/<int:file_id>/save` | `editor_save()` | Save file changes | ✅ |

---

## 🌐 API Blueprint (`api_bp`)

| Method | Route | Function | Description | Auth Required |
|--------|-------|----------|-------------|---------------|
| GET | `/api/config` | `api_config()` | Get application configuration | ❌ |
| GET | `/api/datasets` | `api_datasets()` | Get user datasets (API) | ✅ |

---

## 📋 Smart Table Routes (Legacy)

| Method | Route | Function | Description | Auth Required |
|--------|-------|----------|-------------|---------------|
| GET | `/api/table/data` | `api_table()` | Get table data | ❌ |
| GET | `/api/table/schema` | `api_table_schema()` | Get table schema | ❌ |
| POST | `/api/table/save` | `save()` | Save table data | ❌ |

---

## 🗂️ Dataset Tabs Structure

When accessing `/dataset/<id>/<tab>`, the following tabs are available:

| Tab | Description | Content |
|-----|-------------|---------|
| `files` | File management | Upload, view, delete files |
| `analysis` | Analysis configuration | Column groups, stratifications, clustering, cluster representative |
| `config-editor` | Analysis editor | Analysis type selection, Bracken time points |
| `reports` | Analysis reports | Generated analysis results |
| `settings` | Dataset settings | Dataset configuration |

---

## 🔄 API Response Patterns

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

### Metadata Response
```json
{
  "success": true,
  "clustering_methods": { ... },
  "default_method": "kmeans",
  "method_categories": { ... }
}
```

---

## 🛡️ Security Features

- **Authentication**: Google OAuth 2.0
- **Authorization**: User-based access control
- **Session Management**: Secure filesystem sessions
- **CSRF Protection**: Flask-WTF CSRF tokens
- **Input Validation**: Server-side validation for all inputs
- **File Upload Security**: Type and size validation

---

## 📊 Performance Monitoring

All routes include:
- **Audit Logging**: User actions and requests
- **Performance Tracking**: Response times and database queries
- **Error Logging**: Comprehensive error tracking
- **Database Query Optimization**: Cached queries where appropriate

---

## 🔧 Development Notes

- **Debug Mode**: Enabled in development
- **Hot Reload**: Flask development server with auto-reload
- **Database**: SQLite for development, configurable for production
- **Logging**: Comprehensive logging to `instance/logs/`
- **Static Files**: Served from `app/static/`
- **Templates**: Jinja2 templates in `app/templates/`
