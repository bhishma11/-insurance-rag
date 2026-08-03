import { CalculationStep } from '../../types';

interface Props {
  steps: CalculationStep[];
}

export const CalculationSteps = ({ steps }: Props) => {
  return (
    <div className="bg-gray-50 rounded-lg p-4 my-2 border border-gray-200">
      <h4 className="text-sm font-semibold text-gray-700 mb-3">
        📊 Premium Calculation Breakdown
      </h4>
      
      <div className="space-y-3">
        {steps.map((step, idx) => (
          <div key={idx} className="flex items-start gap-3">
            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center mt-0.5">
              <span className="text-xs font-bold text-blue-600">{step.stepNumber}</span>
            </div>
            
            <div className="flex-1">
              <div className="flex justify-between items-baseline">
                <p className="text-sm text-gray-700">{step.description}</p>
                <span className="text-sm font-mono font-semibold text-gray-900">
                  {step.calculation}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-0.5">{step.details}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};