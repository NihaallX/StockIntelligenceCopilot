"use client";

import { BackgroundPaperShaders } from "@/components/ui/background-paper-shaders";
import { FinTechLandingPage } from "@/components/ui/fin-tech-landing-page";
import { Header } from "@/components/ui/header";
import { Footer } from "@/components/ui/footer";

export default function HomePage() {
  return (
    <div className="relative min-h-screen flex flex-col bg-gradient-to-br from-background via-background to-muted/30">
      {/* Animated shader background - fixed, behind everything, no pointer events */}
      <BackgroundPaperShaders />
      
      {/* Header */}
      <Header />
      
      {/* Main content - positioned above background with proper z-index */}
      <div className="relative z-10 flex-1 pt-20">
        <FinTechLandingPage />
      </div>

      {/* Footer */}
      <div className="relative z-10">
        <Footer />
      </div>
    </div>
  );
}
