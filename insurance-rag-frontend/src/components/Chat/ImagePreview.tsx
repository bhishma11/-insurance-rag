// src/components/Chat/ImagePreview.tsx
import { X, Image, AlertCircle, Loader2, CheckCircle } from 'lucide-react';

interface ImagePreviewProps {
  file: File;
  onRemove: () => void;
  isUploading?: boolean;
  analysisResult?: any;
  error?: string | null;
}

export const ImagePreview = ({ 
  file, 
  onRemove, 
  isUploading = false,
  analysisResult,
  error 
}: ImagePreviewProps) => {
  const imageUrl = URL.createObjectURL(file);

  const getStatusColor = () => {
    if (error) return 'border-red-500 dark:border-red-700';
    if (analysisResult) {
      if (analysisResult.classification === 'car_damage') return 'border-blue-500 dark:border-blue-400';
      if (analysisResult.classification === 'injury') return 'border-red-500 dark:border-red-400';
      return 'border-gray-500 dark:border-gray-600';
    }
    return 'border-gray-300 dark:border-gray-600';
  };

  const getStatusBadge = () => {
    if (isUploading) {
      return (
        <span className="inline-flex items-center gap-1 text-xs text-yellow-600 dark:text-yellow-400">
          <Loader2 className="w-3 h-3 animate-spin" />
          Analyzing...
        </span>
      );
    }
    if (error) {
      return (
        <span className="inline-flex items-center gap-1 text-xs text-red-600 dark:text-red-400">
          <AlertCircle className="w-3 h-3" />
          Failed
        </span>
      );
    }
    if (analysisResult) {
      const classification = analysisResult.classification;
      const icons: Record<string, string> = {
        car_damage: '🚗',
        injury: '🏥',
        other: '📷'
      };
      const labels: Record<string, string> = {
        car_damage: 'Car Damage',
        injury: 'Injury',
        other: 'Other'
      };
      return (
        <span className="inline-flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
          <CheckCircle className="w-3 h-3" />
          {icons[classification] || '📷'} {labels[classification] || 'Analyzed'}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
        <Image className="w-3 h-3" />
        {Math.round(file.size / 1024)}KB
      </span>
    );
  };

  return (
    <div className={`relative inline-flex items-center gap-3 p-2 pr-8 border-2 rounded-lg ${getStatusColor()} bg-white dark:bg-gray-800 shadow-sm max-w-sm`}>
      {/* Image thumbnail */}
      <img 
        src={imageUrl} 
        alt={file.name}
        className="w-10 h-10 rounded object-cover flex-shrink-0"
        onError={(e) => {
          (e.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40"><rect width="40" height="40" fill="%23e5e7eb"/><text x="20" y="25" font-size="16" text-anchor="middle" fill="%239ca3af">📷</text></svg>';
        }}
      />
      
      {/* File info */}
      <div className="flex flex-col min-w-0">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate max-w-[150px]">
          {file.name}
        </span>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {getStatusBadge()}
        </span>
      </div>

      {/* Remove button */}
      <button
        onClick={onRemove}
        className="absolute -top-1 -right-1 p-0.5 bg-gray-200 dark:bg-gray-700 rounded-full hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
      >
        <X className="w-3.5 h-3.5 text-gray-600 dark:text-gray-300" />
      </button>
    </div>
  );
};