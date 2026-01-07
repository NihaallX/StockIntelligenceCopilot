import { motion } from "framer-motion";
import { ShieldAlert, TrendingDown, AlertTriangle } from "lucide-react";

interface RiskZoneProps {
  stopLoss?: number;
  invalidationLevel?: number;
  worstCaseScenario: string;
  riskFactors: string[];
}

export function RiskZone({
  stopLoss,
  invalidationLevel,
  worstCaseScenario,
  riskFactors,
}: RiskZoneProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-red-50 dark:bg-red-900/10 border-2 border-red-200 dark:border-red-800 rounded-xl p-6"
    >
      <div className="flex items-start gap-3 mb-4">
        <ShieldAlert className="w-6 h-6 text-red-600 flex-shrink-0" />
        <div>
          <h3 className="text-lg font-bold text-red-900 dark:text-red-100 mb-1">Risk Zone</h3>
          <p className="text-sm text-red-700 dark:text-red-300">What can go wrong</p>
        </div>
      </div>

      {/* Invalidation Levels */}
      {(stopLoss || invalidationLevel) && (
        <div className="grid grid-cols-2 gap-4 mb-4">
          {stopLoss && (
            <div className="bg-red-100 dark:bg-red-900/20 rounded-lg p-3">
              <div className="text-xs text-red-700 dark:text-red-400 mb-1">Stop Loss</div>
              <div className="text-xl font-bold text-red-900 dark:text-red-100">₹{stopLoss.toFixed(2)}</div>
            </div>
          )}
          {invalidationLevel && (
            <div className="bg-red-100 dark:bg-red-900/20 rounded-lg p-3">
              <div className="text-xs text-red-700 dark:text-red-400 mb-1">Invalidation</div>
              <div className="text-xl font-bold text-red-900 dark:text-red-100">₹{invalidationLevel.toFixed(2)}</div>
            </div>
          )}
        </div>
      )}

      {/* Worst Case */}
      <div className="bg-red-100 dark:bg-red-900/20 rounded-lg p-4 mb-4">
        <div className="flex items-start gap-2">
          <TrendingDown className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <div className="text-xs font-semibold text-red-700 dark:text-red-400 mb-1">Worst Case Scenario</div>
            <p className="text-sm text-red-900 dark:text-red-100">{worstCaseScenario}</p>
          </div>
        </div>
      </div>

      {/* Risk Factors */}
      <div className="space-y-2">
        <div className="text-xs font-semibold text-red-700 dark:text-red-400 mb-2">What Could Go Wrong</div>
        {riskFactors.map((factor, index) => (
          <div key={index} className="flex items-start gap-2 text-sm">
            <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
            <span className="text-red-900 dark:text-red-100">{factor}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
