"use client";

import { motion } from "framer-motion";
import { Shield, AlertTriangle, FileText, Scale, Info } from "lucide-react";
import Link from "next/link";

export default function DisclaimerPage() {
  return (
    <div className="min-h-screen bg-background py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          {/* Header */}
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="p-4 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                <Scale className="w-12 h-12 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
            <h1 className="text-4xl font-bold">Legal Disclaimer</h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Important information about the nature and limitations of this service
            </p>
          </div>

          {/* Main Disclaimer */}
          <div className="bg-card border border-border rounded-xl p-8 space-y-6">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-6 h-6 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-1" />
              <div className="space-y-4">
                <h2 className="text-2xl font-semibold">Educational and Informational Purpose Only</h2>
                <p className="text-muted-foreground leading-relaxed">
                  Stock Intelligence Copilot is a <strong>decision-support tool</strong> designed for educational 
                  and informational purposes only. It is <strong>NOT</strong>:
                </p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-4">
                  <li>Personalized financial advice</li>
                  <li>Investment recommendations</li>
                  <li>Professional financial planning services</li>
                  <li>A substitute for consulting a registered investment advisor</li>
                  <li>A guarantee or prediction of future investment performance</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Key Points */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* No Fiduciary Relationship */}
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-3">
                <Shield className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                <h3 className="text-xl font-semibold">No Fiduciary Relationship</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Use of this service does not create a fiduciary, advisory, or professional relationship between 
                you and the service provider. We do not have access to your financial situation, risk tolerance, 
                or investment objectives.
              </p>
            </div>

            {/* No Execution */}
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-3">
                <FileText className="w-6 h-6 text-green-600 dark:text-green-400" />
                <h3 className="text-xl font-semibold">No Trade Execution</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                This tool <strong>cannot execute trades</strong> on your behalf. All investment decisions and 
                executions are made independently by you. We do not hold, manage, or have access to your funds 
                or securities.
              </p>
            </div>

            {/* Independent Verification */}
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-3">
                <Info className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                <h3 className="text-xl font-semibold">Verify Independently</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                All data, analysis, and context provided should be independently verified. Technical indicators, 
                fundamental data, and market context may be incomplete, delayed, or inaccurate. Always conduct 
                your own research.
              </p>
            </div>

            {/* Past Performance */}
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                <h3 className="text-xl font-semibold">Past Performance Warning</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Historical performance, backtesting results, and scenario analyses are not indicative of future 
                results. Market conditions change, and strategies that worked in the past may not work in the future.
              </p>
            </div>
          </div>

          {/* Risk Warning */}
          <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-xl p-6">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-1" />
              <div className="space-y-3">
                <h3 className="text-xl font-semibold text-red-900 dark:text-red-100">Investment Risks</h3>
                <p className="text-sm text-red-800 dark:text-red-200 leading-relaxed">
                  Investing in securities involves risk, including the potential loss of principal. You should:
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-red-800 dark:text-red-200 ml-4">
                  <li>Only invest funds you can afford to lose</li>
                  <li>Diversify your portfolio to manage risk</li>
                  <li>Understand the instruments you're investing in</li>
                  <li>Consult a SEBI-registered investment advisor for personalized advice</li>
                  <li>Be aware of your risk tolerance and investment horizon</li>
                </ul>
              </div>
            </div>
          </div>

          {/* SEBI Compliance */}
          <div className="bg-card border border-border rounded-xl p-6 space-y-4">
            <h3 className="text-xl font-semibold">Regulatory Compliance (India)</h3>
            <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
              <p>
                This service is designed to comply with SEBI (Securities and Exchange Board of India) regulations 
                regarding investment advice and recommendations:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  <strong>No Buy/Sell Recommendations:</strong> We provide technical and fundamental analysis, 
                  not specific buy or sell recommendations
                </li>
                <li>
                  <strong>Educational Focus:</strong> Content is educational in nature, helping you understand 
                  market mechanics and analysis techniques
                </li>
                <li>
                  <strong>Transparency:</strong> All analysis methods, data sources, and limitations are disclosed
                </li>
                <li>
                  <strong>No Guaranteed Returns:</strong> We never guarantee returns or promise specific outcomes
                </li>
              </ul>
            </div>
          </div>

          {/* Data Sources */}
          <div className="bg-card border border-border rounded-xl p-6 space-y-4">
            <h3 className="text-xl font-semibold">Data Sources and Accuracy</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Market data, financial statements, news articles, and other information are sourced from third-party 
              providers. While we strive for accuracy, we:
            </p>
            <ul className="list-disc list-inside space-y-2 text-sm text-muted-foreground ml-4">
              <li>Cannot guarantee the accuracy, completeness, or timeliness of data</li>
              <li>Are not responsible for errors in third-party data</li>
              <li>May experience delays in data updates</li>
              <li>Cannot verify all citations and sources in real-time</li>
            </ul>
          </div>

          {/* Limitation of Liability */}
          <div className="bg-card border border-border rounded-xl p-6 space-y-4">
            <h3 className="text-xl font-semibold">Limitation of Liability</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              To the maximum extent permitted by law, Stock Intelligence Copilot and its operators shall not be 
              liable for any direct, indirect, incidental, special, consequential, or punitive damages arising from:
            </p>
            <ul className="list-disc list-inside space-y-2 text-sm text-muted-foreground ml-4">
              <li>Investment decisions made based on information provided</li>
              <li>Errors, inaccuracies, or omissions in data or analysis</li>
              <li>Service interruptions or technical failures</li>
              <li>Loss of profits, data, or business opportunities</li>
            </ul>
          </div>

          {/* Contact */}
          <div className="bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
            <h3 className="text-xl font-semibold mb-3">Questions About This Disclaimer?</h3>
            <p className="text-sm text-muted-foreground mb-4">
              If you have questions about this disclaimer or how to use this service responsibly, please review 
              our documentation or consult with a qualified financial professional.
            </p>
            <Link 
              href="/dashboard"
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium"
            >
              Back to Dashboard
            </Link>
          </div>

          {/* Last Updated */}
          <div className="text-center text-sm text-muted-foreground">
            <p>Last updated: January 3, 2026</p>
            <p className="mt-2">
              By using this service, you acknowledge that you have read, understood, and agree to this disclaimer.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
