
import numpy as np

# Load embeddings
embeddings = np.load("embeddings.npy")
print(embeddings.shape)  # e.g., (501, 384)

# Load cluster labels
clusters = np.load("clusters.npy")
print(clusters[:20])     # see first 20 cluster labels

