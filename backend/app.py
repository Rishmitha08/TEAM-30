"""
Flask API backend for Pharmacovigilance Signal Detection System

This Flask application provides REST API endpoints for:
- Uploading and processing adverse event (AE) datasets
- Retrieving signal detection results with cluster summaries
- Accessing top safety signals with human-readable summaries

The backend integrates with existing Python modules:
- data_processing.py: Data cleaning and preprocessing
- embeddings.py: Embedding generation for AE text
- clustering.py: Cluster analysis using HDBSCAN
- signal_detection.py: Signal detection and summary generation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import os
import sys
from werkzeug.utils import secure_filename
import subprocess
import threading

# Add src directory to Python path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import project modules
from data_processing import load_ae_data
from signal_detection import detect_signals, generate_cluster_summaries

# Initialize Flask application
app = Flask(__name__)
# Set maximum upload size to 50MB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max file size

# Enable CORS for all origins to allow frontend access
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/reset', methods=['POST'])
def reset_data():
    """
    Reset the application state by deleting uploaded and processed files.
    """
    try:
        # Define files to delete
        files_to_delete = [
            os.path.join(app.config['UPLOAD_FOLDER'], 'sample_ae.csv'),
            os.path.join(PROJECT_ROOT, 'embeddings.npy'),
            os.path.join(PROJECT_ROOT, 'clusters.npy'),
            os.path.join(PROJECT_ROOT, 'top_signals.csv'),
            os.path.join(PROJECT_ROOT, 'metrics.json')
        ]
        
        deleted = []
        for file_path in files_to_delete:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted.append(os.path.basename(file_path))
                
        return jsonify({
            'success': True, 
            'message': 'Application state reset successfully',
            'deleted_files': deleted
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Configuration
# Configuration
PORT = 5001  # Flask server port
# Use data directory in project root, not backend/data
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'data')
DATA_FOLDER = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure data directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): Name of the file to check
    
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_csv_robust(filepath):
    """
    Robustly read a CSV file, handling potential header issues.
    Tries standard read first, then skips 1 row if that fails.
    """
    try:
        # Try standard read with auto-separator detection
        return pd.read_csv(filepath, sep=None, engine='python')
    except Exception:
        # If that fails (e.g. ParserError due to bad header), try skipping first row
        try:
            return pd.read_csv(filepath, sep=None, engine='python', skiprows=1)
        except Exception as e:
            # If both fail, raise the original error or the new one
            raise e


def run_processing_pipeline(filepath):
    """
    Run the complete processing pipeline after file upload.
    
    This function executes the full pipeline:
    1. Data processing and cleaning
    2. Embedding generation
    3. Clustering
    4. Signal detection
    
    Args:
        filepath (str): Path to the uploaded CSV file
    """
    try:
        # Change to project root directory to run scripts
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)
        
        # Step 1: Data processing (handled by load_ae_data when called)
        # The file is already saved, so load_ae_data will use it
        
        # Step 2: Generate embeddings
        # Run embeddings.py script
        subprocess.run([sys.executable, 'src/embeddings.py'], 
                      check=True, capture_output=True)
        
        # Step 3: Clustering
        # Run clustering.py script
        subprocess.run([sys.executable, 'src/clustering.py'], 
                      check=True, capture_output=True)
        
        # Step 4: Signal detection
        # Run signal_detection.py script
        # This will generate top_signals.csv and update metrics.json
        subprocess.run([sys.executable, 'src/signal_detection.py'], 
                      check=True, capture_output=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error in processing pipeline: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error in processing pipeline: {e}")
        raise


@app.route('/api/signals', methods=['GET'])
def get_signals():
    """
    GET endpoint to retrieve top 5 safety signal clusters with summaries.
    
    This endpoint:
    - Loads the processed data and cluster information
    - Detects signals and generates summaries
    - Returns top 5 clusters with all metrics and human-readable summaries
    
    Returns:
        JSON response with:
        - success (bool): Whether the operation was successful
        - signals (list): List of top 5 cluster summaries, each containing:
            - cluster (int): Cluster ID
            - frequency (int): Number of reports in cluster
            - severity (float): Average severity score
            - growth_rate (float): Growth rate multiplier
            - signal_score (float): Calculated signal score
            - top_adverse_events (list): Most common adverse events
            - summary (str): Human-readable summary text
        - error (str): Error message if operation failed
    
    Example response:
        {
            "success": true,
            "signals": [
                {
                    "cluster": 14,
                    "frequency": 78,
                    "severity": 1.0,
                    "growth_rate": 1.0,
                    "signal_score": 78.0,
                    "top_adverse_events": ["Event1", "Event2"],
                    "summary": "Cluster 14 represents..."
                }
            ]
        }
    """
    try:
        # Check if required files exist
        clusters_path = os.path.join(PROJECT_ROOT, 'clusters.npy')
        if not os.path.exists(clusters_path):
            return jsonify({
                'success': False,
                'error': 'Clusters not found. Please upload and process a dataset first.'
            }), 404
        
        csv_path = os.path.join(DATA_FOLDER, 'sample_ae.csv')
        if not os.path.exists(csv_path):
            return jsonify({
                'success': False,
                'error': 'Dataset not found. Please upload a CSV file first.'
            }), 404
        
        # Detect signals and get cluster statistics
        # We need to ensure we run this in the project root logic
        original_dir = os.getcwd()
        try:
            # Change to project root for the scripts to find their dependencies/files relative to CWD if needed
            # Although we fixed paths, the scripts might still assume CWD for some things
            # But let's check: detect_signals calls load_ae_data which defaults to relative 'data/...'
            # So we MUST be in project root for that default to work, OR we pass the path.
            # detect_signals does NOT accept args. So we must chdir.
            os.chdir(PROJECT_ROOT)
            
            if 'src' not in sys.path:
                sys.path.append(os.path.join(PROJECT_ROOT, 'src'))
                
            signals_df, df_clustered = detect_signals()
            
            # Generate human-readable summaries for top 5 clusters
            summaries = generate_cluster_summaries(signals_df, df_clustered, top_n=5)
        finally:
            os.chdir(original_dir)
        
        # Convert summaries to JSON-serializable format
        signals_json = []
        for summary in summaries:
            signals_json.append({
                'cluster': int(summary['cluster']),
                'frequency': int(summary['frequency']),
                'severity': float(summary['severity']),
                'growth_rate': float(summary['growth_rate']),
                'signal_score': float(summary['signal_score']),
                'top_adverse_events': summary['top_adverse_events'],
                'summary': summary['summary']
            })
        
        return jsonify({
            'success': True,
            'signals': signals_json
        }), 200
        
    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': f'Required file not found: {str(e)}'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error retrieving signals: {str(e)}'
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    POST endpoint to upload a CSV file and trigger the processing pipeline.
    
    This endpoint:
    1. Validates the uploaded file (must be CSV)
    2. Saves the file to the data/ directory
    3. Runs the complete processing pipeline:
       - Data cleaning and preprocessing
       - Embedding generation
       - Clustering analysis
       - Signal detection
    4. Returns the top 5 cluster summaries
    
    Request:
        - Content-Type: multipart/form-data
        - Body: Form data with 'file' field containing CSV file
    
    Returns:
        JSON response with:
        - success (bool): Whether upload and processing were successful
        - message (str): Status message
        - signals (list): Top 5 cluster summaries (same format as GET /api/signals)
        - error (str): Error message if operation failed
    
    Example response:
        {
            "success": true,
            "message": "File uploaded and processed successfully",
            "signals": [...]
        }
    """
    # #region agent log
    import json
    log_path = '/Users/prasannaa/Desktop/pharmacovigilance-agent/.cursor/debug.log'
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'upload-backend',
                'hypothesisId': 'E',
                'location': 'app.py:228',
                'message': 'Upload endpoint called',
                'data': {
                    'method': request.method,
                    'hasFiles': 'files' in request.__dict__,
                    'filesKeys': list(request.files.keys()) if hasattr(request, 'files') else [],
                    'contentType': request.content_type
                },
                'timestamp': int(__import__('time').time() * 1000)
            }) + '\n')
    except: pass
    # #endregion

    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided in request'
            }), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'upload-backend',
                    'hypothesisId': 'F',
                    'location': 'app.py:246',
                    'message': 'File validation',
                    'data': {
                        'filename': file.filename,
                        'isAllowed': allowed_file(file.filename),
                        'fileSize': getattr(file, 'content_length', 'unknown')
                    },
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion

        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only CSV files are allowed.'
            }), 400
        
        # Secure the filename and save to data directory
        filename = secure_filename(file.filename)
        # Save as sample_ae.csv to match expected filename in processing pipeline
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'sample_ae.csv')
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'upload-backend',
                    'hypothesisId': 'G',
                    'location': 'app.py:258',
                    'message': 'Before file save',
                    'data': {
                        'filepath': filepath,
                        'uploadFolder': app.config['UPLOAD_FOLDER'],
                        'folderExists': os.path.exists(app.config['UPLOAD_FOLDER'])
                    },
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Save the uploaded file
        file.save(filepath)
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'upload-backend',
                    'hypothesisId': 'J',
                    'location': 'app.py:318',
                    'message': 'File saved successfully',
                    'data': {'filepath': filepath, 'fileExists': os.path.exists(filepath)},
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        
        # Run the complete processing pipeline
        # This includes: data processing, embeddings, clustering, signal detection
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        original_dir = os.getcwd()
        
        try:
            os.chdir(project_root)
            
            # DEBUG: Check file timestamps before processing
            debug_files = ['data/sample_ae.csv', 'embeddings.npy', 'clusters.npy']
            import time
            import json
            log_path = '/Users/prasannaa/Desktop/pharmacovigilance-agent/.cursor/debug.log'
            
            try:
                pre_times = {}
                for f in debug_files:
                    if os.path.exists(f):
                        pre_times[f] = os.path.getmtime(f)
                
                with open(log_path, 'a') as logf:
                    logf.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'upload-backend',
                        'hypothesisId': 'TIMESTAMP_PRE',
                        'message': 'File timestamps before processing',
                        'data': pre_times,
                        'timestamp': int(time.time() * 1000)
                    }) + '\n')
            except Exception as e:
                pass
            
            # #region agent log
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'upload-backend',
                        'hypothesisId': 'K',
                        'location': 'app.py:327',
                        'message': 'Starting processing pipeline',
                        'data': {'projectRoot': project_root, 'currentDir': os.getcwd()},
                        'timestamp': int(__import__('time').time() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            
            run_processing_pipeline(filepath)
            
            # DEBUG: Check file timestamps after processing
            try:
                post_times = {}
                for f in debug_files:
                    if os.path.exists(f):
                        post_times[f] = os.path.getmtime(f)
                
                with open(log_path, 'a') as logf:
                    logf.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'upload-backend',
                        'hypothesisId': 'TIMESTAMP_POST',
                        'message': 'File timestamps after processing',
                        'data': post_times,
                        'timestamp': int(time.time() * 1000)
                    }) + '\n')
            except Exception as e:
                pass

            # #region agent log
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'upload-backend',
                        'hypothesisId': 'L',
                        'location': 'app.py:335',
                        'message': 'Processing pipeline completed',
                        'data': {},
                        'timestamp': int(__import__('time').time() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            # After pipeline finishes, we remain in project_root for signal detection
            # because detect_signals needs to find clusters.npy which was just created there
            
            try:
                # Add src to path if needed (it is already added at top of file, but let's be safe)
                if 'src' not in sys.path:
                    sys.path.append(os.path.join(os.getcwd(), 'src'))
                    
                signals_df, df_clustered = detect_signals()
                summaries = generate_cluster_summaries(signals_df, df_clustered, top_n=5)
            except Exception as signal_error:
                # #region agent log
                try:
                    with open(log_path, 'a') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'upload-backend',
                            'hypothesisId': 'N',
                            'location': 'app.py:signal-error',
                            'message': 'Signal detection error',
                            'data': {'error': str(signal_error), 'errorType': type(signal_error).__name__},
                            'timestamp': int(__import__('time').time() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                # Don't forget to reset CWD even if this fails
                os.chdir(original_dir)
                return jsonify({
                    'success': False,
                    'error': f'Signal detection failed: {str(signal_error)}'
                }), 500
                
            # If everything succeeded, reset CWD
            os.chdir(original_dir)
            
            # Convert summaries to JSON-serializable format
            signals_json = []
            for summary in summaries:
                signals_json.append({
                    'cluster': int(summary['cluster']),
                    'frequency': int(summary['frequency']),
                    'severity': float(summary['severity']),
                    'growth_rate': float(summary['growth_rate']),
                    'signal_score': float(summary['signal_score']),
                    'top_adverse_events': summary['top_adverse_events'],
                    'summary': summary['summary']
                })
            
            return jsonify({
                'success': True,
                'message': 'File uploaded and processed successfully',
                'signals': signals_json
            }), 200

        except Exception as pipeline_error:
            # #region agent log
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'upload-backend',
                        'hypothesisId': 'M',
                        'location': 'app.py:pipeline-error',
                        'message': 'Processing pipeline error',
                        'data': {'error': str(pipeline_error), 'errorType': type(pipeline_error).__name__},
                        'timestamp': int(__import__('time').time() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            os.chdir(original_dir)
            return jsonify({
                'success': False,
                'error': f'Processing pipeline failed: {str(pipeline_error)}'
            }), 500
        
        # Convert summaries to JSON-serializable format
        signals_json = []
        for summary in summaries:
            signals_json.append({
                'cluster': int(summary['cluster']),
                'frequency': int(summary['frequency']),
                'severity': float(summary['severity']),
                'growth_rate': float(summary['growth_rate']),
                'signal_score': float(summary['signal_score']),
                'top_adverse_events': summary['top_adverse_events'],
                'summary': summary['summary']
            })
        
        return jsonify({
            'success': True,
            'message': 'File uploaded and processed successfully',
            'signals': signals_json
        }), 200
        
    except subprocess.CalledProcessError as e:
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'upload-backend',
                    'hypothesisId': 'H',
                    'location': 'app.py:subprocess-error',
                    'message': 'Subprocess error',
                    'data': {'error': str(e), 'errorType': type(e).__name__},
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        return jsonify({
            'success': False,
            'error': f'Processing pipeline failed: {str(e)}'
        }), 500
    except Exception as e:
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'upload-backend',
                    'hypothesisId': 'I',
                    'location': 'app.py:exception',
                    'message': 'General exception',
                    'data': {'error': str(e), 'errorType': type(e).__name__, 'traceback': str(__import__('traceback').format_exc())[:500]},
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        return jsonify({
            'success': False,
            'error': f'Error uploading file: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        JSON response with status information
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Pharmacovigilance Signal Detection API',
        'version': '1.0.0'
    }), 200


@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Get processing status endpoint (alias for health check).
    Frontend calls this endpoint.
    
    Returns:
        JSON response with status information
    """
    return jsonify({
        'message': 'Ready',
        'type': 'info',
        'processing': False
    }), 200


@app.route('/api/data/cleaned', methods=['GET'])
def get_cleaned_data():
    """
    Get cleaned AE data with pagination and search.
    
    Query Parameters:
        - page: Page number (default: 1)
        - limit: Items per page (default: 100)
        - search: Search query (optional)
    
    Returns:
        JSON response with cleaned data
    """
    try:
        csv_path = os.path.join(DATA_FOLDER, 'sample_ae.csv')
        
        # #region agent log
        import json
        log_path = '/Users/prasannaa/Desktop/pharmacovigilance-agent/.cursor/debug.log'
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'get-cleaned-data',
                    'hypothesisId': 'READ',
                    'location': 'app.py:get_cleaned_data',
                    'message': 'Attempting to read CSV',
                    'data': {
                        'csv_path': csv_path, 
                        'exists': os.path.exists(csv_path),
                        'params': request.args
                    },
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion

        if not os.path.exists(csv_path):
            return jsonify({'data': [], 'total': 0, 'page': 1, 'limit': 100}), 200
        
        # Use robust reader
        df = read_csv_robust(csv_path)
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'get-cleaned-data',
                    'hypothesisId': 'LOAD',
                    'location': 'app.py:get_cleaned_data',
                    'message': 'Loaded CSV',
                    'data': {
                        'shape': list(df.shape),
                        'columns': df.columns.tolist()
                    },
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Apply search filter if provided
        search = request.args.get('search', '').lower()
        if search:
            # Search across all string columns
            mask = df.astype(str).apply(
                lambda x: x.str.lower().str.contains(search, na=False)
            ).any(axis=1)
            df = df[mask]
        
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        total = len(df)
        paginated_df = df.iloc[start_idx:end_idx].copy()
        
        
        # Replace NaN with None for valid JSON serialization
        # df.where(pd.notnull(df), None) fails to catch all NaN types in some pandas versions or mixed types
        # Explicit replace is safer
        paginated_df = paginated_df.replace({np.nan: None})
        
        result = {
            'data': paginated_df.to_dict('records'),
            'total': total,
            'page': page,
            'limit': limit
        }

        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'get-cleaned-data',
                    'hypothesisId': 'RET',
                    'location': 'app.py:get_cleaned_data',
                    'message': 'Returning data',
                    'data': {
                        'total': total,
                        'returned_count': len(result['data'])
                    },
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    """
    Get all cluster data.
    
    Returns:
        JSON response with cluster data
    """
    try:
        csv_path = os.path.join(PROJECT_ROOT, 'top_signals.csv')
        
        # #region agent log
        try:
            with open(os.path.join(app.config['UPLOAD_FOLDER'], '..', '.cursor', 'debug.log'), 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'get_clusters',
                    'message': 'Endpoint called',
                    'data': {'csv_path': csv_path, 'exists': os.path.exists(csv_path)},
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion

        if not os.path.exists(csv_path):
            return jsonify({'clusters': []}), 200
        
        df = pd.read_csv(csv_path)
        # Replace NaN with None for valid JSON serialization
        df = df.where(pd.notnull(df), None)
        clusters = df.to_dict('records')
        
        return jsonify({'clusters': clusters})
    except Exception as e:
        # #region agent log
        try:
            with open(os.path.join(app.config['UPLOAD_FOLDER'], '..', '.cursor', 'debug.log'), 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'get_clusters',
                    'message': 'Error',
                    'data': {'error': str(e)},
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        return jsonify({'error': str(e)}), 500


@app.route('/api/signals/top', methods=['GET'])
def get_top_signals():
    """
    Get top N signals by signal score.
    
    Query Parameters:
        - top_n: Number of top signals (default: 5)
    
    Returns:
        JSON response with top signals
    """
    try:
        top_n = int(request.args.get('top_n', 5))
        csv_path = os.path.join(PROJECT_ROOT, 'top_signals.csv')
        
        if not os.path.exists(csv_path):
            return jsonify({'signals': []}), 200
        
        df = pd.read_csv(csv_path)
        df = df.sort_values('signal_score', ascending=False)
        # Replace NaN with None for valid JSON serialization
        df = df.where(pd.notnull(df), None)
        top_signals = df.head(top_n).to_dict('records')
        
        return jsonify({'signals': top_signals})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/signals/summaries', methods=['GET'])
def get_cluster_summaries():
    """
    Get LLM-generated cluster summaries.
    This endpoint uses the same logic as /api/signals but returns summaries format.
    
    Query Parameters:
        - top_n: Number of top clusters to summarize (default: 5)
    
    Returns:
        JSON response with cluster summaries
    """
    try:
        top_n = int(request.args.get('top_n', 5))
        
        top_n = int(request.args.get('top_n', 5))
        
        # Check if required files exist
        clusters_path = os.path.join(PROJECT_ROOT, 'clusters.npy')
        if not os.path.exists(clusters_path):
            return jsonify({
                'success': False,
                'error': 'Clusters not found. Please upload and process a dataset first.'
            }), 404
        
        csv_path = os.path.join(DATA_FOLDER, 'sample_ae.csv')
        if not os.path.exists(csv_path):
            return jsonify({
                'success': False,
                'error': 'Dataset not found. Please upload a CSV file first.'
            }), 404
        
        # Detect signals and get cluster statistics
        original_dir = os.getcwd()
        try:
            os.chdir(PROJECT_ROOT)
            if 'src' not in sys.path:
                sys.path.append(os.path.join(PROJECT_ROOT, 'src'))
                
            signals_df, df_clustered = detect_signals()
            
            # Generate human-readable summaries
            summaries = generate_cluster_summaries(signals_df, df_clustered, top_n=top_n)
        finally:
            os.chdir(original_dir)
        
        return jsonify({'summaries': summaries})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Get evaluation metrics for clustering and signal detection.
    
    Returns:
        JSON response with metrics
    """
    try:
        metrics_path = os.path.join(PROJECT_ROOT, 'metrics.json')
        
        if not os.path.exists(metrics_path):
            return jsonify({'metrics': None}), 200
            
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
            
        return jsonify({'metrics': metrics})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clusters/search', methods=['GET'])
def search_clusters():
    """
    Search clusters by drug name or adverse event.
    
    Query Parameters:
        - query: Search query
        - type: 'drug' or 'adverse_event' (default: 'adverse_event')
    
    Returns:
        JSON response with filtered clusters
    """
    try:
        query = request.args.get('query', '').lower()
        search_type = request.args.get('type', 'adverse_event')
        
        if not query:
            return jsonify({'clusters': []}), 200
        
        # Load cleaned data with clusters
        csv_path = os.path.join(DATA_FOLDER, 'sample_ae.csv')
        if not os.path.exists(csv_path):
            return jsonify({'clusters': []}), 200
        
        if not os.path.exists(csv_path):
            return jsonify({'clusters': []}), 200
        
        # Use robust reader
        df = read_csv_robust(csv_path)
        
        # Load cluster labels
        clusters_path = os.path.join(PROJECT_ROOT, 'clusters.npy')
        cluster_labels = np.load(clusters_path)
        if len(cluster_labels) > len(df):
            cluster_labels = cluster_labels[:len(df)]
        
        df['cluster'] = cluster_labels
        
        # Filter based on search type
        if search_type == 'drug':
            if 'DRUG' in df.columns:
                mask = df['DRUG'].astype(str).str.lower().str.contains(query, na=False)
            else:
                # Fallback: search in all columns if specific column not found
                mask = df.astype(str).apply(lambda x: x.str.lower().str.contains(query, na=False)).any(axis=1)
        elif search_type == 'adverse_event':
            if 'Adverse_Event' in df.columns:
                mask = df['Adverse_Event'].astype(str).str.lower().str.contains(query, na=False)
            elif 'reaction' in df.columns:
                mask = df['reaction'].astype(str).str.lower().str.contains(query, na=False)
            else:
                # Fallback: search in all columns
                mask = df.astype(str).apply(lambda x: x.str.lower().str.contains(query, na=False)).any(axis=1)
        else:
            return jsonify({'clusters': []}), 200
        
        filtered_df = df[mask]
        
        # Get cluster statistics
        cluster_stats = []
        for cluster_id in filtered_df['cluster'].unique():
            if cluster_id == -1:  # Skip noise points
                continue
            
            cluster_data = filtered_df[filtered_df['cluster'] == cluster_id]
            cluster_stats.append({
                'cluster': int(cluster_id),
                'frequency': len(cluster_data),
                'severity': 1.0,  # Default, would need actual severity data
                'growth_rate': 1.0,  # Default
                'signal_score': len(cluster_data) * 1.0 * 1.0
            })
        
        # No need to sanitize cluster_stats as it is manually constructed
        return jsonify({'clusters': cluster_stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Ensure data directory exists before starting
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    print("=" * 60)
    print("Pharmacovigilance Signal Detection API")
    print("=" * 60)
    print(f"Starting Flask server on port {PORT}...")
    print(f"API will be available at http://localhost:{PORT}")
    print(f"Endpoints:")
    print(f"  - GET  /api/signals - Get top 5 safety signals")
    print(f"  - POST /api/upload  - Upload CSV and process")
    print(f"  - GET  /api/health  - Health check")
    print("=" * 60)
    
    # Run Flask application
    # debug=True enables debug mode with auto-reload
    # host='0.0.0.0' allows connections from any network interface
    app.run(debug=True, port=PORT, host='0.0.0.0')
