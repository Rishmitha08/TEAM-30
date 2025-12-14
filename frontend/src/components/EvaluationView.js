import React, { useState, useEffect } from 'react';
import { getMetrics, getTopSignals } from '../services/api';

function EvaluationView({ uploadDone }) {
    const [metrics, setMetrics] = useState(null);
    const [topSignals, setTopSignals] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchData();
    }, [uploadDone]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [metricsRes, signalsRes] = await Promise.all([
                getMetrics(),
                getTopSignals(5)
            ]);
            setMetrics(metricsRes.data.metrics);
            setTopSignals(signalsRes.data.signals || []);
        } catch (err) {
            console.error('Error fetching evaluation data:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!metrics) {
        return (
            <div className="text-center py-12">
                <h3 className="text-sm font-medium text-gray-900">No Metrics Available</h3>
                <p className="mt-1 text-sm text-gray-500">Upload and process a dataset first.</p>
            </div>
        );
    }

    // Helper for Cluster Score Bar Color
    const getScoreColor = (score) => {
        if (score > 0.5) return 'bg-green-500';
        if (score > 0.2) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    // Helper for Signal Detection Chart (Donut)
    const highPriorityCount = metrics.high_priority_signals || 0;
    const totalSignals = metrics.total_signals || 1; // avoid divide by zero
    const highPriorityPercent = Math.round((highPriorityCount / totalSignals) * 100);

    return (
        <div className="space-y-6">
            <div className="bg-white rounded-lg shadow px-6 py-5">
                <h2 className="text-xl font-semibold text-gray-900">Evaluation Dashboard</h2>
                <p className="text-sm text-gray-500 mt-1">Comprehensive analysis of pharmacovigilance metrics</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* 1. Cluster Metric (Silhouette Score) */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-gray-900">Clustering Quality</h3>
                        <span className="text-2xl">🔷</span>
                    </div>

                    <div className="space-y-4">
                        <div className="flex justify-between items-end">
                            <span className="text-sm text-gray-600">Silhouette Score</span>
                            <span className="text-2xl font-bold text-gray-900">
                                {metrics.silhouette_score ? metrics.silhouette_score.toFixed(3) : 'N/A'}
                            </span>
                        </div>

                        {/* Visual Range Indicator -1 to 1 */}
                        <div className="relative pt-1">
                            <div className="flex mb-2 items-center justify-between text-xs text-gray-400">
                                <span>-1.0</span>
                                <span>0.0</span>
                                <span>1.0</span>
                            </div>
                            <div className="overflow-hidden h-4 text-xs flex rounded bg-gray-200 relative">
                                {/* Center marker */}
                                <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-gray-400 opacity-50"></div>

                                {/* The score bar */}
                                {metrics.silhouette_score !== undefined && (
                                    <div
                                        style={{
                                            width: `${((metrics.silhouette_score + 1) / 2) * 100}%`,
                                            transition: 'width 1s ease-in-out'
                                        }}
                                        className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${getScoreColor(metrics.silhouette_score)}`}
                                    ></div>
                                )}
                            </div>
                            <p className="text-xs text-gray-500 mt-2 text-right">
                                {metrics.silhouette_score > 0.5 ? 'Good structure' :
                                    metrics.silhouette_score > 0.2 ? 'Weak structure' : 'No significant structure'}
                            </p>
                        </div>

                        <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-2 gap-4 text-center">
                            <div>
                                <span className="block text-xl font-semibold text-gray-700">{metrics.n_clusters}</span>
                                <span className="text-xs text-gray-500">Total Clusters</span>
                            </div>
                            <div>
                                <span className="block text-xl font-semibold text-gray-700">{metrics.n_noise || 0}</span>
                                <span className="text-xs text-gray-500">Noise Points</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 2. Signal Detection Metric (High Priority vs Total) */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-gray-900">Signal Detection</h3>
                        <span className="text-2xl">🔴</span>
                    </div>

                    <div className="flex items-center justify-around">
                        {/* CSS Donut Chart */}
                        <div className="relative w-32 h-32 rounded-full"
                            style={{
                                background: `conic-gradient(#ef4444 ${highPriorityPercent}%, #e5e7eb ${highPriorityPercent}% 100%)`
                            }}>
                            <div className="absolute top-0 left-0 w-full h-full rounded-full flex items-center justify-center">
                                <div className="w-24 h-24 bg-white rounded-full flex flex-col items-center justify-center">
                                    <span className="text-xl font-bold text-gray-900">{highPriorityPercent}%</span>
                                    <span className="text-xs text-gray-500">High Risk</span>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-3">
                            <div>
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                                    <span className="text-sm font-medium text-gray-700">High Priority</span>
                                </div>
                                <span className="block text-2xl font-bold ml-5">{highPriorityCount}</span>
                            </div>
                            <div>
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-gray-200"></div>
                                    <span className="text-sm font-medium text-gray-700">Other Signals</span>
                                </div>
                                <span className="block text-2xl font-bold ml-5 text-gray-500">{totalSignals - highPriorityCount}</span>
                            </div>
                        </div>
                    </div>

                    <div className="mt-4 text-sm text-gray-500 text-center">
                        Total {totalSignals} signals detected across all clusters
                    </div>
                </div>

                {/* 3. Severity Ranking Metric (Leaderboard) */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-gray-900">Top 5 Severity Ranking</h3>
                        <span className="text-2xl">⚠️</span>
                    </div>

                    <div className="space-y-3">
                        {topSignals.length > 0 ? (
                            topSignals.map((signal, idx) => (
                                <div key={idx} className="relative">
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="font-medium text-gray-700">Cluster {signal.cluster}</span>
                                        <span className="text-gray-900 font-bold">{signal.signal_score.toFixed(1)}</span>
                                    </div>
                                    <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-100">
                                        <div
                                            style={{ width: `${Math.min((signal.signal_score / (metrics.max_signal_score || 100)) * 100, 100)}%` }}
                                            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-purple-600"
                                        ></div>
                                    </div>
                                    <div className="flex justify-between text-xs text-gray-400 mt-0.5">
                                        <span>Freq: {signal.frequency}</span>
                                        <span>Sev: {signal.severity.toFixed(1)}</span>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p className="text-center text-gray-500 py-4">No signal data available</p>
                        )}
                    </div>
                </div>

                {/* 4. LLM Output Metric */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-gray-900">AI Summary Generation</h3>
                        <span className="text-2xl">🤖</span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 h-full">
                        <div className="bg-green-50 rounded-lg p-4 flex flex-col justify-center text-center border border-green-100">
                            <span className="text-green-600 font-medium mb-1">Coverage</span>
                            <span className="text-3xl font-bold text-green-700">
                                {Math.min(topSignals.length, 5)} / 5
                            </span>
                            <span className="text-xs text-green-600 mt-1">Top Clusters Summarized</span>
                        </div>

                        <div className="flex flex-col justify-around py-2">
                            <div className="flex items-start gap-2">
                                <span className="text-green-500 mt-1">✓</span>
                                <div>
                                    <p className="text-sm font-medium text-gray-800">Risk Assessment</p>
                                    <p className="text-xs text-gray-500">Automated severity analysis</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-2">
                                <span className="text-green-500 mt-1">✓</span>
                                <div>
                                    <p className="text-sm font-medium text-gray-800">Trend Analysis</p>
                                    <p className="text-xs text-gray-500">Growth rate evaluation</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-2">
                                <span className="text-green-500 mt-1">✓</span>
                                <div>
                                    <p className="text-sm font-medium text-gray-800">Recommendations</p>
                                    <p className="text-xs text-gray-500">Actionable insights generated</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Classification Metrics - Only if available */}
            {metrics.accuracy !== undefined && (
                <div className="bg-white rounded-lg shadow p-6 mt-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Classification Performance</h3>
                    <div className="grid grid-cols-4 gap-4 text-center">
                        <div>
                            <span className="block text-2xl font-bold text-green-600">{(metrics.accuracy * 100).toFixed(1)}%</span>
                            <span className="text-xs text-gray-500">Accuracy</span>
                        </div>
                        <div>
                            <span className="block text-2xl font-bold text-blue-600">{(metrics.precision * 100).toFixed(1)}%</span>
                            <span className="text-xs text-gray-500">Precision</span>
                        </div>
                        <div>
                            <span className="block text-2xl font-bold text-yellow-600">{(metrics.recall * 100).toFixed(1)}%</span>
                            <span className="text-xs text-gray-500">Recall</span>
                        </div>
                        <div>
                            <span className="block text-2xl font-bold text-purple-600">{metrics.f1_score?.toFixed(3) || 'N/A'}</span>
                            <span className="text-xs text-gray-500">F1 Score</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default EvaluationView;
