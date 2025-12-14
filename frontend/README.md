# Pharmacovigilance Signal Detection - Frontend

A modern React.js frontend for the Pharmacovigilance Signal Detection system.

## Features

- **Dataset Upload**: Drag-and-drop CSV file upload with processing status
- **Data Table View**: Interactive table with sorting and search functionality
- **Clusters View**: Visual display of cluster analysis with top signals highlighted
- **Cluster Summaries**: LLM-generated human-readable summaries for each cluster
- **Search & Filter**: Filter clusters by drug name or adverse event

## Technology Stack

- **React 18.2.0**: Modern React with hooks
- **Tailwind CSS**: Utility-first CSS framework (via CDN)
- **Axios**: HTTP client for API communication

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API Endpoint

Create a `.env` file in the `frontend` directory:

```env
REACT_APP_API_URL=http://localhost:5000/api
```

Or modify the default in `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### 3. Start Development Server

```bash
npm start
```

The app will open at `http://localhost:3000`

## Backend API Integration

The frontend expects the following API endpoints:

### Required Endpoints

1. **POST `/api/upload`**
   - Upload CSV file
   - Returns: `{ success: boolean, message: string }`

2. **GET `/api/data/cleaned`**
   - Get cleaned AE data
   - Query params: `page`, `limit`, `search`
   - Returns: `{ data: [...], total: number, page: number }`

3. **GET `/api/clusters`**
   - Get all clusters
   - Returns: `{ clusters: [...] }`

4. **GET `/api/signals/top`**
   - Get top N signals
   - Query params: `top_n`
   - Returns: `{ signals: [...] }`

5. **GET `/api/signals/summaries`**
   - Get cluster summaries
   - Query params: `top_n`
   - Returns: `{ summaries: [...] }`

6. **GET `/api/clusters/search`**
   - Search clusters
   - Query params: `query`, `type` ('drug' or 'adverse_event')
   - Returns: `{ clusters: [...] }`

7. **GET `/api/status`**
   - Get processing status
   - Returns: `{ message: string, type: string, processing: boolean }`

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.js
│   │   ├── Sidebar.js
│   │   ├── DataTableView.js
│   │   ├── ClustersView.js
│   │   ├── SummariesView.js
│   │   └── Footer.js
│   ├── services/
│   │   └── api.js
│   ├── App.js
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

## Backend Integration Example (Flask)

Here's a minimal Flask backend example to get you started:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename.endswith('.csv'):
        # Save and process file
        filepath = f'data/{file.filename}'
        file.save(filepath)
        # Trigger processing pipeline
        return jsonify({'success': True, 'message': 'File uploaded successfully'})
    return jsonify({'success': False, 'message': 'Invalid file type'}), 400

@app.route('/api/data/cleaned', methods=['GET'])
def get_cleaned_data():
    # Load and return cleaned data
    df = pd.read_csv('data/sample_ae.csv', sep='\t')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 100))
    # Implement pagination
    return jsonify({'data': df.to_dict('records'), 'total': len(df), 'page': page})

@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    # Load clusters from clusters.npy or top_signals.csv
    import numpy as np
    clusters = np.load('clusters.npy')
    # Process and return
    return jsonify({'clusters': []})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({'message': 'Ready', 'type': 'info', 'processing': False})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Notes

- The frontend uses mock data when API calls fail (for demonstration)
- All API calls include error handling
- The UI is responsive and works on desktop and tablet devices
- Tailwind CSS is loaded via CDN for quick setup (consider using npm package for production)

