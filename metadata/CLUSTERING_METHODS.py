# Clustering Configuration
CLUSTERING_METHODS = {
    'no_clustering': {
        'name': 'No Clustering',
        'description': 'No clustering applied to the data',
        'selected': True,
        'parameters': {},
        'pros': [
            'Simple and straightforward approach',
            'No computational cost or time required',
            'Preserves original data structure completely'
        ],
        'cons': [
            'No grouping or pattern discovery',
            'May miss important underlying data relationships',
            'Not useful for exploratory data analysis requiring clusters'
        ],
        'limitations': [
            'Does not perform any clustering operations',
            'Cannot identify natural groupings in data',
            'No cluster validation or quality metrics available'
        ],
        'expectations': [
            'Data remains completely unchanged',
            'No cluster assignments or labels generated',
            'Analysis proceeds without grouping considerations'
        ]
    },
    'hierarchical': {
        'name': 'Hierarchical Clustering',
        'description': 'Builds a hierarchy of clusters using agglomerative approach',
        'selected': False,
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
        },
        'pros': [
            'Produces a dendrogram for visual interpretation',
            'No need to specify number of clusters beforehand',
            'Can handle different cluster shapes and sizes',
            'Deterministic results (no random initialization)'
        ],
        'cons': [
            'Computationally expensive for large datasets',
            'Sensitive to noise and outliers',
            'Cannot undo previous merges once made',
            'May not scale well with high-dimensional data'
        ],
        'limitations': [
            'Not suitable for very large datasets (>10,000 samples)',
            'Assumes hierarchical structure may not exist',
            'Memory intensive due to distance matrix storage',
            'Difficult to automate cluster number selection'
        ],
        'expectations': [
            'Good performance on small to medium datasets',
            'Visual dendrogram for cluster interpretation',
            'Hierarchical relationship between clusters',
            'Stable results across multiple runs'
        ]
    },
    'kmeans': {
        'name': 'K-Means Clustering',
        'description': 'Partitions data into k clusters by minimizing within-cluster sum of squares',
        'selected': False,
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
        },
        'pros': [
            'Fast and efficient for large datasets',
            'Scalable to high-dimensional data',
            'Easy to implement and understand',
            'Guaranteed convergence (with Lloyd\'s algorithm)'
        ],
        'cons': [
            'Requires specifying number of clusters beforehand',
            'Sensitive to initial centroid positions',
            'Assumes spherical, equally-sized clusters',
            'Affected by outliers and noise'
        ],
        'limitations': [
            'May converge to local optima',
            'Not suitable for non-spherical clusters',
            'Fails with categorical or mixed data types',
            'Performance degrades with high-dimensional data (curse of dimensionality)'
        ],
        'expectations': [
            'Good performance on well-separated, spherical clusters',
            'Fast execution on large datasets',
            'Reproducible results with fixed random seed',
            'Clear cluster centroids and assignments'
        ]
    },
    'dbscan': {
        'name': 'DBSCAN',
        'description': 'Density-based clustering that finds clusters of varying shapes and sizes',
        'selected': False,
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
        },
        'pros': [
            'Can find clusters of arbitrary shapes',
            'Automatically determines number of clusters',
            'Robust to outliers and noise',
            'No need to specify cluster count beforehand'
        ],
        'cons': [
            'Sensitive to parameter selection (eps, min_samples)',
            'Struggles with varying densities',
            'May classify border points as noise',
            'Not suitable for high-dimensional data'
        ],
        'limitations': [
            'Parameter tuning can be challenging',
            'Fails when clusters have significantly different densities',
            'Cannot cluster data with varying densities well',
            'May require domain knowledge for parameter setting'
        ],
        'expectations': [
            'Effective for spatial data with noise',
            'Good at identifying outliers as noise points',
            'Clusters of varying shapes and sizes',
            'Automatic cluster detection without predefined count'
        ]
    },
    'gaussian_mixture': {
        'name': 'Gaussian Mixture Model',
        'description': 'Probabilistic clustering using Gaussian mixture models',
        'selected': False,
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
        },
        'pros': [
            'Provides probabilistic cluster assignments',
            'Can model clusters with different shapes and orientations',
            'Handles overlapping clusters naturally',
            'Provides uncertainty estimates for cluster membership'
        ],
        'cons': [
            'Computationally more expensive than K-means',
            'May converge to local optima',
            'Requires specifying number of components',
            'Assumes Gaussian distribution of data'
        ],
        'limitations': [
            'Sensitive to initialization',
            'May not perform well with non-Gaussian data',
            'Higher computational complexity',
            'Requires careful parameter tuning'
        ],
        'expectations': [
            'Soft cluster assignments with probabilities',
            'Better handling of overlapping clusters than hard clustering',
            'Model parameters describing cluster distributions',
            'Potential for better fit to complex data distributions'
        ]
    },
    'spectral': {
        'name': 'Spectral Clustering',
        'description': 'Clustering using the spectrum of the similarity matrix',
        'selected': False,
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
        },
        'pros': [
            'Can find non-convex clusters',
            'Works well with complex cluster geometries',
            'Less sensitive to initialization than K-means',
            'Can use different similarity measures'
        ],
        'cons': [
            'Computationally expensive',
            'Requires specifying number of clusters',
            'Memory intensive for large datasets',
            'Parameter selection can be challenging'
        ],
        'limitations': [
            'Not scalable to very large datasets',
            'May not perform well with high-dimensional data',
            'Eigenvalue computation can be numerically unstable',
            'Requires careful kernel parameter tuning'
        ],
        'expectations': [
            'Good performance on small to medium datasets',
            'Effective for clusters with complex shapes',
            'Robust to some extent of noise',
            'Better results than traditional methods for certain data types'
        ]
    },
}

# Default clustering method selection
DEFAULT_CLUSTERING_METHOD = 'no_clustering'