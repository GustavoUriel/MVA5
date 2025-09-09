# Clustering Configuration
CLUSTERING_METHODS = {
    'hierarchical': {
        'name': 'Hierarchical Clustering',
        'parameters': ['linkage', 'metric', 'n_clusters']
    },
    'kmeans': {
        'name': 'K-Means Clustering',
        'parameters': ['n_clusters', 'random_state', 'max_iter']
    },
    'dbscan': {
        'name': 'DBSCAN',
        'parameters': ['eps', 'min_samples', 'metric']
    }
}