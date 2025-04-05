import React from 'react';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            {/* Logo and title */}
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
                  A
                </span>
              </div>
              <div className="ml-3 text-xl font-semibold text-gray-800">
                AudioTranscriptionFire
              </div>
            </div>
            
            {/* Navigation */}
            <nav className="flex items-center space-x-4">
              <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                Dashboard
              </a>
              <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                Incidents
              </a>
              <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                Verification
              </a>
              <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                Audio
              </a>
            </nav>
          </div>
        </div>
      </header>
      
      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-500">
            &copy; {new Date().getFullYear()} AudioTranscriptionFire - Emergency Response System
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MainLayout; 