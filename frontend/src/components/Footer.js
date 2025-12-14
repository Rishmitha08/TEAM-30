import React from 'react';

function Footer({ status, processing }) {
  const getStatusColor = () => {
    switch (status.type) {
      case 'success':
        return 'bg-green-100 text-green-800 border-green-400';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-400';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-400';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-400';
    }
  };

  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`px-4 py-2 rounded-lg border-l-4 ${getStatusColor()}`}>
              <div className="flex items-center space-x-2">
                {processing && (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                )}
                <span className="text-sm font-medium">{status.message}</span>
              </div>
            </div>
          </div>
          <div className="text-sm text-gray-500">
            Pharmacovigilance Signal Detection System v1.0
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;

