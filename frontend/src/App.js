import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import DataTableView from './components/DataTableView';
import EvaluationView from './components/EvaluationView';
import ClustersView from './components/ClustersView';
import SummariesView from './components/SummariesView';
import Footer from './components/Footer';
import { getProcessingStatus } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('data');
  const [status, setStatus] = useState({ message: 'Ready', type: 'info' });
  const [processing, setProcessing] = useState(false);
  const [uploadVersion, setUploadVersion] = useState(0); // Track uploads with a version counter to force updates

  useEffect(() => {
    // Check processing status on mount
    checkStatus();
    // Poll status every 5 seconds if processing
    const interval = setInterval(() => {
      if (processing) {
        checkStatus();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [processing]);

  const checkStatus = async () => {
    try {
      const response = await getProcessingStatus();
      setStatus({
        message: response.data.message || 'Ready',
        type: response.data.type || 'info',
      });
      setProcessing(response.data.processing || false);
    } catch (error) {
      console.error('Error checking status:', error);
    }
  };

  const handleStatusUpdate = (message, type = 'info', isProcessing = false) => {
    setStatus({ message, type });
    setProcessing(isProcessing);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          onStatusUpdate={handleStatusUpdate}
          processing={processing}
          onUploadSuccess={() => setUploadVersion(prev => prev + 1)}
        />

        <main className="flex-1 overflow-y-auto p-6">
          {/* Tab Navigation */}
          <div className="mb-6 border-b border-gray-200">
            <nav className="flex space-x-8">
              <button
                onClick={() => setActiveTab('data')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'data'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                Data Table
              </button>
              <button
                onClick={() => setActiveTab('clusters')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'clusters'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                Clusters
              </button>
              <button
                onClick={() => setActiveTab('summaries')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'summaries'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                Cluster Summaries
              </button>
              <button
                onClick={() => setActiveTab('evaluation')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'evaluation'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                Evaluation
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="mt-6">
            {activeTab === 'data' && <DataTableView uploadDone={uploadVersion > 0} key={uploadVersion} />}
            {activeTab === 'clusters' && <ClustersView uploadDone={uploadVersion > 0} key={`clusters-${uploadVersion}`} />}
            {activeTab === 'summaries' && <SummariesView uploadDone={uploadVersion > 0} key={`summaries-${uploadVersion}`} />}
            {activeTab === 'evaluation' && <EvaluationView uploadDone={uploadVersion > 0} key={`eval-${uploadVersion}`} />}
          </div>
        </main>
      </div>

      <Footer status={status} processing={processing} />
    </div>
  );
}

export default App;

