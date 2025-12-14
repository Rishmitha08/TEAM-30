import React, { useState, useEffect, useMemo } from 'react';
import { getClusters, getTopSignals, searchClusters } from '../services/api';

function ClustersView({ uploadDone }) {
  const [clusters, setClusters] = useState([]);
  const [topSignals, setTopSignals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('adverse_event');
  const [sortBy, setSortBy] = useState('signal_score');
  const [sortDirection, setSortDirection] = useState('desc');

  useEffect(() => {
    // Fetch data on mount and when upload is done
    fetchData();
  }, [uploadDone]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [clustersRes, signalsRes] = await Promise.all([
        getClusters(),
        getTopSignals(5),
      ]);
      setClusters(clustersRes.data.clusters || []);
      setTopSignals(signalsRes.data.signals || []);
    } catch (err) {
      console.error('Error fetching clusters:', err);
      // Use mock data for demonstration
      setClusters([]);
      setTopSignals([]);
    } finally {
      setLoading(false);
    }
  };

  // Sort clusters based on sortBy and sortDirection
  const sortedClusters = useMemo(() => {
    if (!clusters.length) return clusters;

    const sorted = [...clusters].sort((a, b) => {
      let aVal = a[sortBy];
      let bVal = b[sortBy];

      // Handle numeric values
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }

      // Handle string values
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      return 0;
    });

    return sorted;
  }, [clusters, sortBy, sortDirection]);

  const handleSort = (column) => {
    if (sortBy === column) {
      // Toggle direction if same column
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New column, default to descending
      setSortBy(column);
      setSortDirection('desc');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchData();
      return;
    }

    setLoading(true);
    try {
      const response = await searchClusters(searchQuery, searchType);
      setClusters(response.data.clusters || []);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    if (severity >= 2.0) return 'bg-red-100 text-red-800';
    if (severity >= 1.5) return 'bg-orange-100 text-orange-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  const getGrowthRateColor = (rate) => {
    if (rate > 1.5) return 'text-red-600 font-semibold';
    if (rate > 1.0) return 'text-orange-600';
    return 'text-gray-600';
  };

  // No early return based on uploadDone.
  // We rely on clusters.length === 0 to show empty state.

  if (loading && clusters.length === 0 && topSignals.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Signals Section */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Top 5 Clusters by Signal Score
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Highest priority safety signals requiring immediate attention
          </p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {topSignals.map((signal, idx) => (
              <div
                key={signal.cluster}
                className={`p-4 rounded-lg border-2 ${idx === 0
                    ? 'border-red-500 bg-red-50'
                    : idx < 3
                      ? 'border-orange-400 bg-orange-50'
                      : 'border-blue-300 bg-blue-50'
                  }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-lg font-bold text-gray-900">
                    Cluster {signal.cluster}
                  </span>
                  {idx === 0 && (
                    <span className="px-2 py-1 text-xs font-semibold bg-red-600 text-white rounded">
                      HIGHEST PRIORITY
                    </span>
                  )}
                </div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Signal Score:</span>
                    <span className="font-semibold">{signal.signal_score?.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Frequency:</span>
                    <span>{signal.frequency} reports</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Severity:</span>
                    <span className={getSeverityColor(signal.severity)}>
                      {signal.severity?.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Growth Rate:</span>
                    <span className={getGrowthRateColor(signal.growth_rate)}>
                      {signal.growth_rate?.toFixed(2)}x
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* All Clusters Section */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                All Clusters
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                Complete cluster analysis with filtering and search
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={searchType}
                onChange={(e) => setSearchType(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="adverse_event">Adverse Event</option>
                <option value="drug">Drug Name</option>
              </select>
              <input
                type="text"
                placeholder="Search clusters..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleSearch}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Search
              </button>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  onClick={() => handleSort('cluster')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    Cluster ID
                    {sortBy === 'cluster' && (
                      <svg
                        className={`ml-1 h-4 w-4 ${sortDirection === 'asc' ? '' : 'transform rotate-180'
                          }`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M5 12a1 1 0 102 0V6.414l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L5 6.414V12zM15 8a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L15 13.586V8z" />
                      </svg>
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('frequency')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    Frequency
                    {sortBy === 'frequency' && (
                      <svg
                        className={`ml-1 h-4 w-4 ${sortDirection === 'asc' ? '' : 'transform rotate-180'
                          }`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M5 12a1 1 0 102 0V6.414l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L5 6.414V12zM15 8a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L15 13.586V8z" />
                      </svg>
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('severity')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    Severity
                    {sortBy === 'severity' && (
                      <svg
                        className={`ml-1 h-4 w-4 ${sortDirection === 'asc' ? '' : 'transform rotate-180'
                          }`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M5 12a1 1 0 102 0V6.414l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L5 6.414V12zM15 8a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L15 13.586V8z" />
                      </svg>
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('growth_rate')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    Growth Rate
                    {sortBy === 'growth_rate' && (
                      <svg
                        className={`ml-1 h-4 w-4 ${sortDirection === 'asc' ? '' : 'transform rotate-180'
                          }`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M5 12a1 1 0 102 0V6.414l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L5 6.414V12zM15 8a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L15 13.586V8z" />
                      </svg>
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('signal_score')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    Signal Score
                    {sortBy === 'signal_score' && (
                      <svg
                        className={`ml-1 h-4 w-4 ${sortDirection === 'asc' ? '' : 'transform rotate-180'
                          }`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M5 12a1 1 0 102 0V6.414l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L5 6.414V12zM15 8a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L15 13.586V8z" />
                      </svg>
                    )}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedClusters.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    No clusters found. Please process a dataset first.
                  </td>
                </tr>
              ) : (
                sortedClusters.map((cluster) => (
                  <tr key={cluster.cluster} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {cluster.cluster}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {cluster.frequency}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(cluster.severity)}`}>
                        {cluster.severity?.toFixed(2)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={getGrowthRateColor(cluster.growth_rate)}>
                        {cluster.growth_rate?.toFixed(2)}x
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                      {cluster.signal_score?.toFixed(2)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default ClustersView;

