import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Activity, Clock } from "lucide-react";

interface DecisionHeaderProps {
  ticker: string;
  bias: "bullish" | "bearish" | "neutral";
  confidence: number;
  regime: string;
  currentPrice: number;
  timestamp: string;
}

export function DecisionHeader({
  ticker,
  bias,
  confidence,
  regime,
  currentPrice,
  timestamp,
}: DecisionHeaderProps) {
  const getBiasColor = () => {
    if (bias === "bullish") return "text-green-600 dark:text-green-400";
    if (bias === "bearish") return "text-red-600 dark:text-red-400";
    return "text-muted-foreground";
  };

  const getBiasIcon = () => {
    if (bias === "bullish") return <TrendingUp className="w-12 h-12" />;
    if (bias === "bearish") return <TrendingDown className="w-12 h-12" />;
    return <Activity className="w-12 h-12" />;
  };

  const getConfidenceColor = () => {
    if (confidence >= 75) return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300";
    if (confidence >= 55) return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300";
    return "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border-2 border-border rounded-xl p-8 mb-6"
    >
      <div className="flex items-center justify-between">
        {/* Left: Ticker + Bias */}
        <div className="flex items-center gap-6">
          <div className={getBiasColor()}>{getBiasIcon()}</div>
          <div>
            <h1 className="text-4xl font-bold mb-2">{ticker}</h1>
            <div className="flex items-center gap-3">
              <span className="text-2xl font-semibold capitalize text-muted-foreground">
                {bias}
              </span>
              <span className="text-lg text-muted-foreground">•</span>
              <span className="text-lg text-muted-foreground">₹{currentPrice.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Right: Confidence + Regime */}
        <div className="text-right space-y-3">
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border ${getConfidenceColor()}`}>
            <span className="text-sm opacity-75">Confidence</span>
            <span className="text-2xl font-bold">{confidence}%</span>
          </div>
          <div className="flex items-center justify-end gap-2 text-sm text-muted-foreground">
            <Activity className="w-4 h-4" />
            <span className="capitalize">{regime} regime</span>
          </div>
          <div className="flex items-center justify-end gap-2 text-xs text-muted-foreground">
            <Clock className="w-3 h-3" />
            <span>{new Date(timestamp).toLocaleTimeString("en-IN")}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
