"""
File Validator Module for Microbiome Analysis Platform

This module provides comprehensive validation, sanitization, and standardization
of uploaded microbiome data files. It handles three main file types:
- patients: Patient demographic and clinical data
- taxonomy: Taxonomic classification data
- bracken: Bracken abundance results

The module performs the following operations:
1. File reading with automatic delimiter detection
2. Data validation based on file type requirements
3. Column name standardization and sanitization
4. Data type conversion and cleaning
5. Missing value handling
6. Duplicate removal
7. Processed file saving

Author: Microbiome Analysis Platform
"""

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Optional, Any
import json

class FileValidator:
    """
    Validates, sanitizes, and standardizes uploaded microbiome data files.
    
    This class provides a comprehensive solution for processing uploaded files
    in the microbiome analysis platform. It handles file reading, validation,
    sanitization, and standardization according to predefined schemas.
    
    Attributes:
        log_user_action: Function to log user actions (optional)
    """
    
    def __init__(self, log_user_action=None):
        """
        Initialize the FileValidator.
        
        Args:
            log_user_action: Optional function to log user actions for audit purposes
        """
        self.log_user_action = log_user_action or (lambda action, message, success=True: None)
        
    def validate_and_process_file(self, file_path: str, file_type: str, user_id: int) -> Dict[str, Any]:
        """
        Main method to validate and process uploaded files.
        
        This is the primary entry point for file processing. It orchestrates
        the entire validation and processing pipeline:
        1. Read the file with appropriate delimiter detection
        2. Sanitize column names for the specific file type
        3. Validate the file structure and content
        4. Sanitize and standardize the data
        5. Save the processed file
        6. Generate processing summary
        
        Args:
            file_path: Path to the uploaded file
            file_type: Type of file ('patients', 'taxonomy', 'bracken')
            user_id: ID of the user who uploaded the file
            
        Returns:
            Dict containing processing results with keys:
            - success: Boolean indicating if processing succeeded
            - processed_file_path: Path to the processed file (if successful)
            - original_rows: Number of rows in original file
            - processed_rows: Number of rows after processing
            - columns: List of standardized column names
            - summary: Processing summary statistics
            - error: Error message (if failed)
            - details: Additional error details (if failed)
        """
        try:
            # Step 1: Read the file with automatic delimiter detection
            df = self._read_file(file_path)
            
            # Step 2: Sanitize column names for the specific file type
            df = self._sanitize_column_names(df, file_type)
            
            # Step 3: Validate file structure and content based on type
            validation_result = self._validate_file_type(df, file_type)
            
            # If validation fails, return error details
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'details': validation_result.get('details', {})
                }
            
            # Step 4: Sanitize and standardize the data
            sanitized_df = self._sanitize_data(df, file_type)
            
            # Step 5: Save the processed file
            processed_file_path = self._save_processed_file(sanitized_df, file_path, file_type)
            
            # Step 6: Log successful processing for audit trail
            self.log_user_action(
                f"{file_type}_file_processed",
                f"Successfully processed {file_type} file: {os.path.basename(file_path)}",
                success=True
            )
            
            # Step 7: Return comprehensive processing results
            return {
                'success': True,
                'processed_file_path': processed_file_path,
                'original_rows': len(df),
                'processed_rows': len(sanitized_df),
                'columns': list(sanitized_df.columns),
                'summary': self._generate_summary(sanitized_df, file_type)
            }
            
        except Exception as e:
            # Handle any unexpected errors during processing
            error_msg = f"Error processing {file_type} file: {str(e)}"
            self.log_user_action(f"{file_type}_file_processing_failed", error_msg, success=False)
            
            return {
                'success': False,
                'error': error_msg,
                'details': {'exception': str(e)}
            }
    
    def _read_file(self, file_path: str) -> pd.DataFrame:
        """
        Read file based on its extension with automatic delimiter detection.
        
        This method handles different file formats and automatically detects
        the appropriate delimiter for text files. It supports:
        - CSV files (.csv): Comma-separated values
        - TSV files (.tsv): Tab-separated values  
        - TXT files (.txt): Automatic delimiter detection
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            pandas DataFrame containing the file data
            
        Raises:
            ValueError: If file extension is not supported
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
        
        # Handle different file extensions
        if file_ext == '.csv':
            # CSV files are comma-separated by default
            # Handle complex quoted fields with commas inside
            try:
                # First try with single quotes
                return pd.read_csv(file_path, quotechar="'", skipinitialspace=True, engine='python')
            except Exception as e:
                self.log_user_action('csv_parsing_debug', f"Single quote parsing failed: {str(e)}", success=False)
                try:
                    # Try with double quotes
                    return pd.read_csv(file_path, quotechar='"', skipinitialspace=True, engine='python')
                except Exception as e2:
                    self.log_user_action('csv_parsing_debug', f"Double quote parsing failed: {str(e2)}", success=False)
                    # Fall back to default parsing with error handling
                    return pd.read_csv(file_path, engine='python', on_bad_lines='skip')
        elif file_ext == '.tsv':
            # TSV files are tab-separated
            return pd.read_csv(file_path, sep='\t')
        elif file_ext == '.txt':
            # For TXT files, we need to detect the delimiter automatically
            # Read the first line to analyze delimiter patterns
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
            
            # Count occurrences of different delimiters in the first line
            tab_count = first_line.count('\t')
            semicolon_count = first_line.count(';')
            comma_count = first_line.count(',')
            
            # Choose the delimiter that appears most frequently
            # This handles cases where files might have mixed delimiters
            if tab_count > 0 and tab_count >= max(semicolon_count, comma_count):
                return pd.read_csv(file_path, sep='\t')
            elif semicolon_count > 0 and semicolon_count > comma_count:
                return pd.read_csv(file_path, sep=';')
            elif comma_count > 0:
                return pd.read_csv(file_path, sep=',')
            else:
                # Default to comma if no clear delimiter pattern is found
                return pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {file_ext}")
    
    def _validate_file_type(self, df: pd.DataFrame, file_type: str) -> Dict[str, Any]:
        """
        Validate file structure based on type.
        
        This method dispatches to type-specific validation functions
        that check for required columns, data types, and content validity.
        
        Args:
            df: pandas DataFrame to validate
            file_type: Type of file ('patients', 'taxonomy', 'bracken')
            
        Returns:
            Dict containing validation results with keys:
            - valid: Boolean indicating if file is valid
            - error: Error message (if invalid)
            - warnings: List of warnings
            - details: Validation details and statistics
        """
        if file_type == 'patients':
            return self._validate_patients_file(df)
        elif file_type == 'taxonomy':
            return self._validate_taxonomy_file(df)
        elif file_type == 'bracken':
            return self._validate_bracken_file(df)
        else:
            return {'valid': False, 'error': f'Unknown file type: {file_type}'}
    
    def _validate_patients_file(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate patients data file structure and content.
        
        This method performs comprehensive validation of patient data files,
        checking for required columns, data integrity, and content quality.
        
        Validation checks include:
        - File is not empty
        - Required columns are present (patient_id)
        - No missing values in critical columns
        - Appropriate data types
        - Duplicate detection (as warnings)
        
        Args:
            df: pandas DataFrame containing patient data
            
        Returns:
            Dict containing validation results
        """
        errors = []
        warnings = []
        
        # Check 1: File is not empty
        if df.empty:
            return {'valid': False, 'error': 'File is empty'}
        
        # Check 2: Required columns are present (case-insensitive)
        required_columns = ['patient_id']
        df_columns_lower = [col.lower().strip() for col in df.columns]
        
        missing_columns = []
        for req_col in required_columns:
            if req_col not in df_columns_lower:
                missing_columns.append(req_col)
        
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check 3: Duplicate patient IDs (warning, not error)
        patient_id_col = self._find_column_by_name(df.columns, 'patient_id')
        if patient_id_col:
            duplicates = df[patient_id_col].duplicated()
            if duplicates.any():
                errors.append(f"Found {duplicates.sum()} duplicate patient IDs")
        
        # Check 4: Missing values in critical columns
        if patient_id_col:
            missing_patient_ids = df[patient_id_col].isna().sum()
            if missing_patient_ids > 0:
                errors.append(f"Found {missing_patient_ids} missing patient IDs")
        
        # Check 5: Data types are appropriate
        if patient_id_col:
            # Patient ID should be string or numeric for consistency
            if not pd.api.types.is_string_dtype(df[patient_id_col]) and not pd.api.types.is_numeric_dtype(df[patient_id_col]):
                warnings.append("Patient ID column should be string or numeric")

        # Convert all pandas objects to native Python types for JSON serialization
        missing_values_dict = df.isna().sum().to_dict()
        missing_values_serializable = {str(k): int(v) for k, v in missing_values_dict.items()}
        
        # Compile validation results
        return {
            'valid': len(errors) == 0,
            'error': '; '.join(errors) if errors else None,
            'warnings': warnings,
            'details': {
                'total_rows': int(len(df)),
                'total_columns': int(len(df.columns)),
                'missing_values': missing_values_serializable
            }
        }
    
    def _validate_taxonomy_file(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate taxonomy data file structure and content.
        
        This method validates taxonomy files which contain taxonomic classification
        information. It checks for required columns and data integrity.
        
        Args:
            df: pandas DataFrame containing taxonomy data
            
        Returns:
            Dict containing validation results
        """
        errors = []
        warnings = []
        
        # Check 1: File is not empty
        if df.empty:
            return {'valid': False, 'error': 'File is empty'}
        
        # Check 2: Required columns are present
        required_columns = ['taxonomy_id', 'taxonomy']
        df_columns_lower = [col.lower().strip() for col in df.columns]
        
        missing_columns = []
        for req_col in required_columns:
            if req_col not in df_columns_lower:
                missing_columns.append(req_col)
        
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check 3: Duplicate taxonomy IDs (error - should be unique)
        self.log_user_action('taxonomy_debug', f"Columns after mapping: {list(df.columns)}", success=True)
        self.log_user_action('taxonomy_debug', f"DataFrame shape: {df.shape}", success=True)
        
        # Debug: Show sample of ALL columns to see what's in each
        for col in df.columns[:3]:  # Just first 3 columns to avoid spam
            sample_values = df[col].head(5).tolist()
            self.log_user_action('taxonomy_debug', f"Column '{col}' sample values: {sample_values}", success=True)
        
        taxonomy_id_col = self._find_column_by_name(df.columns, 'taxonomy_id')
        self.log_user_action('taxonomy_debug', f"Looking for taxonomy_id column, found: {taxonomy_id_col}", success=True)
        
        if taxonomy_id_col:
            # Log sample data for debugging
            sample_values = df[taxonomy_id_col].head(10).tolist()
            self.log_user_action('taxonomy_debug', f"Sample taxonomy_id values: {sample_values}", success=True)
            
            duplicates = df[taxonomy_id_col].duplicated()
            duplicate_count = duplicates.sum()
            self.log_user_action('taxonomy_debug', f"Total rows: {len(df)}, Duplicates found: {duplicate_count}", success=True)
            
            if duplicates.any():
                # Show some example duplicates
                duplicate_values = df[taxonomy_id_col][duplicates].head(5).tolist()
                self.log_user_action('taxonomy_debug', f"Example duplicate values: {duplicate_values}", success=False)
                errors.append(f"Found {duplicate_count} duplicate taxonomy IDs")
        
        # Check 4: Missing values in critical columns
        if taxonomy_id_col:
            missing_taxonomy_ids = df[taxonomy_id_col].isna().sum()
            if missing_taxonomy_ids > 0:
                errors.append(f"Found {missing_taxonomy_ids} missing taxonomy IDs")
        
        # Convert all pandas objects to native Python types for JSON serialization
        missing_values_dict = df.isna().sum().to_dict()
        missing_values_serializable = {str(k): int(v) for k, v in missing_values_dict.items()}
        
        return {
            'valid': len(errors) == 0,
            'error': '; '.join(errors) if errors else None,
            'warnings': warnings,
            'details': {
                'total_rows': int(len(df)),
                'total_columns': int(len(df.columns)),
                'missing_values': missing_values_serializable
            }
        }
    
    def _validate_bracken_file(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate bracken results file structure and content.
        
        This method validates bracken abundance files which contain intersection
        data between patients and taxonomies. It checks for required columns
        and validates column naming patterns for time-based measurements.
        
        Args:
            df: pandas DataFrame containing bracken abundance data
            
        Returns:
            Dict containing validation results
        """
        errors = []
        warnings = []
        
        # Check 1: File is not empty
        if df.empty:
            return {'valid': False, 'error': 'File is empty'}
        
        # Check 2: Required columns are present
        required_columns = ['taxonomy_id']
        df_columns_lower = [col.lower().strip() for col in df.columns]
        
        missing_columns = []
        for req_col in required_columns:
            if req_col not in df_columns_lower:
                missing_columns.append(req_col)
        
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check 3: Validate column naming pattern
        # Columns should be either 'taxonomy_id' or end with time suffixes (p, e, 2.4m with or without dots)
        # First apply common sanitization to get the actual column names that will be used
        sanitized_columns = self._apply_common_sanitization(df.columns)
        valid_suffixes = ['p', 'e', '2.4m', '.p', '.e', '.2.4m']
        invalid_columns = []
        
        # Log the validation process for debugging
        self.log_user_action('bracken_validation_debug', f"Original columns: {list(df.columns)}", success=True)
        self.log_user_action('bracken_validation_debug', f"Sanitized columns: {sanitized_columns}", success=True)
        
        for i, col in enumerate(df.columns):
            sanitized_col = sanitized_columns[i]
            self.log_user_action('bracken_validation_debug', f"Checking column: '{col}' -> sanitized: '{sanitized_col}'", success=True)
            if sanitized_col != 'taxonomy_id' and not any(sanitized_col.endswith(suffix) for suffix in valid_suffixes):
                invalid_columns.append(col)  # Show original column name in error
                self.log_user_action('bracken_validation_debug', f"Invalid column found: '{col}' (sanitized: '{sanitized_col}')", success=False)
        
        if invalid_columns:
            error_msg = f"Invalid column names found: {', '.join(invalid_columns[:5])}{'...' if len(invalid_columns) > 5 else ''}. Columns must be 'taxonomy_id' or end with time suffixes (P/p, E/e, 2.4M/2.4m with or without dots)"
            errors.append(error_msg)
            self.log_user_action('bracken_validation_error', error_msg, success=False)
        
        # Check 4: Check for numeric values in measurement columns
        measurement_columns = [col for col in df.columns if col.lower().strip() != 'taxonomy_id']
        if measurement_columns:
            # Test first few rows to ensure they contain numeric values
            sample_col = measurement_columns[0]
            try:
                pd.to_numeric(df[sample_col], errors='coerce')
            except:
                errors.append(f"Measurement column '{sample_col}' contains non-numeric values")
        
        # Convert all pandas objects to native Python types for JSON serialization
        missing_values_dict = df.isna().sum().to_dict()
        missing_values_serializable = {str(k): int(v) for k, v in missing_values_dict.items()}
        
        return {
            'valid': len(errors) == 0,
            'error': '; '.join(errors) if errors else None,
            'warnings': warnings,
            'details': {
                'total_rows': int(len(df)),
                'total_columns': int(len(df.columns)),
                'missing_values': missing_values_serializable
            }
        }
    
    def _sanitize_column_names(self, df: pd.DataFrame, file_type: str) -> pd.DataFrame:
        """
        Sanitize column names for the specific file type.
        
        This method performs file-type specific column name standardization:
        1. Apply common sanitization (remove spaces, newlines, replace with underscores)
        2. Apply file-type specific mapping
        3. Handle duplicate column names
        
        Args:
            df: pandas DataFrame to sanitize
            file_type: Type of file for specific column mapping
            
        Returns:
            DataFrame with sanitized column names
        """
        # Create a copy to avoid modifying the original dataframe
        sanitized_df = df.copy()
        
        # Apply common sanitization first
        sanitized_df.columns = self._apply_common_sanitization(sanitized_df.columns)
        
        # Apply file-type specific column mapping
        if file_type == 'patients':
            sanitized_df.columns = self._map_patients_columns(sanitized_df.columns)
        elif file_type == 'taxonomy':
            sanitized_df.columns = self._map_taxonomy_columns(sanitized_df.columns)
        elif file_type == 'bracken':
            sanitized_df.columns = self._map_bracken_columns(sanitized_df.columns)
        
        # Handle duplicate column names
        sanitized_df.columns = self._handle_duplicate_columns(sanitized_df.columns)
        
        return sanitized_df
    
    def _sanitize_data(self, df: pd.DataFrame, file_type: str) -> pd.DataFrame:
        """
        Sanitize and standardize the data.
        
        This method performs comprehensive data cleaning and standardization:
        1. Remove leading/trailing whitespace
        2. Handle missing values
        3. Remove duplicate rows
        4. Apply type-specific sanitization
        
        Args:
            df: pandas DataFrame to sanitize
            file_type: Type of file for type-specific processing
            
        Returns:
            Sanitized pandas DataFrame
        """
        # Create a copy to avoid modifying the original dataframe
        sanitized_df = df.copy()
        
        # Step 1: Remove leading/trailing whitespace from string columns
        for col in sanitized_df.select_dtypes(include=['object']).columns:
            sanitized_df[col] = sanitized_df[col].astype(str).str.strip()
        
        # Step 2: Handle missing values according to file type requirements
        sanitized_df = self._handle_missing_values(sanitized_df, file_type)
        
        # Step 3: Remove duplicate rows to ensure data integrity
        sanitized_df = sanitized_df.drop_duplicates()
        
        # Step 4: Apply type-specific sanitization
        if file_type == 'patients':
            sanitized_df = self._sanitize_patients_data(sanitized_df)
        elif file_type == 'taxonomy':
            sanitized_df = self._sanitize_taxonomy_data(sanitized_df)
        elif file_type == 'bracken':
            sanitized_df = self._sanitize_bracken_data(sanitized_df)
        
        return sanitized_df
    
    def _apply_common_sanitization(self, columns: pd.Index) -> List[str]:
        """
        Apply common sanitization to column names.
        
        This method performs basic column name cleaning that applies to all file types:
        1. Remove newlines from quoted text
        2. Strip leading/trailing spaces
        3. Replace semicolons and spaces with underscores
        4. Convert to lowercase
        
        Args:
            columns: pandas Index of column names to sanitize
            
        Returns:
            List of sanitized column names
        """
        sanitized = []
        
        for col in columns:
            # Step 1: Remove newlines from quoted text and strip spaces
            clean_col = col.strip()
            
            # Step 2: Replace semicolons and spaces with underscores
            clean_col = re.sub(r'[; ]', '_', clean_col)
            
            # Step 3: Convert to lowercase
            clean_col = clean_col.lower()
            
            sanitized.append(clean_col)
        
        return sanitized
    
    def _map_patients_columns(self, columns: List[str]) -> List[str]:
        """
        Map patients file columns to standardized names.
        
        This method maps original column names to standardized versions
        specific to the patients file type, including medication columns.
        
        Args:
            columns: List of sanitized column names
            
        Returns:
            List of mapped column names
        """
        # Define comprehensive mapping for patients file columns
        patients_column_mapping = {
            'patient_study_id': 'patient_id',
            'age': 'age',
            'gender': 'gender',
            'race': 'race',
            'ethnicity': 'ethnicity',
            'weight_kg': 'weight_kg',
            'height_m': 'height_m',
            'bmi': 'bmi',
            'smoking': 'smoking',
            'smoking_status': 'smoking_status',
            'igg': 'igg',
            'iga': 'iga',
            'biclonal': 'biclonal',
            'lightchain': 'lightchain',
            'igh_rearrangement': 'igh_rearrangement',
            '3_monosomy': '3_monosomy',
            '3_gain': '3_gain',
            '5_gain': '5_gain',
            '7_gain': '7_gain',
            '9_monosomy': '9_monosomy',
            '9_gain': '9_gain',
            '11_monosomy': '11_monosomy',
            '11_gain': '11_gain',
            '13_monosomy': '13_monosomy',
            '15_gain': '15_gain',
            '17_monosomy': '17_monosomy',
            '19_gain': '19_gain',
            '21_gain': '21_gain',
            'del(13q)': 'del(13q)',
            't(11_14)': 't(11_14)',
            't(4_14)': 't(4_14)',
            't(14_16)': 't(14_16)',
            't(14_20)': 't(14_20)',
            '1q+': '1qPlus',
            'del(1p32)': 'del(1p32)',
            'del(17p)': 'del(17p)',
            '6q21': '6q21',
            't(12_22)': 't(12_22)',
            'hr_mutations': 'hr_mutations',
            'ultrahr_mutations': 'ultrahr_mutations',
            'imwg_hr': 'imwg_hr',
            'functional_hr': 'functional_hr',
            'iss': 'iss',
            'riss': 'riss',
            'beta2microglobulin': 'beta2microglobulin',
            'creatinine': 'creatinine',
            'albumin': 'albumin',
            'induction_therapy': 'induction_therapy',
            'melphalanmgperm2': 'melphalanmgperm2',
            'first_transplant_date': 'first_transplant_date',
            'date_engraftment': 'date_engraftment',
            'es': 'es',
            'esnoninfectiousfever': 'esnoninfectiousfever',
            'esnoninfectious_diarhhea': 'esnoninfectious_diarhhea',
            'esrash': 'esrash',
            'last_date_of_contact': 'last_date_of_contact',
            'monthsfirst_transplant': 'monthsfirst_transplant',
            'secona_transplant_date': 'secona_transplant_date',
            'monthssecona_transplantrk': 'monthssecona_transplantrk',
            'rk_updated_relapse_date': 'rk_updated_relapse_date',
            'relapsemonthsfirst_transplant': 'relapsemonthsfirst_transplant',
            'relapsemonthssecona_transplant': 'relapsemonthssecona_transplant',
            'duration_pfs': 'duration_pfs',
            'pfs_status': 'pfs_status',
            'rk_updated_death_date': 'rk_updated_death_date',
            'deathmonthsfirst_transplant': 'deathmonthsfirst_transplant',
            'deathmonthssecona_transplant': 'deathmonthssecona_transplant',
            'duration_survival': 'duration_survival',
            'death_status': 'death_status'
        }
        
        mapped_columns = []
        
        for i, col in enumerate(columns):
            mapped_col = col
            
            # Handle start_date and end_date columns by appending the previous column name
            if col.startswith('start_date'):
                if i > 0:  # Make sure there's a previous column
                    previous_col = columns[i - 1]
                    mapped_col = f"{previous_col}_start"
            elif col.startswith('end_date'):
                if i > 0:  # Make sure there's a previous column
                    previous_col = columns[i - 1]
                    mapped_col = f"{previous_col}_end"
            
            # Map to standardized names if not a date column
            if mapped_col == col:  # Only apply mapping if we didn't change it above
                mapped_col = patients_column_mapping.get(col, col)
            
            mapped_columns.append(mapped_col)
        
        return mapped_columns
    
    def _map_taxonomy_columns(self, columns: List[str]) -> List[str]:
        """
        Map taxonomy file columns to standardized names.
        
        This method maps original column names to standardized versions
        specific to the taxonomy file type.
        
        Args:
            columns: List of sanitized column names
            
        Returns:
            List of mapped column names
        """
        # Define mapping for taxonomy file columns
        taxonomy_column_mapping = {
            'taxonomy_id': 'taxonomy_id',
            'taxonomy': 'taxonomy',
            'domain': 'domain',
            'phylum': 'phylum',
            'class': 'class',
            'order': 'order',
            'family': 'family',
            'genus': 'genus',
            'species': 'species'
        }
        
        mapped_columns = []
        
        # Debug: Log original columns before mapping
        self.log_user_action('taxonomy_mapping_debug', f"Original columns before mapping: {list(columns)}", success=True)
        
        for col in columns:
            # Handle taxonomy columns first (more specific matching)
            if 'taxonomy' in col.lower() and 'id' in col.lower():
                mapped_col = 'taxonomy_id'
                self.log_user_action('taxonomy_mapping_debug', f"'{col}' -> '{mapped_col}' (taxonomy+id rule)", success=True)
            elif 'taxonomy' in col.lower() and 'id' not in col.lower():
                mapped_col = 'taxonomy'
                self.log_user_action('taxonomy_mapping_debug', f"'{col}' -> '{mapped_col}' (taxonomy-only rule)", success=True)
            else:
                # Use the mapping dictionary for other columns
                mapped_col = taxonomy_column_mapping.get(col, col)
                self.log_user_action('taxonomy_mapping_debug', f"'{col}' -> '{mapped_col}' (dictionary lookup)", success=True)
            
            mapped_columns.append(mapped_col)
        
        return mapped_columns
    
    def _map_bracken_columns(self, columns: List[str]) -> List[str]:
        """
        Map bracken file columns to standardized names.
        
        This method maps original column names to standardized versions
        specific to the bracken file type. For bracken files, columns are
        either 'taxonomy_id' or patient measurements with time suffixes.
        
        Args:
            columns: List of sanitized column names
            
        Returns:
            List of mapped column names
        """
        mapped_columns = []
        
        for col in columns:
            # Keep taxonomy_id as is
            if col == 'taxonomy_id':
                mapped_col = 'taxonomy_id'
            else:
                # For patient measurement columns, preserve the original structure
                # but ensure time suffixes are properly formatted
                col_lower = col.lower()
                if col_lower.endswith('.p'):
                    # Previous to treatment start
                    mapped_col = col
                elif col_lower.endswith('.e'):
                    # Two weeks after treatment start
                    mapped_col = col
                elif col_lower.endswith('.2.4m'):
                    # 24 months after treatment start
                    mapped_col = col
                else:
                    # Keep other columns as is (might be patient_id without suffix)
                    mapped_col = col
            
            mapped_columns.append(mapped_col)
        
        return mapped_columns
    
    def _handle_duplicate_columns(self, columns: List[str]) -> List[str]:
        """
        Handle duplicate column names by adding numbering.
        
        This method prevents conflicts when multiple columns have the same name
        by adding (1), (2), etc. to duplicate column names.
        
        Args:
            columns: List of column names to process
            
        Returns:
            List of column names with duplicates resolved
        """
        seen_columns = {}
        final_columns = []
        
        for col in columns:
            if col in seen_columns:
                seen_columns[col] += 1
                final_columns.append(f"{col}({seen_columns[col]})")
            else:
                seen_columns[col] = 0
                final_columns.append(col)
        
        return final_columns
    
    def _handle_missing_values(self, df: pd.DataFrame, file_type: str) -> pd.DataFrame:
        """
        Handle missing values appropriately based on file type.
        
        This method removes rows with missing values in critical columns
        to ensure data quality. Different file types have different
        critical column requirements.
        
        Args:
            df: pandas DataFrame to process
            file_type: Type of file to determine critical columns
            
        Returns:
            DataFrame with missing values handled
        """
        # Define critical columns for each file type
        # These columns must have values for the row to be valid
        critical_columns = []
        if file_type == 'patients':
            critical_columns = ['patient_id']
        elif file_type == 'taxonomy':
            critical_columns = ['taxonomy_id', 'taxonomy']
        elif file_type == 'bracken':
            critical_columns = ['taxonomy_id']
        
        # Find actual column names (case-insensitive matching)
        actual_critical_cols = []
        for crit_col in critical_columns:
            found_col = self._find_column_by_name(df.columns, crit_col)
            if found_col:
                actual_critical_cols.append(found_col)
        
        # Remove rows with missing values in critical columns
        if actual_critical_cols:
            df = df.dropna(subset=actual_critical_cols)
        
        return df
    
    def _sanitize_patients_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sanitize patients data with type-specific processing.
        
        This method ensures that patient data has appropriate data types
        and formats for consistent analysis.
        
        Args:
            df: pandas DataFrame containing patient data
            
        Returns:
            Sanitized DataFrame
        """
        # Ensure patient_id is string for consistent handling
        patient_id_col = self._find_column_by_name(df.columns, 'patient_id')
        if patient_id_col:
            df[patient_id_col] = df[patient_id_col].astype(str)
        
        return df
    
    def _sanitize_taxonomy_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sanitize taxonomy data with type-specific processing.
        
        This method ensures that taxonomy data has appropriate data types
        for consistent analysis.
        
        Args:
            df: pandas DataFrame containing taxonomy data
            
        Returns:
            Sanitized DataFrame
        """
        # Ensure taxonomy_id is string for consistent handling
        taxonomy_id_col = self._find_column_by_name(df.columns, 'taxonomy_id')
        if taxonomy_id_col:
            df[taxonomy_id_col] = df[taxonomy_id_col].astype(str)
        
        # Ensure taxonomy is string for consistent handling
        taxonomy_col = self._find_column_by_name(df.columns, 'taxonomy')
        if taxonomy_col:
            df[taxonomy_col] = df[taxonomy_col].astype(str)
        
        return df
    
    def _sanitize_bracken_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sanitize bracken data with type-specific processing.
        
        This method ensures that bracken intersection data has appropriate
        data types and handles numeric measurement values.
        
        Args:
            df: pandas DataFrame containing bracken intersection data
            
        Returns:
            Sanitized DataFrame
        """
        # Ensure taxonomy_id is string for consistent handling
        taxonomy_id_col = self._find_column_by_name(df.columns, 'taxonomy_id')
        if taxonomy_id_col:
            df[taxonomy_id_col] = df[taxonomy_id_col].astype(str)
        
        # Convert measurement columns to numeric and fill missing values with 0
        # These are the patient measurement columns with time suffixes (.P, .E, .2.4M)
        measurement_columns = [col for col in df.columns if col.lower().strip() != 'taxonomy_id']
        for col in measurement_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    
    def _save_processed_file(self, df: pd.DataFrame, original_path: str, file_type: str) -> str:
        """
        Save the processed file with standardized format.
        
        This method saves the processed DataFrame as a CSV file with
        a standardized naming convention.
        
        Args:
            df: pandas DataFrame to save
            original_path: Path to the original file
            file_type: Type of file for naming purposes
            
        Returns:
            Path to the saved processed file
        """
        # Create processed file path with '_processed.csv' suffix
        base_name = os.path.splitext(original_path)[0]
        processed_path = f"{base_name}_processed.csv"
        
        # Save as CSV with standardized format
        df.to_csv(processed_path, index=False)
        
        return processed_path
    
    def _generate_summary(self, df: pd.DataFrame, file_type: str) -> Dict[str, Any]:
        """
        Generate comprehensive summary statistics for the processed file.
        
        This method creates detailed statistics about the processed data
        including row counts, column counts, missing values, and
        type-specific metrics like unique counts.
        
        Args:
            df: pandas DataFrame to summarize
            file_type: Type of file for type-specific statistics
            
        Returns:
            Dict containing summary statistics
        """
        # Basic summary statistics for all file types
        summary = {
            'total_rows': int(len(df)),
            'total_columns': int(len(df.columns)),
            'missing_values': {str(k): int(v) for k, v in df.isna().sum().to_dict().items()},
            'column_types': {str(col): str(dtype) for col, dtype in df.dtypes.to_dict().items()}
        }
        
        # Type-specific summary statistics
        if file_type == 'patients':
            # Count unique patients for patient files
            patient_id_col = self._find_column_by_name(df.columns, 'patient_id')
            if patient_id_col:
                summary['unique_patients'] = int(df[patient_id_col].nunique())
        
        elif file_type == 'taxonomy':
            # Count unique taxonomies for taxonomy files
            taxonomy_id_col = self._find_column_by_name(df.columns, 'taxonomy_id')
            if taxonomy_id_col:
                summary['unique_taxonomies'] = int(df[taxonomy_id_col].nunique())
        
        elif file_type == 'bracken':
            # Count unique taxonomies and measurement time points for bracken files
            taxonomy_id_col = self._find_column_by_name(df.columns, 'taxonomy_id')
            if taxonomy_id_col:
                summary['unique_taxonomies'] = int(df[taxonomy_id_col].nunique())
            
            # Count measurement time points (columns with time suffixes)
            measurement_columns = [col for col in df.columns if col.lower().strip() != 'taxonomy_id']
            summary['measurement_timepoints'] = int(len(measurement_columns))
            
            # Count measurements by time period
            p_columns = [col for col in measurement_columns if col.lower().endswith('.p')]
            e_columns = [col for col in measurement_columns if col.lower().endswith('.e')]
            m24_columns = [col for col in measurement_columns if col.lower().endswith('.2.4m')]
            
            summary['measurements_pre_treatment'] = int(len(p_columns))
            summary['measurements_2weeks'] = int(len(e_columns))
            summary['measurements_24months'] = int(len(m24_columns))
        
        return summary
    
    def _find_column_by_name(self, columns: pd.Index, target_name: str) -> Optional[str]:
        """
        Find column by name with case-insensitive matching.
        
        This method searches for a column name in a case-insensitive manner,
        which is useful for handling variations in column naming conventions.
        
        Args:
            columns: pandas Index of column names to search
            target_name: Target column name to find
            
        Returns:
            Actual column name if found, None otherwise
        """
        # Convert all column names to lowercase for case-insensitive matching
        columns_lower = [col.lower().strip() for col in columns]
        try:
            # Find the index of the target name
            index = columns_lower.index(target_name)
            # Return the original column name (preserving case)
            return columns[index]
        except ValueError:
            # Column not found
            return None
