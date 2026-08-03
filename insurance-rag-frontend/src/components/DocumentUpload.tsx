import { useState, useRef } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle, Loader2, FileSearch } from 'lucide-react';
import { api } from '../services/api';

interface DocumentResult {
  filename: string;
  file_extension: string;
  status: string;
  classification: {
    type: string;
    confidence: number;
    detected_type: string;
    keywords_found: string[];
    reason: string;
  };
  structured_data: Record<string, any>;
  preview: string;
  text_length: number;
}

export const DocumentUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<DocumentResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      uploadFile(droppedFile);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      uploadFile(selectedFile);
    }
  };

  const uploadFile = async (fileToUpload: File) => {
    setIsProcessing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', fileToUpload);

    try {
      const response = await fetch('http://localhost:8000/api/documents/upload', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (data.status === 'error') {
        setError(data.message);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError('Failed to upload document. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const clearUpload = () => {
    setFile(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getStatusColor = (type: string) => {
    switch (type) {
      case 'insurance':
        return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case 'non_insurance':
        return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case 'uncertain':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-4">
      {/* Upload Area */}
      {!file && !isProcessing && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
            isDragging
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.docx,.txt,.html,.htm,.xlsx,.xls,.pptx,.ppt"
          />
          <div className="flex flex-col items-center gap-3">
            <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <Upload className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                Upload Document
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Drag & drop or click to upload insurance policies
              </p>
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Choose File
            </button>
            <p className="text-xs text-gray-400 dark:text-gray-500">
              Supports: PDF, DOCX, TXT, HTML, XLSX, PPTX
            </p>
          </div>
        </div>
      )}

      {/* Processing */}
      {isProcessing && (
        <div className="flex flex-col items-center justify-center p-8">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Processing document...</p>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-4">
          {/* File Header */}
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-blue-500" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white">{result.filename}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {result.text_length} characters • {result.file_extension}
                </p>
              </div>
            </div>
            <button
              onClick={clearUpload}
              className="p-1 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>

          {/* Classification Status */}
          <div className={`p-4 rounded-xl border ${getStatusColor(result.classification.type)}`}>
            <div className="flex items-start gap-3">
              {result.classification.type === 'insurance' && (
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              )}
              {result.classification.type === 'non_insurance' && (
                <X className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              )}
              {result.classification.type === 'uncertain' && (
                <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
              )}
              <div>
                <p className="font-semibold">
                  {result.classification.type === 'insurance' && '✅ Insurance Document'}
                  {result.classification.type === 'non_insurance' && '❌ Non-Insurance Document'}
                  {result.classification.type === 'uncertain' && '⚠️ Uncertain Classification'}
                </p>
                <p className="text-sm opacity-80">
                  {result.classification.reason}
                </p>
                {result.classification.detected_type !== 'Unknown' && (
                  <p className="text-sm font-medium mt-1">
                    Detected Type: {result.classification.detected_type}
                  </p>
                )}
                <p className="text-xs opacity-70 mt-1">
                  Confidence: {(result.classification.confidence * 100).toFixed(1)}%
                </p>
                {result.classification.keywords_found.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {result.classification.keywords_found.slice(0, 5).map((kw, i) => (
                      <span key={i} className="text-xs px-2 py-0.5 bg-white/30 dark:bg-black/20 rounded-full">
                        {kw}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Structured Data */}
          {result.structured_data && Object.keys(result.structured_data).length > 0 && (
            <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📋 Extracted Data</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {Object.entries(result.structured_data).map(([key, value]) => (
                  value && (
                    <div key={key} className="text-sm">
                      <span className="text-gray-500 dark:text-gray-400">{key.replace('_', ' ').title()}:</span>
                      <span className="font-medium text-gray-900 dark:text-white ml-1">{value}</span>
                    </div>
                  )
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          {result.classification.type === 'insurance' && (
            <div className="flex gap-3">
              <button className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors">
                <FileSearch className="w-4 h-4 inline mr-2" />
                Ask Questions About This Policy
              </button>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-800 dark:text-red-300">Error</p>
              <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};