"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { getPortfolioSummary, PortfolioSummary } from "@/lib/api";
import { motion } from "framer-motion";
import Link from "next/link";
import TodaysSituations from "./components/TodaysSituations";
import {
  TrendingUp,
  TrendingDown,
  Briefcase,
  DollarSign,
  Target,
  ArrowRight,
  Scale,
} from "lucide-react";

export default function DashboardPage() {
  const { user, tokens } = useAuth();
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSlowLoading, setIsSlowLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (tokens?.access_token) {
      setIsSlowLoading(false);
      setError("");
      const slowTimer = setTimeout(() => setIsSlowLoading(true), 3000);
      
      getPortfolioSummary(tokens.access_token)
        .then(setSummary)
        .catch((err: any) => {
          if (err.getUserMessage) {
            setError(err.getUserMessage());
          } else {
            setError("Unable to load portfolio summary");
          }
          
          // Handle auth errors
          if (err.category === 'auth') {
            setTimeout(() => window.location.href = '/login', 2000);
          }
        })
        .finally(() => {
          clearTimeout(slowTimer);
          setIsLoading(false);
          setIsSlowLoading(false);
        });
    }
  }, [tokens]);

  const stats = [
    {
      label: "Total Value",
      value: summary ? `₹${parseFloat(summary.total_value).toLocaleString('en-IN')}` : "-",
      icon: DollarSign,
      color: "text-blue-500",
    },
    {
      label: "Total Positions",
      value: summary?.total_positions ?? "-",
      icon: Briefcase,
      color: "text-purple-500",
    },
    {
      label: "Unrealized P&L",
      value: summary ? `$${parseFloat(summary.total_unrealized_pnl).toLocaleString()}` : "-",
      icon: summary && parseFloat(summary.total_unrealized_pnl) >= 0 ? TrendingUp : TrendingDown,
      color: summary && parseFloat(summary.total_unrealized_pnl) >= 0 ? "text-green-500" : "text-red-500",
    },
    {
      label: "P&L Percent",
      value: summary ? `${summary.total_unrealized_pnl_percent}%` : "-",
      icon: Target,
      color: "text-orange-500",
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Welcome back, {user?.full_name}</h1>
        <p className="text-muted-foreground">
          Here's an overview of your portfolio performance
        </p>
      </div>
      
      {isSlowLoading && (
        <div className="p-3 bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg text-sm">
          <p className="text-muted-foreground">
            ⏱️ Loading portfolio data is taking longer than usual. Please wait...
          </p>
        </div>
      )}
      
      {error && (
        <div className="p-4 bg-amber-50 dark:bg-amber-900/10 border border-amber-300 dark:border-amber-700 rounded-lg">
          <p className="text-sm text-muted-foreground">{error}</p>
          <p className="text-xs text-muted-foreground mt-2">
            Please try refreshing the page or contact support if this persists.
          </p>
        </div>
      )}

      {/* Stats Grid */}
      {!isLoading && !error && summary?.total_positions === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-card border border-border rounded-xl p-12 text-center"
        >
          <Briefcase className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-2xl font-semibold mb-3">Start Building Your Portfolio</h3>
          <p className="text-muted-foreground mb-6 max-w-md mx-auto">
            Add your first position to unlock portfolio-aware insights, risk management, 
            and personalized analysis based on your holdings.
          </p>
          <Link
            href="/dashboard/portfolio"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:opacity-90 transition-opacity"
          >
            Add First Position
            <ArrowRight className="w-5 h-5" />
          </Link>
          <p className="text-xs text-muted-foreground mt-6">
            💡 Tip: Adding positions helps us provide better risk assessments and portfolio-aware recommendations
          </p>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium text-muted-foreground">
                    {stat.label}
                  </span>
                  <Icon className={`w-5 h-5 ${stat.color}`} />
                </div>
                <div className="text-2xl font-bold">
                  {isLoading ? (
                    <div className="w-20 h-8 bg-muted animate-pulse rounded" />
                  ) : (
                    stat.value
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Today's Situations - Show for users with portfolio */}
      {!isLoading && !error && summary && summary.total_positions > 0 && (
        <TodaysSituations userId={user?.id} maxSignals={5} />
      )}

      {/* Risk Profile */}
      {user?.risk_profile && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-card border border-border rounded-xl p-6"
        >
          <h2 className="text-xl font-semibold mb-4">Risk Profile</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Risk Tolerance</p>
              <p className="text-lg font-semibold capitalize">
                {user.risk_profile.risk_tolerance}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Max Position Size</p>
              <p className="text-lg font-semibold">
                ${user.risk_profile.max_position_size_usd.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Max Drawdown</p>
              <p className="text-lg font-semibold">
                {user.risk_profile.max_drawdown_percent}%
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Largest Position */}
      {summary && summary.largest_position_ticker && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-card border border-border rounded-xl p-6"
        >
          <h2 className="text-xl font-semibold mb-4">Portfolio Concentration</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Largest Position</span>
              <span className="font-semibold">{summary.largest_position_ticker}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Concentration</span>
              <span className="font-semibold">{summary.largest_position_percent}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div
                className="bg-primary rounded-full h-2 transition-all"
                style={{ width: `${summary.largest_position_percent}%` }}
              />
            </div>
          </div>
        </motion.div>
      )}

      {/* Legal Disclaimer */}
      <div className="bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Scale className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
              Educational Tool • Not Financial Advice
            </h4>
            <p className="text-xs text-blue-800 dark:text-blue-200 leading-relaxed">
              This platform is for educational and informational purposes only. It does not provide personalized 
              financial advice or investment recommendations. Always consult a SEBI-registered investment advisor 
              before making investment decisions.{" "}
              <Link 
                href="/legal/disclaimer" 
                className="underline hover:text-blue-600 dark:hover:text-blue-400 font-medium"
              >
                Full Disclaimer
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
