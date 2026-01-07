"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { getMarketPulse, MarketPulse } from "@/lib/api";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Activity, Droplets, Eye, PauseCircle, AlertCircle } from "lucide-react";

export default function MarketPulsePage() {
  const { tokens } = useAuth();
  const router = useRouter();
  const [pulse, setPulse] = useState<MarketPulse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access_token) {
      router.push("/login");
      return;
    }

    fetchPulse();
  }, [tokens]);

  const fetchPulse = async () => {
    if (!tokens?.access_token) return;

    try {
      setIsLoading(true);
      const data = await getMarketPulse(tokens.access_token);
      setPulse(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to fetch market pulse");
    } finally {
      setIsLoading(false);
    }
  };

  const getRegimeColor = (regime: string) => {
    const colors = {
      trending: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 border-green-300",
      choppy: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300 border-amber-300",
      "range-bound": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 border-blue-300",
      "low-liquidity": "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 border-red-300"
    };
    return colors[regime as keyof typeof colors] || colors.choppy;
  };

  const getBiasIcon = (bias: string) => {
    if (bias.toLowerCase().includes("strong")) return <TrendingUp className="w-4 h-4" />;
    if (bias.toLowerCase().includes("weak")) return <TrendingDown className="w-4 h-4" />;
    return <Activity className="w-4 h-4" />;
  };

  const getLiquidityColor = (liquidity: string) => {
    const colors = {
      low: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 border-red-300",
      normal: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 border-blue-300",
      high: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 border-green-300"
    };
    return colors[liquidity as keyof typeof colors] || colors.normal;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Reading market conditions...</p>
        </div>
      </div>
    );
  }

  if (error || !pulse) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-xl p-6 max-w-md">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <p className="text-center text-red-900 dark:text-red-100 mb-4">
            {error || "Unable to fetch market conditions"}
          </p>
          <button
            onClick={fetchPulse}
            className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30 p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto space-y-6"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">Today's Market Pulse</h1>
          <p className="text-muted-foreground">Is today worth trading?</p>
        </div>

        {/* Market Status Strip */}
        <div className="bg-card border border-border rounded-xl p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {/* Regime */}
            <div>
              <div className="text-xs text-muted-foreground mb-2">Market Regime</div>
              <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border ${getRegimeColor(pulse.regime)}`}>
                <Activity className="w-5 h-5" />
                <span className="font-semibold capitalize">{pulse.regime}</span>
              </div>
            </div>

            {/* Index Bias */}
            <div>
              <div className="text-xs text-muted-foreground mb-2">Index Bias</div>
              <div className="space-y-2">
                {pulse.index_bias.map((index, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    {getBiasIcon(index.bias)}
                    <span className="font-medium">{index.name}:</span>
                    <span className={
                      index.bias.toLowerCase().includes("strong") ? "text-green-600 dark:text-green-400" :
                      index.bias.toLowerCase().includes("weak") ? "text-red-600 dark:text-red-400" :
                      "text-muted-foreground"
                    }>
                      {index.bias}
                    </span>
                    {index.change_percent !== undefined && index.change_percent !== null && (
                      <span className="text-xs text-muted-foreground">
                        ({index.change_percent > 0 ? "+" : ""}{index.change_percent.toFixed(2)}%)
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Liquidity */}
            <div>
              <div className="text-xs text-muted-foreground mb-2">Liquidity</div>
              <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border ${getLiquidityColor(pulse.liquidity)}`}>
                <Droplets className="w-5 h-5" />
                <span className="font-semibold capitalize">{pulse.liquidity}</span>
              </div>
            </div>
          </div>

          {/* Market Summary */}
          <div className={`p-4 rounded-lg border-2 ${
            pulse.worth_trading 
              ? "bg-blue-50 dark:bg-blue-900/10 border-blue-300 dark:border-blue-700"
              : "bg-amber-50 dark:bg-amber-900/10 border-amber-300 dark:border-amber-700"
          }`}>
            <p className="text-lg font-medium text-center leading-relaxed">
              {pulse.summary}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => router.push("/dashboard/opportunities")}
            className="flex items-center justify-center gap-3 px-8 py-6 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-all shadow-lg hover:shadow-xl"
          >
            <Eye className="w-6 h-6" />
            <div className="text-left">
              <div className="text-lg font-bold">View Opportunities</div>
              <div className="text-sm opacity-90">See actionable setups</div>
            </div>
          </button>

          <button
            onClick={() => {
              localStorage.setItem("stand_down_mode", "true");
              router.push("/dashboard");
            }}
            className="flex items-center justify-center gap-3 px-8 py-6 bg-muted text-muted-foreground border-2 border-border rounded-xl hover:bg-muted/80 transition-all"
          >
            <PauseCircle className="w-6 h-6" />
            <div className="text-left">
              <div className="text-lg font-bold">Stand Down Today</div>
              <div className="text-sm">Wait for better conditions</div>
            </div>
          </button>
        </div>

        {/* Conditions Warning */}
        {!pulse.worth_trading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800 rounded-lg p-4"
          >
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-amber-900 dark:text-amber-100">
                  Challenging Conditions
                </p>
                <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">
                  Current market conditions don't favor active intraday trading. Standing down is a valid strategy.
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Footer */}
        <div className="text-center text-xs text-muted-foreground">
          Last updated: {new Date(pulse.timestamp).toLocaleTimeString("en-IN")} IST
        </div>
      </motion.div>
    </div>
  );
}
