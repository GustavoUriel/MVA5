# Project Endpoints

This file lists the project's endpoints. The table is split into two sections:
- Active routes (not archived)
- Archived routes (implementations moved to `archive/archived_handlers.py`)

## Active routes (not archived)

| Endpoint | Method | Function | File |
|---|---:|---|---|
| `/api/config` | GET | `api_config` | `api_bp.py` |

<!-- grouped by file: datasets_bp.py comes next alphabetically -->
| `/dataset/<int:dataset_id>` | GET | `view_dataset` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/<tab>` | GET | `view_dataset` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/upload` | POST | `upload_dataset_file` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/processing-status` | GET | `get_processing_status` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/files/<int:file_id>/duplicate` | POST | `duplicate_dataset_file` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/files/<int:file_id>/rename` | POST | `rename_dataset_file` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/files/<int:file_id>` | DELETE | `delete_dataset_file_alt` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/files/api` | GET | `get_dataset_files` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/metadata/column-groups` | GET | `get_column_groups` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/metadata/attribute-discarding` | GET | `get_attribute_discarding_policies` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/metadata/microbial-discarding` | GET | `get_microbial_discarding_policies` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/metadata/microbial-grouping` | GET | `get_microbial_grouping_methods` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/metadata/stratifications` | GET | `get_stratifications` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/metadata/clustering-methods` | GET | `get_clustering_methods` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/metadata/cluster-representative-methods` | GET | `get_cluster_representative_methods` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/data-stats` | GET | `get_dataset_data_stats` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/file/<int:file_id>/patient-count` | GET | `get_patient_count` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/metadata/bracken-time-points` | GET | `get_bracken_time_points` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/metadata/analysis-methods` | GET | `get_analysis_methods` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/analysis/save` | POST | `save_analysis_configuration` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/analysis/list` | GET | `list_saved_analyses` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/analysis/delete` | POST | `delete_analysis` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/analysis/duplicate` | POST | `duplicate_analysis` | `datasets_bp.py` |
| `/dataset/<int:dataset_id>/analysis/rename` | POST | `rename_analysis` | `datasets_bp.py` |

<!-- editor_bp.py -->
| `/file/<int:file_id>` | GET | `editor_route` | `editor_bp.py` |
| `/file/<int:file_id>/data` | GET | `editor_data` | `editor_bp.py` |
| `/file/<int:file_id>/schema` | GET | `editor_schema` | `editor_bp.py` |

<!-- files_bp.py (active but some handlers marked UNUSED) -->
| `/dataset/<int:dataset_id>/file/<int:file_id>/duplicate` | POST | `duplicate_dataset_file` | `files_bp.py` — UNUSED (no hits in requests.log) |
| `/dataset/<int:dataset_id>/file/<int:file_id>/curate` | POST | `cure_dataset_file` | `files_bp.py` — UNUSED (no hits in requests.log) |
| `/dataset/<int:dataset_id>/file/<int:file_id>/rename` | POST | `rename_dataset_file` | `files_bp.py` — UNUSED (no hits in requests.log) |

<!-- main_bp.py -->
| `/` | GET | `index` | `main_bp.py` |
| `/dashboard` | GET | `dashboard` | `main_bp.py` |





## Archived routes (implementations moved to `archive/archived_handlers.py`)

| Endpoint | Method | Function | File |
|---|---:|---|---|
<!-- analysis_bp.py (alphabetical order by file) -->
| `/analysis/new` | GET | `new_analysis` | `analysis_bp.py` — ARCHIVED |
| `/analysis/create` | POST | `create_analysis` | `analysis_bp.py` — ARCHIVED |
| `/analysis/<int:analysis_id>` | GET | `view_analysis` | `analysis_bp.py` — ARCHIVED |
| `/analysis/<int:analysis_id>/edit` | GET | `edit_analysis` | `analysis_bp.py` — ARCHIVED |
| `/analysis/<int:analysis_id>/update` | POST | `update_analysis` | `analysis_bp.py` — ARCHIVED |
| `/analysis/<int:analysis_id>/delete` | POST | `delete_analysis` | `analysis_bp.py` — ARCHIVED |
| `/analysis/<int:analysis_id>/run` | POST | `run_analysis` | `analysis_bp.py` — ARCHIVED |
| `/analysis/<int:analysis_id>/report` | GET | `view_report` | `analysis_bp.py` — ARCHIVED |

<!-- api_bp.py -->
| `/api/datasets` | GET | `api_datasets` | `api_bp.py` — ARCHIVED |

<!-- datasets_bp.py -->
| `/dataset/new` | GET, POST | `new_dataset` | `datasets_bp.py` — ARCHIVED |
| `/dataset/<int:dataset_id>/file/<int:file_id>/delete` | POST | `delete_dataset_file` | `datasets_bp.py` — ARCHIVED |
| `/dataset/<int:dataset_id>/delete` | POST | `delete_dataset` | `datasets_bp.py` — ARCHIVED |
| `/dataset/<int:dataset_id>/metadata/attribute-discarding/calculate-remaining` | POST | `calculate_remaining_attributes` | `datasets_bp.py` — ARCHIVED |
| `/dataset/<int:dataset_id>/metadata/microbial-discarding/calculate-remaining` | POST | `calculate_remaining_microbes` | `datasets_bp.py` — ARCHIVED |
| `/dataset/<int:dataset_id>/metadata/clustering-methods/<method_name>` | GET | `get_clustering_method` | `datasets_bp.py` — ARCHIVED |
| `/dataset/<int:dataset_id>/metadata/cluster-representative-methods/<method_name>` | GET | `get_cluster_representative_method` | `datasets_bp.py` — ARCHIVED |
| `/dataset/<int:dataset_id>/sanitize` | POST | `sanitize_dataset_data` | `datasets_bp.py` — ARCHIVED |
| `/dataset/<int:dataset_id>/metadata/analysis-methods/<method_name>` | GET | `get_analysis_method` | `datasets_bp.py` — ARCHIVED |
| `/metadata/<metadata_type>` | GET | `get_metadata` | `datasets_bp.py` — ARCHIVED |

<!-- editor_bp.py -->
| `/file/<int:file_id>/save` | POST | `editor_save` | `editor_bp.py` — ARCHIVED |

<!-- files_bp.py -->
| `/dataset/<int:dataset_id>/file/<int:file_id>/delete` | POST | `delete_dataset_file` | `files_bp.py` — ARCHIVED |

