# Clustering Configuration
CLUSTERING_METHODS = {
    'hierarchical': {
        'name': 'Hierarchical Clustering',
        'description': 'Builds a hierarchy of clusters using agglomerative approach',
        'parameters': {
            'linkage': {
                'name': 'Linkage Method',
                'type': 'select',
                'options': ['ward', 'complete', 'average', 'single'],
                'default': 'ward',
                'best_component': 'ward',
                'description': 'Linkage criterion for merging clusters'
            },
            'metric': {
                'name': 'Distance Metric',
                'type': 'select',
                'options': ['euclidean', 'manhattan', 'cosine', 'correlation'],
                'default': 'euclidean',
                'best_component': 'euclidean',
                'description': 'Distance metric for computing linkage'
            },
            'n_clusters': {
                'name': 'Number of Clusters',
                'type': 'number',
                'min': 2,
                'max': 20,
                'default': 3,
                'best_component': 'auto',
                'description': 'Number of clusters to form'
            }
        }
    },
    'kmeans': {
        'name': 'K-Means Clustering',
        'description': 'Partitions data into k clusters by minimizing within-cluster sum of squares',
        'parameters': {
            'n_clusters': {
                'name': 'Number of Clusters',
                'type': 'number',
                'min': 2,
                'max': 20,
                'default': 3,
                'best_component': 'auto',
                'description': 'Number of clusters to form'
            },
            'random_state': {
                'name': 'Random State',
                'type': 'number',
                'min': 0,
                'max': 1000,
                'default': 42,
                'best_component': 42,
                'description': 'Random seed for reproducibility'
            },
            'max_iter': {
                'name': 'Maximum Iterations',
                'type': 'number',
                'min': 100,
                'max': 1000,
                'default': 300,
                'best_component': 300,
                'description': 'Maximum number of iterations'
            }
        }
    },
    'dbscan': {
        'name': 'DBSCAN',
        'description': 'Density-based clustering that finds clusters of varying shapes and sizes',
        'parameters': {
            'eps': {
                'name': 'Epsilon (eps)',
                'type': 'number',
                'min': 0.1,
                'max': 5.0,
                'step': 0.1,
                'default': 0.5,
                'best_component': 'auto',
                'description': 'Maximum distance between two samples for one to be considered in the neighborhood'
            },
            'min_samples': {
                'name': 'Minimum Samples',
                'type': 'number',
                'min': 2,
                'max': 50,
                'default': 5,
                'best_component': 5,
                'description': 'Minimum number of samples in a neighborhood for a point to be considered a core point'
            },
            'metric': {
                'name': 'Distance Metric',
                'type': 'select',
                'options': ['euclidean', 'manhattan', 'cosine', 'minkowski'],
                'default': 'euclidean',
                'best_component': 'euclidean',
                'description': 'Distance metric for computing distances'
            }
        }
    },
    'gaussian_mixture': {
        'name': 'Gaussian Mixture Model',
        'description': 'Probabilistic clustering using Gaussian mixture models',
        'parameters': {
            'n_components': {
                'name': 'Number of Components',
                'type': 'number',
                'min': 2,
                'max': 20,
                'default': 3,
                'best_component': 'auto',
                'description': 'Number of mixture components'
            },
            'covariance_type': {
                'name': 'Covariance Type',
                'type': 'select',
                'options': ['full', 'tied', 'diag', 'spherical'],
                'default': 'full',
                'best_component': 'full',
                'description': 'Type of covariance parameters'
            },
            'random_state': {
                'name': 'Random State',
                'type': 'number',
                'min': 0,
                'max': 1000,
                'default': 42,
                'best_component': 42,
                'description': 'Random seed for reproducibility'
            }
        }
    },
    'spectral': {
        'name': 'Spectral Clustering',
        'description': 'Clustering using the spectrum of the similarity matrix',
        'parameters': {
            'n_clusters': {
                'name': 'Number of Clusters',
                'type': 'number',
                'min': 2,
                'max': 20,
                'default': 3,
                'best_component': 'auto',
                'description': 'Number of clusters to form'
            },
            'affinity': {
                'name': 'Affinity Matrix',
                'type': 'select',
                'options': ['rbf', 'nearest_neighbors', 'polynomial', 'sigmoid'],
                'default': 'rbf',
                'best_component': 'rbf',
                'description': 'How to construct the affinity matrix'
            },
            'gamma': {
                'name': 'Gamma',
                'type': 'number',
                'min': 0.01,
                'max': 10.0,
                'step': 0.01,
                'default': 1.0,
                'best_component': 1.0,
                'description': 'Kernel coefficient for rbf, polynomial and sigmoid'
            }
        }
    }
}

# Default clustering method selection
DEFAULT_CLUSTERING_METHOD = 'kmeans'