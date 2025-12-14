import numpy as np
from data_processing import load_ae_data
from sentence_transformers import SentenceTransformer
import os


def generate_embeddings():
    """
    Loads cleaned AE data and generates embeddings for the text column.
    Uses SentenceTransformers for embedding generation.
    
    Returns:
        numpy.ndarray: Array of embeddings
    """
    # Load the cleaned AE data
    print("Loading cleaned AE data...")
    df = load_ae_data()
    
    # Determine which text column to use ('reaction' or 'adverse_event')
    text_column = None
    if 'reaction' in df.columns:
        text_column = 'reaction'
    elif 'adverse_event' in df.columns:
        text_column = 'adverse_event'
    else:
        # If neither exists, try to find a text-like column
        # Look for columns with string/object dtype
        text_columns = df.select_dtypes(include=['object']).columns
        if len(text_columns) > 0:
            text_column = text_columns[0]
            print(f"Warning: 'reaction' or 'adverse_event' not found. Using '{text_column}' instead.")
        else:
            raise ValueError("No suitable text column found for embedding generation.")
    
    print(f"Using column '{text_column}' for embeddings")
    
    # Extract text data
    texts = df[text_column].astype(str).tolist()
    print(f"Generating embeddings for {len(texts)} texts...")
    
    # Initialize SentenceTransformer model
    # Using a general-purpose model suitable for clinical/medical text
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embeddings
    ae_embeddings = model.encode(texts, show_progress_bar=True)
    
    # Convert to numpy array if not already
    ae_embeddings = np.array(ae_embeddings)
    
    return ae_embeddings


if __name__ == "__main__":
    # Define project root relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Generate embeddings
    embeddings = generate_embeddings()
    
    # Print shape and sample embedding for verification
    print(f"Sample embedding shape: {embeddings[0].shape}")
    
    # Save embeddings to file
    output_path = 'embeddings.npy'
    print(f"\nSaving embeddings to {output_path}...")
    np.save(output_path, embeddings)
    print(f"Embeddings saved successfully!")

