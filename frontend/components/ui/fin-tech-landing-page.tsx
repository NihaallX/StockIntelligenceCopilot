"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  TrendingUp,
  Shield,
  BarChart3,
  Zap,
  Check,
  ArrowRight,
} from "lucide-react";

interface FinTechLandingPageProps {
  className?: string;
}

export function FinTechLandingPage({ className }: FinTechLandingPageProps) {
  const features = [
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Technical Analysis",
      description: "Advanced indicators and signals powered by real-time market data",
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Fundamental Scoring",
      description: "Deep analysis of valuations, growth, profitability, and financial health",
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Scenario Analysis",
      description: "Probabilistic best/base/worst case projections with risk metrics",
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Risk Management",
      description: "Personalized risk profiles with position limits and exposure controls",
    },
  ];

  const benefits = [
    "Real-time market analysis",
    "Portfolio tracking with P&L",
    "Multi-factor scoring algorithm",
    "Actionable recommendations",
    "Comprehensive risk assessment",
    "Secure authentication",
  ];

  return (
    <div className={`min-h-screen ${className}`}>
      {/* Hero Section */}
      <section className="container mx-auto px-6 pt-20 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-4xl mx-auto"
        >
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6">
            Stock Intelligence
            <span className="block text-primary mt-2">Powered by AI</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Make informed investment decisions with comprehensive technical analysis,
            fundamental scoring, and probabilistic scenario modeling.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 bg-primary text-primary-foreground rounded-lg font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity w-full sm:w-auto"
              >
                Get Started
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>
            <Link href="/login">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 border border-border rounded-lg font-semibold hover:bg-accent transition-colors w-full sm:w-auto"
              >
                Sign In
              </motion.button>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="p-6 rounded-xl border border-border bg-card hover:shadow-lg transition-shadow"
            >
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 text-primary">
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-sm text-muted-foreground">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Benefits Section */}
      <section className="container mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="max-w-5xl mx-auto"
        >
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-4">
                Everything you need for intelligent investing
              </h2>
              <p className="text-muted-foreground mb-6">
                Our platform combines cutting-edge technical analysis with deep
                fundamental research and probabilistic scenario modeling to give you
                a complete picture of any stock.
              </p>
              <ul className="space-y-3">
                {benefits.map((benefit, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="flex items-center gap-3"
                  >
                    <div className="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Check className="w-3 h-3 text-primary" />
                    </div>
                    <span>{benefit}</span>
                  </motion.li>
                ))}
              </ul>
            </div>
            <div className="relative">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
                className="aspect-square rounded-2xl bg-gradient-to-br from-primary/20 via-primary/10 to-transparent border border-border p-8 flex items-center justify-center"
              >
                <div className="text-center">
                  <div className="text-6xl font-bold text-primary mb-2">43/100</div>
                  <div className="text-sm text-muted-foreground">Combined Score</div>
                  <div className="mt-6 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Technical</span>
                      <span className="font-semibold">53%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Fundamental</span>
                      <span className="font-semibold">21%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Scenario</span>
                      <span className="font-semibold">+0.5%</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto text-center bg-primary/5 rounded-2xl p-12 border border-border"
        >
          <h2 className="text-3xl font-bold mb-4">
            Ready to make smarter investment decisions?
          </h2>
          <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of investors using data-driven insights to optimize
            their portfolio strategy.
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-3 bg-primary text-primary-foreground rounded-lg font-semibold inline-flex items-center gap-2 hover:opacity-90 transition-opacity"
          >
            Start Free Trial
            <ArrowRight className="w-5 h-5" />
          </motion.button>
          <p className="text-xs text-muted-foreground mt-4">
            No credit card required • Cancel anytime
          </p>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-6 py-8 border-t border-border">
        <div className="text-center text-sm text-muted-foreground">
          <p>
            This is for informational purposes only and does not constitute
            financial advice.
          </p>
          <p className="mt-2">
            © 2026 Stock Intelligence Copilot. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
