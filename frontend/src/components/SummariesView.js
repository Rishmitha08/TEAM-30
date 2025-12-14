import React, { useState, useEffect } from 'react';
import { getClusterSummaries } from '../services/api';

function SummariesView({ uploadDone }) {
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedCluster, setExpandedCluster] = useState(null);

  useEffect(() => {
    // Fetch data on mount and when upload is done
    fetchSummaries();
  }, [uploadDone]);

  const fetchSummaries = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getClusterSummaries(5);
      setSummaries(response.data.summaries || []);
    } catch (err) {
      console.error('Error fetching summaries:', err);
      setError('Failed to load cluster summaries. Please try again.');
      // Use mock data for demonstration
      setSummaries([]);
    } finally {
      setLoading(false);
    }
  };

  const getSignalScoreColor = (score) => {
    if (score > 50) return 'border-red-500 bg-red-50';
    if (score > 20) return 'border-orange-400 bg-orange-50';
    return 'border-blue-300 bg-blue-50';
  };

  const getPriorityBadge = (score, index) => {
    if (score > 50) return 'HIGH PRIORITY';
    if (score > 20) return 'MEDIUM PRIORITY';
    return 'LOW PRIORITY';
  };

  // No early return based on uploadDone.
  // We rely on summaries.length === 0 to show empty state.

  if (loading && summaries.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          LLM-Generated Cluster Summaries
        </h2>
        <p className="text-sm text-gray-500">
          Human-readable safety signal summaries generated using AI analysis
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {summaries.length === 0 && !loading ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No summaries available</h3>
          <p className="mt-1 text-sm text-gray-500">
            Please process a dataset to generate cluster summaries.
          </p>
        </div>
      ) : (
        summaries.map((summary, index) => (
          <div
            key={summary.cluster}
            className={`bg-white rounded-lg shadow border-l-4 ${getSignalScoreColor(summary.signal_score)}`}
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-bold text-gray-900">
                      Cluster {summary.cluster}
                    </h3>
                    <span className="px-3 py-1 text-xs font-semibold bg-blue-600 text-white rounded-full">
                      {getPriorityBadge(summary.signal_score, index)}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() =>
                    setExpandedCluster(
                      expandedCluster === summary.cluster ? null : summary.cluster
                    )
                  }
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg
                    className={`h-5 w-5 transform transition-transform ${expandedCluster === summary.cluster ? 'rotate-180' : ''
                      }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>
              </div>

              {/* Summary Text */}
              <div className="prose max-w-none mb-4">
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {summary.summary}
                </p>
              </div>

              {/* Key Metrics */}
              {expandedCluster === summary.cluster && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h4 className="text-sm font-semibold text-gray-900 mb-3">
                    Key Metrics
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-xs text-gray-500 mb-1">Reports</div>
                      <div className="text-lg font-semibold text-gray-900">
                        {summary.frequency}
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-xs text-gray-500 mb-1">Severity</div>
                      <div className="text-lg font-semibold text-gray-900">
                        {summary.severity?.toFixed(2)}
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-xs text-gray-500 mb-1">Growth Rate</div>
                      <div className="text-lg font-semibold text-gray-900">
                        {summary.growth_rate?.toFixed(2)}x
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-xs text-gray-500 mb-1">Signal Score</div>
                      <div className="text-lg font-semibold text-gray-900">
                        {summary.signal_score?.toFixed(2)}
                      </div>
                    </div>
                  </div>

                  {summary.top_adverse_events && summary.top_adverse_events.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-semibold text-gray-900 mb-2">
                        Top Adverse Events
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {summary.top_adverse_events.map((event, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                          >
                            {event}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default SummariesView;

