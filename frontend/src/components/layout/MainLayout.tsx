'use client';

import React, { ReactNode } from 'react';
import Link from 'next/link';
import { useWebSocket, WebSocketStatus } from '@/services/websocket';

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const { status } = useWebSocket();

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="container mx-auto py-4 px-4 flex justify-between items-center">
          <div className="flex items-center gap-x-2">
            <Link href="/" className="text-lg font-bold text-blue-600 dark:text-blue-400">
              AudioTranscriptionFire
            </Link>
            
            {/* WebSocket Status Indicator */}
            <div className="ml-4 flex items-center">
              <div className={`w-2 h-2 rounded-full mr-2 ${
                status === WebSocketStatus.OPEN 
                  ? 'bg-green-500' 
                  : status === WebSocketStatus.CONNECTING 
                    ? 'bg-yellow-500 animate-pulse' 
                    : status === WebSocketStatus.ERROR 
                      ? 'bg-red-500' 
                      : 'bg-gray-500'
              }`}></div>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {status === WebSocketStatus.OPEN 
                  ? 'Connected' 
                  : status === WebSocketStatus.CONNECTING 
                    ? 'Connecting...' 
                    : status === WebSocketStatus.ERROR 
                      ? 'Connection Error' 
                      : 'Disconnected'}
              </span>
            </div>
          </div>
          
          <nav className="flex gap-x-4">
            <Link href="/" className="text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
              Dashboard
            </Link>
            <Link href="/incidents" className="text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
              Incidents
            </Link>
            <Link href="/verification" className="text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
              Verification
            </Link>
            <Link href="/audio" className="text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
              Audio Input
            </Link>
          </nav>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="flex-grow">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 shadow-inner">
        <div className="container mx-auto py-4 px-4 text-center text-sm text-gray-500 dark:text-gray-400">
          &copy; {new Date().getFullYear()} AudioTranscriptionFire | Emergency Response System
        </div>
      </footer>
    </div>
  );
} 