import React, { useState } from 'react';
import { uploadDataset } from '../services/api';

function Sidebar({ onStatusUpdate, processing, onUploadSuccess }) {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    // #region agent log
    const logEntry = {
      sessionId: 'debug-session',
      runId: 'upload-attempt',
      hypothesisId: 'A',
      location: 'Sidebar.js:33',
      message: 'File upload started',
      data: { fileName: file.name, fileSize: file.size, fileType: file.type },
      timestamp: Date.now()
    };
    fetch('http://127.0.0.1:7242/ingest/db8cbf8d-cd75-46b1-9434-b4f5cd7bfb2e', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(logEntry)
    }).catch(() => { });
    // #endregion

    if (!file.name.endsWith('.csv')) {
      onStatusUpdate('Please upload a CSV file', 'error');
      return;
    }

    onStatusUpdate('Uploading and processing dataset...', 'info', true);

    try {
      // #region agent log
      const logBefore = {
        sessionId: 'debug-session',
        runId: 'upload-attempt',
        hypothesisId: 'B',
        location: 'Sidebar.js:42',
        message: 'Before API call',
        data: { apiBaseUrl: 'http://localhost:5001/api', endpoint: '/upload' },
        timestamp: Date.now()
      };
      fetch('http://127.0.0.1:7242/ingest/db8cbf8d-cd75-46b1-9434-b4f5cd7bfb2e', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logBefore)
      }).catch(() => { });
      // #endregion

      const response = await uploadDataset(file);

      // #region agent log
      const logAfter = {
        sessionId: 'debug-session',
        runId: 'upload-attempt',
        hypothesisId: 'C',
        location: 'Sidebar.js:45',
        message: 'After API call - success',
        data: {
          status: response.status,
          success: response.data?.success,
          hasData: !!response.data,
          error: response.data?.error
        },
        timestamp: Date.now()
      };
      fetch('http://127.0.0.1:7242/ingest/db8cbf8d-cd75-46b1-9434-b4f5cd7bfb2e', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logAfter)
      }).catch(() => { });
      // #endregion

      if (response.data.success) {
        onStatusUpdate('Processing complete!', 'success', false);
        // Notify parent that upload was successful - this triggers data fetching
        if (onUploadSuccess) {
          onUploadSuccess();
        }
      } else {
        onStatusUpdate(response.data.message || 'Upload failed', 'error', false);
      }
    } catch (error) {
      // #region agent log
      const logError = {
        sessionId: 'debug-session',
        runId: 'upload-attempt',
        hypothesisId: 'D',
        location: 'Sidebar.js:53',
        message: 'Upload error caught',
        data: {
          errorMessage: error.message,
          errorName: error.name,
          hasResponse: !!error.response,
          responseStatus: error.response?.status,
          responseData: error.response?.data,
          responseError: error.response?.data?.error,
          stack: error.stack?.substring(0, 200)
        },
        timestamp: Date.now()
      };
      fetch('http://127.0.0.1:7242/ingest/db8cbf8d-cd75-46b1-9434-b4f5cd7bfb2e', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logError)
      }).catch(() => { });
      // #endregion

      console.error('Upload error:', error);
      onStatusUpdate(
        error.response?.data?.message || error.message || 'Error uploading file. Please try again.',
        'error',
        false
      );
    }
  };

  return (
    <aside className="w-64 bg-white shadow-sm border-r border-gray-200 p-6">
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Dataset Upload
          </h2>

          <div
            className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${dragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
              } ${processing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => !processing && document.getElementById('file-input')?.click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".csv"
              className="hidden"
              onChange={handleFileInput}
              disabled={processing}
            />

            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>

            <p className="mt-2 text-sm text-gray-600">
              <span className="font-medium text-blue-600 hover:text-blue-500">
                Click to upload
              </span>{' '}
              or drag and drop
            </p>
            <p className="text-xs text-gray-500 mt-1">CSV file only</p>
          </div>

          {processing && (
            <div className="mt-4">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span className="ml-2 text-sm text-gray-600">Processing...</span>
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">
            Quick Actions
          </h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-center">
              <svg className="h-4 w-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Data Processing
            </li>
            <li className="flex items-center">
              <svg className="h-4 w-4 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Embedding Generation
            </li>
            <li className="flex items-center">
              <svg className="h-4 w-4 mr-2 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Cluster Analysis
            </li>
            <li className="flex items-center">
              <svg className="h-4 w-4 mr-2 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Signal Detection
            </li>
            <li className="flex items-center mt-4 pt-4 border-t border-gray-100">
              <button
                onClick={async () => {
                  if (window.confirm('Are you sure you want to delete all uploaded data and reset the application? This cannot be undone.')) {
                    try {
                      const { resetData } = require('../services/api');
                      onStatusUpdate('Resetting data...', 'info', true);
                      await resetData();
                      window.location.reload();
                    } catch (err) {
                      console.error('Reset failed:', err);
                      onStatusUpdate('Reset failed: ' + err.message, 'error');
                    }
                  }
                }}
                className="flex items-center text-red-600 hover:text-red-800 transition-colors w-full text-left"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Reset Data
              </button>
            </li>
          </ul>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;

