import pandas as pd
import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.preprocessing import StandardScaler
from sksurv.ensemble import RandomSurvivalForest
from sksurv.util import Surv
import warnings
warnings.filterwarnings('ignore')


def RSF_PLS_DA_remover(data_matrix, event_column, time_column, random_state=42):
    """
    Remove irrelevant variables using Random Survival Forest (RSF) and PLS-DA feature importance.

    Parameters:
    -----------
    data_matrix : pd.DataFrame
        Input dataframe containing features and survival data
    event_column : str
        Name of the column containing event indicator (1=event occurred, 0=censored)
    time_column : str
        Name of the column containing time-to-event data
    random_state : int
        Random state for reproducibility

    Returns:
    --------
    tuple: (removed_columns, filtered_matrix)
        removed_columns: list of column names that were removed
        filtered_matrix: DataFrame with only the selected relevant columns
    """

    # Validate inputs
    if not isinstance(data_matrix, pd.DataFrame):
        raise ValueError("data_matrix must be a pandas DataFrame")

    if event_column not in data_matrix.columns:
        raise ValueError(f"event_column '{event_column}' not found in data_matrix")

    if time_column not in data_matrix.columns:
        raise ValueError(f"time_column '{time_column}' not found in data_matrix")

    # Separate features from survival data
    survival_data = data_matrix[[event_column, time_column]].copy()
    feature_data = data_matrix.drop([event_column, time_column], axis=1)

    # Remove non-numeric columns
    numeric_features = feature_data.select_dtypes(include=[np.number]).columns
    if len(numeric_features) == 0:
        raise ValueError("No numeric feature columns found")

    feature_data = feature_data[numeric_features]

    # Handle missing values
    feature_data = feature_data.fillna(feature_data.median())

    n_samples, n_features = feature_data.shape

    if n_samples < 10:
        raise ValueError("Need at least 10 samples for reliable feature selection")

    # Calculate target number of features to keep (n-1)
    target_features = max(1, n_samples - 1)

    if n_features <= target_features:
        return [], data_matrix  # No features to remove

    print(f"Starting feature selection with {n_features} features and {n_samples} samples")
    print(f"Target number of features to keep: {target_features}")

    # Initialize importance scores
    rsf_importance = {}
    pls_importance = {}

    # 1. Random Survival Forest importance
    try:
        print("Calculating RSF importance...")
        # Prepare survival data for scikit-survival
        y_surv = Surv.from_dataframe(event_column, time_column, survival_data)

        # Fit Random Survival Forest
        rsf = RandomSurvivalForest(
            n_estimators=100,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=random_state,
            n_jobs=-1
        )

        rsf.fit(feature_data.values, y_surv)

        # Calculate permutation importance
        rsf_importance = _calculate_permutation_importance(
            rsf, feature_data.values, y_surv, feature_data.columns
        )

    except Exception as e:
        print(f"Warning: RSF failed ({str(e)}), using PLS-DA only")
        rsf_importance = {col: 0 for col in feature_data.columns}

    # 2. PLS-DA importance
    try:
        print("Calculating PLS-DA importance...")
        # Create binary groups based on median survival time for patients who had events
        event_times = survival_data[survival_data[event_column] == 1][time_column]
        if len(event_times) == 0:
            raise ValueError("No events found in data")

        median_time = event_times.median()
        # Create groups: 1 = survived longer than median, 0 = survived shorter
        y_groups = (survival_data[time_column] > median_time).astype(int)

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(feature_data.values)

        # Fit PLS-DA (PLS regression with binary target)
        pls = PLSRegression(n_components=min(10, n_features, n_samples-1))
        pls.fit(X_scaled, y_groups)

        # Calculate VIP (Variable Importance in Projection) scores
        pls_importance = _calculate_vip_scores(pls, X_scaled, y_groups)

    except Exception as e:
        print(f"Warning: PLS-DA failed ({str(e)}), using RSF only")
        pls_importance = {col: 0 for col in feature_data.columns}

    # 3. Combine importance scores
    print("Combining importance scores...")
    combined_scores = {}

    for col in feature_data.columns:
        rsf_score = rsf_importance.get(col, 0)
        pls_score = pls_importance.get(col, 0)

        # Normalize scores to 0-1 range
        if rsf_score > 0:
            rsf_score = rsf_score / max(rsf_importance.values()) if max(rsf_importance.values()) > 0 else 0
        if pls_score > 0:
            pls_score = pls_score / max(pls_importance.values()) if max(pls_importance.values()) > 0 else 0

        # Combined score (weighted average)
        combined_scores[col] = (rsf_score + pls_score) / 2

    # 4. Rank features by combined importance
    ranked_features = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

    # 5. Select top features
    selected_features = [col for col, score in ranked_features[:target_features]]
    removed_features = [col for col, score in ranked_features[target_features:]]

    # 6. Create filtered matrix
    filtered_matrix = data_matrix[selected_features + [event_column, time_column]].copy()

    print(f"Feature selection completed:")
    print(f"- Original features: {n_features}")
    print(f"- Selected features: {len(selected_features)}")
    print(f"- Removed features: {len(removed_features)}")

    return removed_features, filtered_matrix


def _calculate_permutation_importance(model, X, y, feature_names, n_repeats=5):
    """
    Calculate permutation importance for survival model.
    """
    from sklearn.metrics import concordance_index_censored

    baseline_score = concordance_index_censored(y['event'], y['time'], model.predict(X))[0]

    importance_scores = {}

    for i, feature_name in enumerate(feature_names):
        scores = []
        X_permuted = X.copy()

        for _ in range(n_repeats):
            # Permute the feature
            np.random.shuffle(X_permuted[:, i])
            permuted_score = concordance_index_censored(
                y['event'], y['time'], model.predict(X_permuted)
            )[0]
            scores.append(baseline_score - permuted_score)

        importance_scores[feature_name] = np.mean(scores)

    return importance_scores


def _calculate_vip_scores(pls_model, X, y, feature_names=None):
    """
    Calculate Variable Importance in Projection (VIP) scores for PLS-DA.
    """
    if feature_names is None:
        feature_names = [f"feature_{i}" for i in range(X.shape[1])]

    n_features = X.shape[1]
    vip_scores = {}

    # Get PLS components
    T = pls_model.x_scores_
    W = pls_model.x_weights_
    Q = pls_model.y_loadings_

    # Calculate VIP for each variable
    for i in range(n_features):
        vip_sum = 0
        denominator = 0

        for j in range(pls_model.n_components):
            component_weight = W[i, j]**2 * Q[j, 0]**2 * np.var(T[:, j])
            vip_sum += component_weight
            denominator += component_weight

        if denominator > 0:
            vip_scores[feature_names[i]] = np.sqrt(vip_sum * pls_model.n_components / denominator)
        else:
            vip_scores[feature_names[i]] = 0

    return vip_scores


# Example usage:
"""
Example:
--------
import pandas as pd
from RSF_PLS_DA_remover import RSF_PLS_DA_remover

# Create sample data
data = pd.DataFrame({
    'feature1': np.random.randn(100),
    'feature2': np.random.randn(100),
    'feature3': np.random.randn(100),
    'time': np.random.exponential(12, 100),
    'event': np.random.binomial(1, 0.7, 100)
})

# Apply feature selection
removed_cols, filtered_data = RSF_PLS_DA_remover(
    data_matrix=data,
    event_column='event',
    time_column='time',
    random_state=42
)

print(f"Removed columns: {removed_cols}")
print(f"Filtered data shape: {filtered_data.shape}")
"""
