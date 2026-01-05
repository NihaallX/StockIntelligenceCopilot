"use client";

import { withAuth } from "@/lib/with-auth";
import { DashboardNav } from "@/components/ui/dashboard-nav";

function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/20">
      <DashboardNav />
      <main className="container mx-auto px-6 py-8">{children}</main>
    </div>
  );
}

export default withAuth(DashboardLayout);
