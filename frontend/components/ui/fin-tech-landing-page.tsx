"use client";

import Link from "next/link";
import { ArrowRight, BarChart3, Lock, Zap, MousePointer2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export function FinTechLandingPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen w-full text-center px-4 py-24 relative overflow-hidden">

      {/* Background Grid Pattern is in globals.css .technical-grid */}
      <div className="absolute inset-0 z-0 technical-grid opacity-30 pointer-events-none" />

      {/* Hero Section */}
      <div className="relative z-10 w-full max-w-7xl mx-auto space-y-12">

        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 text-xs font-mono font-medium text-primary border border-primary/20 bg-primary/5 rounded-none uppercase tracking-wider mb-8">
          <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
          System Online: v2.0.4
        </div>

        {/* Main Title */}
        <h1 className="text-6xl md:text-8xl font-bold tracking-tight text-white leading-[0.9]">
          MARKET INTELLIGENCE <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-emerald-400 to-cyan-500 animate-gradient">
            REDEFINED
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto font-mono leading-relaxed pt-4">
          Deploy AI agents to analyze complex market signals.
          Real-time execution. Institutional-grade precision.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-6 justify-center items-center pt-12 pb-24">
          <Link href="/register">
            <Button size="lg" className="h-14 px-10 text-lg font-bold bg-primary text-black hover:bg-primary/90 rounded-none border border-primary transition-all hover:scale-105 shadow-[0_0_30px_rgba(0,255,157,0.4)]">
              INITIALIZE TERMINAL <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </Link>
          <Link href="/login">
            <Button size="lg" variant="outline" className="h-14 px-10 text-lg font-mono rounded-none border-secondary-foreground/20 hover:bg-secondary/50 transition-all">
              ACCESS PORTAL
            </Button>
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left border-t border-border/20 pt-24">
          {[
            {
              icon: Zap,
              title: "Real-Time Signals",
              desc: "Sub-millisecond latency processing of global market feeds via Tavily MCP."
            },
            {
              icon: Lock,
              title: "Secure Core",
              desc: "Enterprise-grade encryption with persistent user memory context."
            },
            {
              icon: BarChart3,
              title: "Predictive Alpha",
              desc: "Advanced algorithmic models for high-confidence setup detection."
            }
          ].map((feature, idx) => (
            <div key={idx} className="group p-8 border border-border/40 bg-background/50 hover:border-primary/50 transition-all duration-300 hover:bg-background/80">
              <feature.icon className="w-10 h-10 text-primary mb-6 group-hover:scale-110 transition-transform duration-300" />
              <h3 className="text-xl font-bold mb-3 font-sans tracking-tight">{feature.title}</h3>
              <p className="text-base text-muted-foreground font-mono leading-relaxed">
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
