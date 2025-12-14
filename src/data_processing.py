import pandas as pd
import os


def load_ae_data(filepath=None):
    """
    Loads a CSV file, removes rows with missing values,
    and returns a cleaned pandas DataFrame.
    
    Args:
        filepath (str, optional): Path to the CSV file. If None, defaults to data/sample_ae.csv
    
    Returns:
        pandas.DataFrame: A cleaned DataFrame with no missing values
    """
    # Get the path to the CSV file
    # If filepath is provided, use it; otherwise usdef load_ae_data(filepath=None):
    if filepath is None:
        # Define project root relative to this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        csv_path = os.path.join(project_root, 'data', 'sample_ae.csv')
    else:
        csv_path = filepath
    
    try:
        # Try standard read with auto-separator detection
        df = pd.read_csv(csv_path, sep=None, engine='python')
    except Exception:
        # If that fails (e.g. ParserError), try skipping first row
        # This handles the "labeled_data" header issue seen in debugging
        try:
            df = pd.read_csv(csv_path, sep=None, engine='python', skiprows=1)
        except Exception as e:
            print(f"Error loading CSV: {e}")
            raise e
    
    # Print the original number of rows
    print(f"Original number of rows: {len(df)}")
    
    # Split the combined column into separate columns
    if 'RXAUI$DRUG$Adverse_Event$count_of_reaction' in df.columns:
        split_cols = df['RXAUI$DRUG$Adverse_Event$count_of_reaction'].str.split('$', expand=True)
        df[['RXAUI', 'DRUG', 'Adverse_Event', 'count_of_reaction']] = split_cols
        # Drop the original combined column
        df = df.drop(columns=['RXAUI$DRUG$Adverse_Event$count_of_reaction'])
        # Convert count_of_reaction to integer type
        df['count_of_reaction'] = pd.to_numeric(df['count_of_reaction'], errors='coerce').astype('Int64')
    
    # Remove rows with missing values
    df_cleaned = df.dropna()
    
    # Convert count_of_reaction to regular integer type (after dropping missing values)
    if 'count_of_reaction' in df_cleaned.columns:
        df_cleaned['count_of_reaction'] = df_cleaned['count_of_reaction'].astype(int)
        
    # Standardize label column if present
    # Look for common ground truth column names
    label_candidates = ['label', 'is_adr', 'class', 'target', 'ground_truth']
    found_label = False
    for col in df_cleaned.columns:
        if col.lower() in label_candidates:
            print(f"Found ground truth label column: '{col}'. Renaming to 'label'.")
            df_cleaned = df_cleaned.rename(columns={col: 'label'})
            # Ensure label is numeric (0 or 1)
            try:
                df_cleaned['label'] = pd.to_numeric(df_cleaned['label'], errors='coerce').fillna(0).astype(int)
            except:
                pass
            found_label = True
            break
            
    if not found_label:
        print("No ground truth label column found (checked: label, is_adr, class, target, ground_truth).")
    
    # Print the number of rows after cleaning
    print(f"Number of rows after cleaning: {len(df_cleaned)}")
    
    # Print the first 5 rows of the cleaned DataFrame
    print("\nFirst 5 rows of cleaned DataFrame:")
    print(df_cleaned.head())
    
    return df_cleaned


if __name__ == "__main__":
    load_ae_data()

