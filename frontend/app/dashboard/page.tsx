"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function DashboardPage() {
  const router = useRouter();
  const { tokens } = useAuth();

  useEffect(() => {
    // Redirect to intraday page (default workflow)
    if (tokens?.access_token) {
      router.push("/dashboard/intraday");
    }
  }, [router, tokens]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading today's watch...</p>
      </div>
    </div>
  );
}
