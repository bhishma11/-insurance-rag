// src/types.ts
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
  use_deepseek_only?: boolean;  // ← ADD THIS
}

export interface ChatResponse {
  response: string;
  session_id: string;
  sources?: any[];
  calculation_steps?: CalculationStep[];
  premium_data?: any;  // ← ADD THIS
  model_used?: string;
}