import numpy as np
import pandas as pd
import json
from data_processing import load_ae_data
from datetime import datetime
import os


def detect_signals():
    """
    Detects safety signals from clustered adverse event data.
    Computes frequency, severity, and growth rate for each cluster,
    then calculates a Signal Score.
    
    Returns:
        pandas.DataFrame: DataFrame with signal scores for each cluster
    """
    # Define project root relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    # Load cleaned AE data
    print("Loading cleaned AE data...")
    df = load_ae_data()
    
    # Load cluster labels
    clusters_path = os.path.join(project_root, 'clusters.npy')
    print(f"Loading cluster labels from {clusters_path}...")
    
    if not os.path.exists(clusters_path):
        raise FileNotFoundError(f"Cluster file not found: {clusters_path}")
        
    cluster_labels = np.load(clusters_path)
    
    # Ensure cluster labels match DataFrame length
    if len(cluster_labels) != len(df):
        # If there's a mismatch, take the first len(df) labels
        # This can happen if clustering was done before data cleaning
        print(f"Warning: Cluster labels length ({len(cluster_labels)}) doesn't match DataFrame length ({len(df)})")
        print("Truncating cluster labels to match DataFrame...")
        cluster_labels = cluster_labels[:len(df)]
    
    # Add cluster labels as a new column
    df['cluster'] = cluster_labels
    
    # Filter out noise points (cluster == -1) for signal detection
    df_clustered = df[df['cluster'] != -1].copy()
    
    print(f"\nAnalyzing {len(df_clustered)} reports across clusters (excluding noise points)...")
    
    # Identify severity column
    severity_column = None
    severity_columns = ['seriousness', 'severity', 'serious', 'severity_score', 'seriousness_score']
    for col in severity_columns:
        if col in df_clustered.columns:
            severity_column = col
            break
    
    if severity_column:
        print(f"Using '{severity_column}' column for severity calculation")
    else:
        print("Warning: No severity column found. Using default severity score of 1.0 for all reports.")
    
    # Identify date/time column for growth rate calculation
    date_column = None
    date_columns = ['date', 'time', 'timestamp', 'event_date', 'report_date', 'date_received']
    for col in date_columns:
        if col in df_clustered.columns:
            date_column = col
            break
    
    if date_column:
        print(f"Using '{date_column}' column for growth rate calculation")
    else:
        print("Warning: No date/time column found. Growth rate will be set to 1.0 for all clusters.")
    
    # Compute metrics for each cluster
    cluster_stats = []
    
    for cluster_id in sorted(df_clustered['cluster'].unique()):
        cluster_data = df_clustered[df_clustered['cluster'] == cluster_id]
        
        # Frequency: number of reports in this cluster
        frequency = len(cluster_data)
        
        # Severity: average seriousness or predefined severity score
        if severity_column:
            # Try to convert to numeric if it's not already
            severity_values = pd.to_numeric(cluster_data[severity_column], errors='coerce')
            severity = severity_values.mean()
            if pd.isna(severity):
                severity = 1.0  # Default if conversion fails
        else:
            severity = 1.0  # Default severity
        
        # Growth rate: calculate based on time data if available
        growth_rate = 1.0  # Default growth rate
        if date_column:
            try:
                # Convert date column to datetime
                dates = pd.to_datetime(cluster_data[date_column], errors='coerce')
                dates = dates.dropna()
                
                if len(dates) > 1:
                    # Calculate growth rate as ratio of recent reports to older reports
                    # Split into two time periods
                    dates_sorted = dates.sort_values()
                    mid_point = len(dates_sorted) // 2
                    recent_count = len(dates_sorted[mid_point:])
                    older_count = len(dates_sorted[:mid_point])
                    
                    if older_count > 0:
                        growth_rate = recent_count / older_count
                    else:
                        growth_rate = 1.0
                else:
                    growth_rate = 1.0
            except Exception as e:
                print(f"Warning: Could not calculate growth rate for cluster {cluster_id}: {e}")
                growth_rate = 1.0
        
        # Calculate Signal Score = Frequency * Severity * Growth Rate
        signal_score = frequency * severity * growth_rate
        
        cluster_stats.append({
            'cluster': cluster_id,
            'frequency': frequency,
            'severity': severity,
            'growth_rate': growth_rate,
            'signal_score': signal_score
        })
    
    # Create DataFrame with signal scores
    signals_df = pd.DataFrame(cluster_stats)
    
    # Sort by signal score (descending)
    signals_df = signals_df.sort_values('signal_score', ascending=False)
    
    output_path = os.path.join(project_root, 'top_signals.csv')
    print(f"\nSaving top signals to {output_path}...")
    signals_df.to_csv(output_path, index=False)
    
    return signals_df, df_clustered


def generate_cluster_summaries(signals_df, df_clustered, top_n=5):
    """
    Generates human-readable summaries for drug safety clusters.
    
    Args:
        signals_df: DataFrame with cluster statistics (from detect_signals())
        df_clustered: DataFrame with cluster labels and adverse event data
        top_n: Number of top clusters to summarize (default: 5)
    
    Returns:
        list: List of summary dictionaries with cluster information and summaries
    """
    # Identify adverse event column
    ae_column = None
    ae_columns = ['Adverse_Event', 'adverse_event', 'reaction', 'adverse_reaction', 'event']
    for col in ae_columns:
        if col in df_clustered.columns:
            ae_column = col
            break
    
    summaries = []
    top_clusters = signals_df.head(top_n)
    
    for idx, row in top_clusters.iterrows():
        cluster_id = int(row['cluster'])
        frequency = int(row['frequency'])
        severity = row['severity']
        growth_rate = row['growth_rate']
        signal_score = row['signal_score']
        
        # Get cluster data
        cluster_data = df_clustered[df_clustered['cluster'] == cluster_id]
        
        # Get top adverse events
        top_adverse_events = []
        if ae_column:
            event_counts = cluster_data[ae_column].value_counts().head(5)
            top_adverse_events = event_counts.index.tolist()
        
        # Generate summary text
        summary_parts = []
        
        # Opening sentence about the cluster
        summary_parts.append(
            f"Cluster {cluster_id} represents a safety signal with {frequency} reported adverse events."
        )
        
        # Severity assessment
        if severity >= 2.0:
            severity_desc = "high"
            severity_risk = "This cluster shows elevated severity levels, indicating that the adverse events are generally serious in nature."
        elif severity >= 1.5:
            severity_desc = "moderate"
            severity_risk = "The average severity in this cluster is moderate, suggesting a mix of serious and non-serious events."
        else:
            severity_desc = "low to moderate"
            severity_risk = "While the severity levels are relatively lower, the frequency of reports warrants attention."
        
        summary_parts.append(severity_risk)
        
        # Growth rate assessment
        if growth_rate > 1.5:
            growth_desc = "increasing"
            growth_risk = f"The reporting rate for this cluster is {growth_rate:.1f}x higher in recent periods compared to earlier periods, indicating a concerning upward trend that requires immediate monitoring."
        elif growth_rate > 1.0:
            growth_desc = "slightly increasing"
            growth_risk = f"This cluster shows a modest increase in reporting frequency ({growth_rate:.1f}x), suggesting a potential emerging safety concern."
        elif growth_rate < 0.8:
            growth_desc = "decreasing"
            growth_risk = f"While the reporting rate has decreased ({growth_rate:.1f}x), the overall frequency and severity still warrant continued surveillance."
        else:
            growth_desc = "stable"
            growth_risk = "The reporting frequency has remained relatively stable over time."
        
        summary_parts.append(growth_risk)
        
        # Top adverse events
        if top_adverse_events:
            events_str = ", ".join(top_adverse_events[:3])  # Show top 3
            if len(top_adverse_events) > 3:
                events_str += f", and {len(top_adverse_events) - 3} other event type(s)"
            summary_parts.append(
                f"The most commonly reported adverse events in this cluster include: {events_str}."
            )
        
        # Closing recommendation
        if signal_score > 50:
            recommendation = "Given the high signal score, this cluster requires priority investigation and may necessitate regulatory action or product labeling updates."
        elif signal_score > 20:
            recommendation = "This cluster should be closely monitored, and additional analysis may be needed to understand the underlying risk factors."
        else:
            recommendation = "While the signal score is lower, continued surveillance is recommended to detect any emerging patterns."
        
        summary_parts.append(recommendation)
        
        # Combine into full summary
        full_summary = " ".join(summary_parts)
        
        summaries.append({
            'cluster': cluster_id,
            'frequency': frequency,
            'severity': severity,
            'growth_rate': growth_rate,
            'signal_score': signal_score,
            'top_adverse_events': top_adverse_events,
            'summary': full_summary
        })
    
    return summaries


if __name__ == "__main__":
    # Define project root relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Detect signals
    signals_df, df_clustered = detect_signals()
    
    # Load df again for classification metrics (need original df with labels)
    from data_processing import load_ae_data
    df = load_ae_data()
    
    # Print top 5 clusters with highest Signal Score
    print("\n" + "="*60)
    print("TOP 5 CLUSTERS WITH HIGHEST SIGNAL SCORE")
    print("="*60)
    top_5 = signals_df.head(5)
    
    for idx, row in top_5.iterrows():
        print(f"\nCluster {int(row['cluster'])}:")
        print(f"  Signal Score: {row['signal_score']:.2f}")
        print(f"  Frequency: {int(row['frequency'])} reports")
        print(f"  Severity: {row['severity']:.2f}")
        print(f"  Growth Rate: {row['growth_rate']:.2f}")
    
    # Save top signals to CSV
    output_path = 'top_signals.csv'
    print(f"\n\nSaving top signals to {output_path}...")
    signals_df.to_csv(output_path, index=False)
    print(f"Top signals saved successfully!")
    print(f"\nTotal clusters analyzed: {len(signals_df)}")

    # Calculate and save signal metrics
    metrics_path = os.path.join(project_root, 'metrics.json')
    
    # Compute classification metrics if ground truth label column is present
    classification_metrics = {}
    if 'label' in df.columns:
        print("\nFound 'label' column - calculating classification metrics...")
        
        # Load cluster labels
        clusters_path = os.path.join(project_root, 'clusters.npy')
        cluster_labels = np.load(clusters_path)
        if len(cluster_labels) > len(df):
            cluster_labels = cluster_labels[:len(df)]
        
        # Add cluster info to df for analysis
        df_temp = df.copy()
        df_temp['cluster'] = cluster_labels[:len(df_temp)]
        true_labels = df_temp['label'].fillna(0).astype(int)
        
        # Calculate majority class for each cluster
        cluster_majority = {}
        for cluster_id in df_temp['cluster'].unique():
            cluster_data = df_temp[df_temp['cluster'] == cluster_id]
            pos_count = (cluster_data['label'] == 1).sum()
            neg_count = (cluster_data['label'] == 0).sum()
            # Majority voting: if >50% positive, predict positive
            cluster_majority[cluster_id] = 1 if pos_count > neg_count else 0
        
        # Generate predictions based on cluster majority
        predictions = [cluster_majority.get(c, 0) for c in cluster_labels[:len(df_temp)]]
        pred_series = pd.Series(predictions, index=df_temp.index)
        
        tp = ((pred_series == 1) & (true_labels == 1)).sum()
        tn = ((pred_series == 0) & (true_labels == 0)).sum()
        fp = ((pred_series == 1) & (true_labels == 0)).sum()
        fn = ((pred_series == 0) & (true_labels == 1)).sum()
        total = len(df_temp)
        accuracy = (tp + tn) / total if total else 0
        precision = tp / (tp + fp) if (tp + fp) else 0
        recall = tp / (tp + fn) if (tp + fn) else 0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0
        classification_metrics = {
            'accuracy': round(accuracy, 4),
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1, 4)
        }
        print(f"  Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
    
    signal_metrics = {
        'total_signals': len(signals_df),
        'mean_signal_score': float(signals_df['signal_score'].mean()) if not signals_df.empty else 0,
        'max_signal_score': float(signals_df['signal_score'].max()) if not signals_df.empty else 0,
        'min_signal_score': float(signals_df['signal_score'].min()) if not signals_df.empty else 0,
        'high_priority_signals': int(len(signals_df[signals_df['signal_score'] > 50])),
        'avg_growth_rate': float(signals_df['growth_rate'].mean()) if not signals_df.empty else 0,
        'avg_severity': float(signals_df['severity'].mean()) if not signals_df.empty else 0
    }
    # Merge classification metrics into overall metrics
    signal_metrics.update(classification_metrics)
    
    print("\nCalculated signal metrics:")
    print(json.dumps(signal_metrics, indent=2))
    
    # Update existing metrics file
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r') as f:
                existing_metrics = json.load(f)
            existing_metrics.update(signal_metrics)
            
            with open(metrics_path, 'w') as f:
                json.dump(existing_metrics, f, indent=2)
            print(f"Updated metrics in {metrics_path}")
        except Exception as e:
            print(f"Error updating metrics file: {e}")
    else:
        # Create new if doesn't exist (though clustering should have created it)
        with open(metrics_path, 'w') as f:
            json.dump(signal_metrics, f, indent=2)
        print(f"Created metrics file at {metrics_path}")
    
    # Generate and print human-readable summaries
    print("\n" + "="*80)
    print("PHARMACOVIGILANCE CLUSTER SUMMARIES")
    print("="*80)
    summaries = generate_cluster_summaries(signals_df, df_clustered, top_n=5)
    
    for summary in summaries:
        print(f"\n{'='*80}")
        print(f"CLUSTER {summary['cluster']}")
        print(f"{'='*80}")
        print(f"\n{summary['summary']}\n")
        print(f"Key Metrics:")
        print(f"  • Number of reports: {summary['frequency']}")
        print(f"  • Average severity: {summary['severity']:.2f}")
        print(f"  • Growth rate: {summary['growth_rate']:.2f}x")
        print(f"  • Signal score: {summary['signal_score']:.2f}")
        if summary['top_adverse_events']:
            print(f"  • Top adverse events: {', '.join(summary['top_adverse_events'][:5])}")

