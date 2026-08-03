import { useState } from 'react';
import { FileText, Eye, X, Download, File, FileSearch } from 'lucide-react';

interface Document {
  id: string;
  name: string;
  type: string;
  size: string;
  date: string;
  content: string;
}

const mockDocuments: Document[] = [
  {
    id: '1',
    name: 'auto_policy.pdf',
    type: 'PDF',
    size: '2.4 MB',
    date: '2024-01-01',
    content: 'POLICY NUMBER: AUTO-2024-003\nVEHICLE: 2022 Toyota Camry\nCOVERAGE PERIOD: Jan 1, 2024 – Dec 31, 2024\nINSURER: Lemonade Insurance\n\nCOVERAGE DETAILS:\n- Collision: $1,000 deductible\n- Comprehensive: $500 deductible\n- Liability: $250,000/$500,000\n- Uninsured Motorist: Included\n- Glass: $0 deductible'
  },
  {
    id: '2',
    name: 'renters_policy.pdf',
    type: 'PDF',
    size: '1.8 MB',
    date: '2024-01-01',
    content: 'POLICY NUMBER: RENT-2024-001\nINSURER: Lemonade Insurance\nCOVERAGE PERIOD: Jan 1, 2024 – Dec 31, 2024\n\nCOVERAGE DETAILS:\n- Personal Property: $20,000\n- Liability: $100,000\n- Loss of Use: $5,000\n- Deductible: $500'
  },
  {
    id: '3',
    name: 'health_policy.pdf',
    type: 'PDF',
    size: '3.1 MB',
    date: '2024-01-01',
    content: 'POLICY NUMBER: HEALTH-2024-002\nINSURER: Lemonade Health\nCOVERAGE PERIOD: Jan 1, 2024 – Dec 31, 2024\n\nCOVERAGE DETAILS:\n- Deductible: $1,500\n- Out-of-Pocket Max: $5,000\n- ER Copay: $150\n- Hospitalization: 80% coverage'
  },
];

export const DocumentList = () => {
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredDocs = mockDocuments.filter(doc =>
    doc.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-3">
      {/* Search */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search documents..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <FileSearch className="absolute right-3 top-2 w-4 h-4 text-gray-400" />
      </div>

      {/* Document List */}
      <div className="space-y-1.5 max-h-64 overflow-y-auto">
        {filteredDocs.length === 0 ? (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">No documents found</p>
        ) : (
          filteredDocs.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <File className="w-4 h-4 text-blue-500 flex-shrink-0" />
                <span className="text-sm text-gray-700 dark:text-gray-300 truncate">{doc.name}</span>
              </div>
              <div className="flex items-center gap-1 flex-shrink-0">
                <button
                  onClick={() => setSelectedDoc(doc)}
                  className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                  title="Preview"
                >
                  <Eye className="w-3.5 h-3.5 text-gray-400 hover:text-blue-500" />
                </button>
                <button
                  className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                  title="Download"
                >
                  <Download className="w-3.5 h-3.5 text-gray-400 hover:text-green-500" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Document Preview Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden mx-4">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-blue-500" />
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{selectedDoc.name}</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {selectedDoc.type} • {selectedDoc.size} • {selectedDoc.date}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Document Content */}
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 font-mono bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                {selectedDoc.content}
              </pre>
            </div>

            {/* Actions */}
            <div className="flex gap-2 px-6 py-4 border-t border-gray-200 dark:border-gray-700">
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors">
                <Download className="w-4 h-4 inline mr-2" />
                Download
              </button>
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};