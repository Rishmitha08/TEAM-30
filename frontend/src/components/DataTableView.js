import React, { useState, useEffect, useCallback } from 'react';
import { getCleanedData } from '../services/api';

function DataTableView({ uploadDone }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [debugInfo, setDebugInfo] = useState('Init');
  const limit = 50;

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getCleanedData(page, limit, search);
      console.log('API Response:', response);

      let rawData = response.data;
      let parseError = null;

      // If data is a string, try to parse it
      if (typeof rawData === 'string') {
        try {
          rawData = JSON.parse(rawData);
        } catch (e) {
          // If parsing fails, it might be due to NaN (which is invalid JSON but common in Python serialization)
          // Try to sanitize NaN values to null
          console.warn('JSON parse failed, attempting to sanitize NaNs...');
          try {
            const sanitized = rawData.replace(/:\s*NaN/g, ': null');
            rawData = JSON.parse(sanitized);
            parseError = null; // Clear error if sanitation worked
          } catch (e2) {
            console.error('Failed to parse response data string after sanitation:', e2);
            parseError = e.message;
          }
        }
      }

      let tableData = [];
      let totalCount = 0;

      // Handle different response structures
      if (Array.isArray(rawData)) {
        // Case: Raw data is array
        tableData = rawData;
        totalCount = response.total || rawData.length;
      } else if (rawData && Array.isArray(rawData.data)) {
        // Case: Standard structure
        tableData = rawData.data;
        totalCount = rawData.total || tableData.length;
      } else if (rawData && typeof rawData === 'object') {
        // Case: Object with numeric keys
        const keys = Object.keys(rawData);
        if (keys.length > 0 && keys.every(k => !isNaN(parseInt(k)))) {
          tableData = Object.values(rawData);
          totalCount = tableData.length;
        } else if (rawData.data && typeof rawData.data === 'object') {
          tableData = Object.values(rawData.data);
          totalCount = tableData.length;
        }
      }

      const rawSnippet = (typeof response.data === 'string') ? response.data.substring(0, 50).replace(/\n/g, ' ') : 'N/A';
      setDebugInfo(`Type: ${typeof response.data}, Parsed(${parseError || 'OK'}), Snippet: "${rawSnippet}", DataLen: ${tableData.length}`);
      setData(tableData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load data. Please try again.');
      // Use mock data for demonstration
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [page, limit, search]);

  useEffect(() => {
    // Fetch data on mount and when upload is done
    fetchData();
  }, [fetchData, uploadDone]);

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });

    // Sort data
    const sortedData = [...data].sort((a, b) => {
      if (a[key] < b[key]) return direction === 'asc' ? -1 : 1;
      if (a[key] > b[key]) return direction === 'asc' ? 1 : -1;
      return 0;
    });
    setData(sortedData);
  };

  // Dynamic columns based on data
  const [columns, setColumns] = useState([]);

  useEffect(() => {
    if (data.length > 0) {
      const cols = Object.keys(data[0]).map(key => ({
        key: key,
        label: key.replace(/_/g, ' ').toUpperCase()
      }));
      setColumns(cols);
    }
  }, [data]);

  // No early return based on uploadDone. 
  // We rely on data.length === 0 to show empty state.

  if (loading && data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            Cleaned Adverse Event Data
          </h2>
          <div className="flex items-center space-x-4">
            <input
              type="text"
              placeholder="Search..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border-l-4 border-red-400">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => handleSort(col.key)}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    {col.label}
                    {sortConfig.key === col.key && (
                      <svg
                        className={`ml-1 h-4 w-4 ${sortConfig.direction === 'asc' ? '' : 'transform rotate-180'
                          }`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M5 12a1 1 0 102 0V6.414l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L5 6.414V12zM15 8a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L15 13.586V8z" />
                      </svg>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-8 text-center text-gray-500">
                  No data available. Please upload a dataset.
                  <br />
                  <span className="text-xs text-gray-400">
                    Debug: {debugInfo}
                    <br />
                    Loaded: {String(loading)}, Len: {data?.length}, Err: {String(error)}
                  </span>
                </td>
              </tr>
            ) : (
              data.map((row, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  {columns.map((col) => (
                    <td key={col.key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {row[col.key] || '-'}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <p className="mt-1 text-sm text-gray-500">
          {data.length > 0 ? (
            <span>
              Showing <span className="font-medium">{(page - 1) * limit + 1}</span> to{' '}
              <span className="font-medium">{(page - 1) * limit + data.length}</span> of{' '}
              <span className="font-medium">{debugInfo.match(/Total: (\d+)/)?.[1] || data.length}</span> results
            </span>
          ) : (
            'Please upload a dataset to view results.'
          )}
          <br />
          <span className="text-xs text-gray-400">
            Debug: {debugInfo} | Len: {data?.length}
          </span>
        </p>
        <div className="flex space-x-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Previous
          </button>
          <button
            onClick={() => setPage(page + 1)}
            disabled={data.length < limit}
            className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

export default DataTableView;

