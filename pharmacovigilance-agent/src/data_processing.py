import pandas as pd
import os


def load_ae_data():
    """
    Loads a CSV file named data/sample_ae.csv, removes rows with missing values,
    and returns a cleaned pandas DataFrame.
    
    Returns:
        pandas.DataFrame: A cleaned DataFrame with no missing values
    """
    # Get the path to the CSV file
    # Assuming the script is run from the project root
    csv_path = os.path.join('data', 'sample_ae.csv')
    
    # Load the CSV file
    df = pd.read_csv(csv_path, sep="\t", low_memory=False)
    
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
    
    # Print the number of rows after cleaning
    print(f"Number of rows after cleaning: {len(df_cleaned)}")
    
    # Print the first 5 rows of the cleaned DataFrame
    print("\nFirst 5 rows of cleaned DataFrame:")
    print(df_cleaned.head())
    
    return df_cleaned


if __name__ == "__main__":
    load_ae_data()

