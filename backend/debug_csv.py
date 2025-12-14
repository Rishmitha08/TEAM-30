import pandas as pd
import os
import sys

# Hardcoded project root for debugging
PROJECT_ROOT = '/Users/prasannaa/Desktop/pharmacovigilance-agent'
csv_path = os.path.join(PROJECT_ROOT, 'data', 'sample_ae.csv')

print(f"Trying to load: {csv_path}")

try:
    print("\nAttempt 1: Standard read")
    df = pd.read_csv(csv_path, sep=None, engine='python')
    print("Success!")
    print(df.head())
except Exception as e:
    print(f"Attempt 1 Failed: {e}")

try:
    print("\nAttempt 2: Skip 1 row")
    df = pd.read_csv(csv_path, sep=None, engine='python', skiprows=1)
    print("Success!")
    print(f"Columns: {df.columns.tolist()}")
    print(df.head())
except Exception as e:
    print(f"Attempt 2 Failed: {e}")
