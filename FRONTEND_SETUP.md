# Pharmacovigilance Signal Detection - Complete Setup Guide

This guide will help you set up and run the complete Pharmacovigilance Signal Detection system with React frontend and Flask backend.

## Project Structure

```
pharmacovigilance-agent/
├── frontend/          # React.js frontend application
├── backend/           # Flask REST API backend
├── src/               # Python processing scripts
│   ├── data_processing.py
│   ├── embeddings.py
│   ├── clustering.py
│   └── signal_detection.py
└── data/              # Data files
```

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

The backend will start on `http://localhost:5000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The frontend will start on `http://localhost:3000` and automatically open in your browser.

## Complete Setup Instructions

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** and npm
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install flask flask-cors pandas numpy werkzeug
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 3: Configure API Endpoint (Optional)

If your backend runs on a different port or host, create a `.env` file in the `frontend` directory:

```env
REACT_APP_API_URL=http://localhost:5000/api
```

### Step 4: Start the Backend Server

```bash
cd backend
python app.py
```

You should see:
```
Starting Pharmacovigilance API server...
API will be available at http://localhost:5000
```

### Step 5: Start the Frontend Development Server

In a new terminal:

```bash
cd frontend
npm start
```

The React app will open at `http://localhost:3000`

## Usage

### 1. Upload a Dataset

1. Click the upload area in the left sidebar
2. Select or drag-and-drop a CSV file
3. The system will automatically:
   - Clean the data
   - Generate embeddings
   - Perform clustering
   - Detect signals
   - Generate summaries

### 2. View Data Table

- Navigate to the "Data Table" tab
- Use the search box to filter data
- Click column headers to sort
- Navigate pages using Previous/Next buttons

### 3. View Clusters

- Navigate to the "Clusters" tab
- See top 5 clusters highlighted by priority
- View all clusters in a sortable table
- Search clusters by drug name or adverse event

### 4. View Cluster Summaries

- Navigate to the "Cluster Summaries" tab
- Read LLM-generated human-readable summaries
- Expand clusters to see detailed metrics
- View top adverse events for each cluster

## Features

### Frontend Features

✅ **Modern React UI** with Tailwind CSS
✅ **Drag-and-drop file upload**
✅ **Interactive data tables** with sorting and search
✅ **Visual cluster display** with priority highlighting
✅ **LLM-generated summaries** in human-readable format
✅ **Real-time status updates** during processing
✅ **Responsive design** for desktop and tablet

### Backend Features

✅ **RESTful API** with Flask
✅ **File upload handling** with validation
✅ **Data pagination** and search
✅ **Cluster analysis** integration
✅ **Signal detection** with summaries
✅ **CORS enabled** for frontend access

## API Endpoints

The backend provides the following endpoints:

- `POST /api/upload` - Upload CSV file
- `GET /api/data/cleaned` - Get cleaned data (paginated)
- `GET /api/clusters` - Get all clusters
- `GET /api/signals/top` - Get top N signals
- `GET /api/signals/summaries` - Get cluster summaries
- `GET /api/clusters/search` - Search clusters
- `GET /api/status` - Get processing status

See `backend/README.md` for detailed API documentation.

## Troubleshooting

### Backend Issues

**Port 5000 already in use:**
```bash
# Change port in backend/app.py
app.run(debug=True, port=5001, host='0.0.0.0')
```

**Module not found errors:**
```bash
# Ensure you're in the project root when running scripts
# Add src to Python path if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Frontend Issues

**API connection errors:**
- Check that backend is running on port 5000
- Verify CORS is enabled in backend
- Check browser console for detailed error messages

**npm install fails:**
```bash
# Clear npm cache
npm cache clean --force
# Try again
npm install
```

### Data Processing Issues

**Missing data files:**
- Ensure `data/sample_ae.csv` exists
- Run `python src/fetch_dataset.py` to download sample data

**Clustering fails:**
- Check that embeddings.npy exists
- Run `python src/embeddings.py` first
- Then run `python src/clustering.py`

## Development

### Frontend Development

The React app uses:
- **React 18.2.0** with hooks
- **Tailwind CSS** via CDN (consider npm package for production)
- **Axios** for HTTP requests

Hot reload is enabled during development.

### Backend Development

The Flask app runs in debug mode by default. For production:
- Set `debug=False`
- Use a production WSGI server (e.g., Gunicorn)
- Configure proper CORS settings
- Add authentication/authorization

## Production Build

### Build Frontend

```bash
cd frontend
npm run build
```

This creates an optimized build in `frontend/build/` that can be served by any static file server.

### Deploy Backend

For production deployment:
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Configure reverse proxy (Nginx, Apache)
3. Set up SSL/TLS certificates
4. Configure environment variables
5. Set up logging and monitoring

## Next Steps

1. **Customize the UI**: Modify components in `frontend/src/components/`
2. **Add authentication**: Implement user login/registration
3. **Enhance API**: Add more endpoints for advanced features
4. **Add visualizations**: Integrate charts/graphs for cluster analysis
5. **Export functionality**: Add PDF/Excel export for reports
6. **Real-time updates**: Use WebSockets for live status updates

## Support

For issues or questions:
1. Check the README files in `frontend/` and `backend/`
2. Review the API documentation
3. Check browser console and server logs for errors

