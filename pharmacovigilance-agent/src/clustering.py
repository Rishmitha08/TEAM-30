import numpy as np
import hdbscan
from sklearn.cluster import KMeans


def cluster_embeddings(embeddings, method='hdbscan', n_clusters=10):
    """
    Clusters embeddings using HDBSCAN or KMeans.
    
    Args:
        embeddings: numpy array of embeddings
        method: 'hdbscan' or 'kmeans'
        n_clusters: number of clusters for KMeans (ignored for HDBSCAN)
    
    Returns:
        numpy.ndarray: Cluster labels
    """
    print(f"Clustering embeddings using {method.upper()}...")
    
    if method.lower() == 'hdbscan':
        # HDBSCAN automatically determines number of clusters
        clusterer = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=3)
        cluster_labels = clusterer.fit_predict(embeddings)
    elif method.lower() == 'kmeans':
        # KMeans requires specifying number of clusters
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
    else:
        raise ValueError(f"Unknown clustering method: {method}. Use 'hdbscan' or 'kmeans'.")
    
    return cluster_labels


if __name__ == "__main__":
    # Load embeddings
    print("Loading embeddings from embeddings.npy...")
    embeddings = np.load('embeddings.npy')
    original_size = embeddings.shape[0]
    print(f"Loaded embeddings shape: {embeddings.shape}")
    
    # Demo-scale optimization: Sample only the first 50,000 embeddings for clustering
    # This reduces computational complexity and memory usage for large-scale datasets
    # In production, consider using batch processing or distributed clustering
    max_samples = 50000
    if original_size > max_samples:
        embeddings = embeddings[:max_samples]
        print(f"\nDemo-scale optimization: Sampling first {max_samples:,} embeddings")
        print(f"Original size: {original_size:,} embeddings")
        print(f"Sampled size: {embeddings.shape[0]:,} embeddings")
    else:
        print(f"\nUsing all {original_size:,} embeddings (no sampling needed)")
    
    # Perform clustering (using HDBSCAN by default)
    cluster_labels = cluster_embeddings(embeddings, method='hdbscan')
    
    # Print number of clusters and sample cluster assignments
    unique_clusters = np.unique(cluster_labels)
    n_clusters = len(unique_clusters[unique_clusters != -1])  # Exclude noise points (-1) for HDBSCAN
    n_noise = np.sum(cluster_labels == -1) if -1 in cluster_labels else 0
    
    print(f"\nNumber of clusters: {n_clusters}")
    if n_noise > 0:
        print(f"Number of noise points (outliers): {n_noise}")
    
    print(f"\nSample cluster assignments (first 20):")
    print(cluster_labels[:20])
    
    print(f"\nCluster distribution:")
    unique, counts = np.unique(cluster_labels, return_counts=True)
    for cluster_id, count in zip(unique, counts):
        if cluster_id == -1:
            print(f"  Noise (outliers): {count}")
        else:
            print(f"  Cluster {cluster_id}: {count} points")
    
    # Save cluster labels
    output_path = 'clusters.npy'
    print(f"\nSaving cluster labels to {output_path}...")
    np.save(output_path, cluster_labels)
    print(f"Cluster labels saved successfully!")

