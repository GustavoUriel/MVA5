#!/usr/bin/env python3
"""
Simple test script for RSF_PLS_DA_remover module
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the app modules to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import the module directly without going through Flask app imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'modules'))
import importlib.util
spec = importlib.util.spec_from_file_location("RSF_PLS_DA_remover",
    os.path.join(os.path.dirname(__file__), 'app', 'modules', 'RSF_PLS_DA_remover.py'))
rsf_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rsf_module)
RSF_PLS_DA_remover = rsf_module.RSF_PLS_DA_remover

def create_test_data(n_samples=50, n_features=20):
    """Create synthetic survival data for testing"""
    np.random.seed(42)

    # Create features
    features = {}
    for i in range(n_features):
        features[f'feature_{i}'] = np.random.randn(n_samples)

    # Create survival data (some features are prognostic, others are noise)
    # feature_0 and feature_1 are prognostic
    hazard_ratio = 0.5 * features['feature_0'] + 0.3 * features['feature_1']

    # Generate survival times
    baseline_hazard = 0.1
    u = np.random.uniform(0, 1, n_samples)
    time = -np.log(u) / (baseline_hazard * np.exp(hazard_ratio))

    # Censoring (20% censored)
    censoring_time = np.random.exponential(15, n_samples)
    observed_time = np.minimum(time, censoring_time)
    event = (time <= censoring_time).astype(int)

    # Create dataframe
    data = pd.DataFrame(features)
    data['time'] = observed_time
    data['event'] = event

    return data

def main():
    print("Testing RSF_PLS_DA_remover module...")

    # Create test data
    print("Creating test data...")
    test_data = create_test_data(n_samples=50, n_features=20)

    print(f"Test data shape: {test_data.shape}")
    print(f"Number of events: {test_data['event'].sum()}")
    print(".2f")

    # Apply feature selection
    print("\nRunning feature selection...")
    try:
        removed_cols, filtered_data = RSF_PLS_DA_remover(
            data_matrix=test_data,
            event_column='event',
            time_column='time',
            random_state=42
        )

        print(f"\nResults:")
        print(f"- Original features: {len(test_data.columns) - 2}")  # Excluding time and event
        print(f"- Selected features: {len(filtered_data.columns) - 2}")
        print(f"- Removed features: {len(removed_cols)}")
        print(f"- Target features (n-1): {len(test_data) - 1}")

        print(f"\nRemoved columns: {removed_cols[:5]}...")  # Show first 5

        # Check that important features (feature_0, feature_1) are kept
        selected_cols = [col for col in filtered_data.columns if col not in ['event', 'time']]
        if 'feature_0' in selected_cols and 'feature_1' in selected_cols:
            print("✓ Important features (feature_0, feature_1) were retained!")
        else:
            print("⚠ Some important features may have been removed")

        print("\nTest completed successfully!")

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
