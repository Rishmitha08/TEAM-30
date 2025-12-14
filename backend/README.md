# Pharmacovigilance Signal Detection - Backend API

Flask REST API backend for the Pharmacovigilance Signal Detection system.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### POST `/api/upload`
Upload a CSV file for processing.

**Request:**
- `file`: CSV file (multipart/form-data)

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully. Processing started."
}
```

### GET `/api/data/cleaned`
Get cleaned adverse event data with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 100)
- `search`: Search query (optional)

**Response:**
```json
{
  "data": [...],
  "total": 1000,
  "page": 1,
  "limit": 100
}
```

### GET `/api/clusters`
Get all cluster data.

**Response:**
```json
{
  "clusters": [
    {
      "cluster": 0,
      "frequency": 78,
      "severity": 1.0,
      "growth_rate": 1.0,
      "signal_score": 78.0
    }
  ]
}
```

### GET `/api/signals/top`
Get top N signals by signal score.

**Query Parameters:**
- `top_n`: Number of top signals (default: 5)

**Response:**
```json
{
  "signals": [...]
}
```

### GET `/api/signals/summaries`
Get LLM-generated cluster summaries.

**Query Parameters:**
- `top_n`: Number of top clusters to summarize (default: 5)

**Response:**
```json
{
  "summaries": [
    {
      "cluster": 0,
      "frequency": 78,
      "severity": 1.0,
      "growth_rate": 1.0,
      "signal_score": 78.0,
      "top_adverse_events": [...],
      "summary": "Human-readable summary text..."
    }
  ]
}
```

### GET `/api/clusters/search`
Search clusters by drug name or adverse event.

**Query Parameters:**
- `query`: Search query
- `type`: 'drug' or 'adverse_event' (default: 'adverse_event')

**Response:**
```json
{
  "clusters": [...]
}
```

### GET `/api/status`
Get current processing status.

**Response:**
```json
{
  "message": "Ready",
  "type": "info",
  "processing": false
}
```

## Integration with Python Scripts

The backend integrates with your existing Python scripts:

- `src/data_processing.py` - Data cleaning
- `src/embeddings.py` - Embedding generation
- `src/clustering.py` - Cluster analysis
- `src/signal_detection.py` - Signal detection and summaries

## CORS Configuration

CORS is enabled to allow the React frontend to make requests. Adjust the CORS settings in `app.py` if needed.

## Error Handling

All endpoints include error handling and return appropriate HTTP status codes:
- 200: Success
- 400: Bad Request
- 500: Internal Server Error

