from datasets import load_dataset
import pandas as pd
import os


def fetch_and_save_dataset():
    """
    Loads the Hugging Face dataset "ml6team/clinical-adverse-events",
    converts the 'train' split to a pandas DataFrame, and saves it as data/sample_ae.csv.
    
    Returns:
        pandas.DataFrame: The loaded dataset as a DataFrame
    """
    # Load the dataset from Hugging Face
    print("Loading dataset from Hugging Face...")
    dataset = load_dataset("ml6team/clinical-adverse-events")
    
    # Convert the 'train' split to pandas DataFrame
    df = dataset['train'].to_pandas()
    
    # Ensure the data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    csv_path = os.path.join('data', 'sample_ae.csv')
    print(f"Saving dataset to {csv_path}...")
    df.to_csv(csv_path, index=False)
    print(f"Dataset saved successfully! Total rows: {len(df)}")
    
    return df


if __name__ == "__main__":
    # Fetch and save the dataset
    df = fetch_and_save_dataset()
    
    # Print the first 5 rows for testing
    print("\nFirst 5 rows of the dataset:")
    print(df.head())
    
    print(f"\nDataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

