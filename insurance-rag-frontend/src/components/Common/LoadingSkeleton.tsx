import React from 'react';
import { LemonLogo } from './LemonLogo';

interface LoadingSkeletonProps {
  type?: 'chat' | 'dashboard' | 'login';
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ type = 'chat' }) => {
  if (type === 'login') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-logo">
            <div className="logo-icon">
              <LemonLogo size={44} animated={false} />
            </div>
            <div className="h-8 w-40 bg-gray-200 dark:bg-gray-700 rounded mx-auto mt-3 skeleton"></div>
            <div className="h-4 w-56 bg-gray-200 dark:bg-gray-700 rounded mx-auto mt-2 skeleton"></div>
          </div>
          <div className="space-y-4 auth-form">
            <div className="form-group">
              <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
              <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded-xl mt-1 skeleton"></div>
            </div>
            <div className="form-group">
              <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
              <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded-xl mt-1 skeleton"></div>
            </div>
            <div className="h-12 bg-gradient-to-r from-blue-200 to-purple-200 dark:from-blue-700 dark:to-purple-700 rounded-xl skeleton"></div>
          </div>
        </div>
      </div>
    );
  }

  if (type === 'dashboard') {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 mb-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gray-200 dark:bg-gray-700 skeleton"></div>
            <div className="flex-1">
              <div className="h-6 w-48 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
              <div className="h-4 w-64 bg-gray-200 dark:bg-gray-700 rounded mt-2 skeleton"></div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
              <div className="h-8 w-16 bg-gray-200 dark:bg-gray-700 rounded mt-2 skeleton"></div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="h-6 w-48 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
            <div className="mt-4 space-y-4">
              <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded-xl skeleton"></div>
              <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-xl skeleton"></div>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="h-6 w-32 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
            <div className="mt-4 space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded-xl skeleton"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Chat skeleton
  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-gray-900">
      <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full skeleton"></div>
          <div>
            <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
            <div className="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded mt-1 skeleton"></div>
          </div>
        </div>
      </div>
      <div className="flex-1 p-6 space-y-4 overflow-y-auto">
        {[...Array(3)].map((_, i) => (
          <div key={i} className={`flex ${i % 2 === 0 ? 'justify-end' : 'justify-start'}`}>
            <div className={`w-2/3 ${i % 2 === 0 ? 'bg-blue-100 dark:bg-blue-800' : 'bg-gray-100 dark:bg-gray-800'} rounded-2xl p-4 skeleton`}>
              <div className="h-4 w-full bg-white/50 dark:bg-gray-600/50 rounded"></div>
              <div className="h-4 w-3/4 bg-white/50 dark:bg-gray-600/50 rounded mt-2"></div>
            </div>
          </div>
        ))}
      </div>
      <div className="border-t border-gray-200 dark:border-gray-700 p-4">
        <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded-xl skeleton"></div>
      </div>
    </div>
  );
};

export default LoadingSkeleton;