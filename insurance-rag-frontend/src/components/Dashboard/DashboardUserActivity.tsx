// src/components/Dashboard/DashboardUserActivity.tsx
import { User, Mail, Building, Calendar, Clock, CheckCircle, XCircle } from 'lucide-react';

interface UserData {
  user_id: string;
  email: string;
  name: string;
  company: string;
  status: string;
  created_at: string;
}

interface Props {
  users: UserData[];
  loading?: boolean;
}

export const DashboardUserActivity = ({ users, loading = false }: Props) => {
  const getStatusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'ACTIVE': return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400';
      case 'PENDING': return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400';
      case 'REJECTED': return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400';
      default: return 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'ACTIVE': return <CheckCircle className="w-3.5 h-3.5 text-green-500" />;
      case 'PENDING': return <Clock className="w-3.5 h-3.5 text-yellow-500" />;
      case 'REJECTED': return <XCircle className="w-3.5 h-3.5 text-red-500" />;
      default: return null;
    }
  };

  if (loading) {
    return (
      <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          👥 Users
        </h3>
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse flex items-center gap-3 p-3 bg-white dark:bg-gray-900/50 rounded-lg">
              <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
              <div className="flex-1">
                <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="h-3 w-32 bg-gray-200 dark:bg-gray-700 rounded mt-1"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!users || users.length === 0) {
    return (
      <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          👥 Users
        </h3>
        <div className="text-center py-6 text-gray-500 dark:text-gray-400 text-sm">
          <User className="w-8 h-8 mx-auto mb-2 text-gray-300 dark:text-gray-600" />
          No users registered yet
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        👥 Users ({users.length})
      </h3>

      <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
        {users.slice(0, 10).map((user, i) => (
          <div
            key={i}
            className="flex items-center justify-between p-2.5 bg-white dark:bg-gray-900/50 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors border border-gray-100 dark:border-gray-800"
          >
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                {user.name?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {user.name || 'Unknown'}
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full ${getStatusColor(user.status)} flex-shrink-0`}>
                    {user.status || 'UNKNOWN'}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                  <span className="flex items-center gap-1 truncate">
                    <Mail className="w-3 h-3 flex-shrink-0" />
                    {user.email || 'No email'}
                  </span>
                  {user.company && (
                    <span className="flex items-center gap-1 truncate">
                      <Building className="w-3 h-3 flex-shrink-0" />
                      {user.company}
                    </span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1 flex-shrink-0">
              {getStatusIcon(user.status)}
            </div>
          </div>
        ))}
      </div>

      {users.length > 10 && (
        <div className="text-center mt-2 text-xs text-gray-400 dark:text-gray-500">
          Showing 10 of {users.length} users
        </div>
      )}
    </div>
  );
};

// ✅ Named export (already done above)
// Also export as default for flexibility
export default DashboardUserActivity;