import { Zap, FileCheck, Scale, Calculator } from 'lucide-react';
import { useChatStore } from '../../stores/chatStore';

const actions = [
  { 
    icon: Calculator,
    label: 'Get Quote',
    prompt: 'Calculate my premium for 30 year old with $35,000 car'
  },
  { 
    icon: FileCheck,
    label: 'Claim Status',
    prompt: 'Check claim status for CL-12345'
  },
  { 
    icon: Scale,
    label: 'Compare Policies',
    prompt: 'Compare auto and renters insurance'
  },
  { 
    icon: Zap,
    label: 'Quick Quote',
    prompt: 'What is my average premium for my age?'
  },
];

export const QuickActions = () => {
  const { sendMessage, addMessage } = useChatStore();

  const handleAction = (prompt: string) => {
    sendMessage(prompt);
  };

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Quick Actions</p>
      <div className="space-y-1.5">
        {actions.map((action) => (
          <button
            key={action.label}
            onClick={() => handleAction(action.prompt)}
            className="w-full flex items-center gap-2.5 px-3 py-2 bg-gray-50 hover:bg-blue-50 rounded-lg transition-all duration-200 group border border-gray-100 hover:border-blue-200"
          >
            <action.icon className="w-4 h-4 text-gray-400 group-hover:text-blue-600 transition-colors" />
            <span className="text-sm text-gray-600 group-hover:text-blue-700 transition-colors">{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};