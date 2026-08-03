// frontend/src/types/index.ts

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  calculationSteps?: CalculationStep[];
  totalPremium?: number;
  isStreaming?: boolean;
  sources?: any[];
}

export interface CalculationStep {
  stepNumber: number;
  description: string;
  calculation: string;
  details: string;
}

export interface ChatRequest {
  query: string;
  session_id?: string;
  use_hyde?: boolean;
  use_memory?: boolean;
  temperature?: number;
  use_deepseek_only?: boolean;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  sources?: any[];
  calculation_steps?: CalculationStep[];
  premium_data?: any;
  model_used?: string;
}

export interface Session {
  session_id: string;
  title: string;
  timestamp: string;
  first_query: string;
}

// ============ Dashboard Types ============

export interface DashboardStats {
  // ✅ Simple stats from your backend
  total_users?: number;
  active_users?: number;
  total_requests?: number;
  pending_requests?: number;
  system_status?: string;
  safety_score?: number;
  uptime?: string;

  // ✅ Optional nested objects for compatibility
  system_health?: {
    status: string;
    uptime: string;
    cpu: string;
    memory: string;
    gpu: string;
    qlora_loaded: boolean;
  };
  request_stats?: {
    total_requests: number;
    qlora_requests: number;
    deepseek_requests: number;
    avg_latency: number;
    peak_hour: string;
  };
  token_usage?: {
    total_tokens: number;
    avg_tokens_per_request: number;
    estimated_cost: number;
    cost_per_user: Record<string, number>;
  };
  tool_usage?: Array<{
    tool: string;
    uses: number;
    success_rate: number;
    avg_latency: number;
  }>;
  governance_stats?: {
    safety_score: number;
    pii_detections: number;
    blocked_requests: number;
    audit_logs: number;
    explanations: number;
    safety_violations: Array<{
      category: string;
      count: number;
      severity: string;
    }>;
  };
  user_activity?: Array<{
    user_id: string;
    queries: number;
    tokens: number;
    cost: number;
    last_active: string;
  }>;
  recent_alerts?: Array<{
    time: string;
    type: string;
    message: string;
    severity: 'info' | 'warning' | 'error';
  }>;
  mcp_tools?: {
    total_calls: number;
    success_rate: number;
    avg_latency: number;
    tools: Array<{
      name: string;
      calls: number;
      success_rate: number;
      latency: number;
      last_used: string;
    }>;
    top_5: Array<{
      name: string;
      calls: number;
    }>;
  };
}

// ============ Analytics Types ============

export interface AnalyticsStats {
  users: {
    total_users: number;
    active_users_7d: number;
    active_users_30d: number;
    new_users_30d: number;
    growth_rate: number;
    retention_rate: number;
  };
  sessions: {
    total_sessions: number;
    avg_session_duration: number;
    bounce_rate: number;
  };
  features: {
    total_calls: number;
    feature_usage: Record<string, number>;
    most_used: Array<{ name: string; count: number }>;
    least_used: Array<{ name: string; count: number }>;
  };
  queries: {
    total_queries: number;
    categories: {
      premium: number;
      claim: number;
      comparison: number;
      coverage: number;
      general: number;
    };
    daily_queries: Array<{ date: string; count: number }>;
    peak_hour: number;
  };
  cost: {
    total_cost: number;
    qlora_cost: number;
    deepseek_cost: number;
    cost_per_query: number;
    cost_per_user: number;
    savings: number;
    savings_percentage: number;
  };
  performance: {
    avg_response_time: number;
    avg_qlora_time: number;
    avg_deepseek_time: number;
    success_rate: number;
  };
}

// ============ User Types ============

export interface User {
  user_id: string;
  email: string;
  name: string;
  company: string;
  status: 'PENDING' | 'ACTIVE' | 'REJECTED';
  created_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  token: string;
  user: User;
}

export interface SignupRequest {
  email: string;
  name: string;
  company?: string;
}

export interface SignupResponse {
  success: boolean;
  user_id: string;
  status: string;
  message: string;
}

export interface UsersResponse {
  success: boolean;
  users: User[];
}