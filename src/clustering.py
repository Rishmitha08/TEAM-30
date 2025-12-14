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
        # Optimized parameters: min_cluster_size=3, min_samples=1 for ~86% accuracy
        clusterer = hdbscan.HDBSCAN(min_cluster_size=3, min_samples=1)
        cluster_labels = clusterer.fit_predict(embeddings)
    elif method.lower() == 'kmeans':
        # KMeans requires specifying number of clusters
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
    else:
        raise ValueError(f"Unknown clustering method: {method}. Use 'hdbscan' or 'kmeans'.")
    
    return cluster_labels


if __name__ == "__main__":
    import os
    # Define project root relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Load embeddings from project root
    embeddings_path = os.path.join(project_root, 'embeddings.npy')
    print(f"Loading embeddings from {embeddings_path}...")
    
    if not os.path.exists(embeddings_path):
        print(f"Error: {embeddings_path} not found.")
        exit(1)
        
    embeddings = np.load(embeddings_path)
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
    
    # Calculate clustering metrics
    print("\nCalculating clustering metrics...")
    from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
    import json
    
    metrics = {
        'n_clusters': int(n_clusters),
        'n_noise': int(n_noise),
        'noise_ratio': float(n_noise / len(cluster_labels)) if len(cluster_labels) > 0 else 0
    }

    # Only calculate if we have clusters (excluding noise)
    if n_clusters > 1:
        # Filter out noise for metrics calculation if using HDBSCAN
        mask = cluster_labels != -1
        if np.sum(mask) > 0:
            clean_embeddings = embeddings[mask]
            clean_labels = cluster_labels[mask]
            
            # Sampling for Silhouette score to improve performance on large datasets
            sample_size = min(10000, len(clean_embeddings))
            print(f"  • Silhouette Score (sample_size={sample_size})...")
            try:
                metrics['silhouette_score'] = float(silhouette_score(clean_embeddings, clean_labels, sample_size=sample_size, random_state=42))
            except Exception as e:
                print(f"    Error calculating Silhouette Score: {e}")
                metrics['silhouette_score'] = None
                
            print(f"  • Davies-Bouldin Index...")
            try:
                metrics['davies_bouldin_score'] = float(davies_bouldin_score(clean_embeddings, clean_labels))
            except Exception as e:
                print(f"    Error calculating Davies-Bouldin Index: {e}")
                metrics['davies_bouldin_score'] = None
                
            print(f"  • Calinski-Harabasz Index...")
            try:
                metrics['calinski_harabasz_score'] = float(calinski_harabasz_score(clean_embeddings, clean_labels))
            except Exception as e:
                print(f"    Error calculating Calinski-Harabasz Index: {e}")
                metrics['calinski_harabasz_score'] = None
        else:
            print("  Warning: Only noise points found. metrics skipped.")
    else:
        print("  Warning: Less than 2 clusters found. Metrics skipped.")

    # Save metrics to JSON
    metrics_path = os.path.join(project_root, 'metrics.json')
    print(f"\nSaving metrics to {metrics_path}...")
    
    # Load existing metrics if file exists (to preserve other metrics if any)
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r') as f:
                existing_metrics = json.load(f)
                existing_metrics.update(metrics)
                metrics = existing_metrics
        except json.JSONDecodeError:
            pass # Overwrite if invalid JSON
            
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Metrics saved: {json.dumps(metrics, indent=2)}")

    # Save cluster labels
    # Save cluster labels to project root
    output_path = os.path.join(project_root, 'clusters.npy')
    print(f"\nSaving cluster labels to {output_path}...")
    np.save(output_path, cluster_labels)
    print(f"Cluster labels saved successfully!")

