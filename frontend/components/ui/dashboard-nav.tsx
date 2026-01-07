"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import {
  LayoutDashboard,
  Briefcase,
  BarChart3,
  LogOut,
  User,
  Scale,
  Activity,
  Eye,
  PauseCircle,
} from "lucide-react";
import { useState, useEffect } from "react";

export function DashboardNav() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [standDownMode, setStandDownMode] = useState(false);

  // Check for stand down mode on mount
  useEffect(() => {
    const mode = localStorage.getItem("stand_down_mode") === "true";
    setStandDownMode(mode);
  }, []);

  const navItems = [
    { href: "/dashboard/pulse", label: "Market Pulse", icon: Activity },
    { href: "/dashboard/opportunities", label: "Opportunities", icon: Eye },
    { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
    { href: "/dashboard/portfolio", label: "Portfolio", icon: Briefcase },
    { href: "/dashboard/analysis", label: "Analysis", icon: BarChart3 },
    { href: "/legal/disclaimer", label: "Legal", icon: Scale },
  ];

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const toggleStandDown = () => {
    const newMode = !standDownMode;
    setStandDownMode(newMode);
    localStorage.setItem("stand_down_mode", newMode.toString());
  };

  return (
    <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      {/* Stand Down Banner */}
      {standDownMode && (
        <div className="bg-amber-100 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-800">
          <div className="container mx-auto px-6 py-2 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm">
              <PauseCircle className="w-4 h-4 text-amber-600" />
              <span className="font-medium text-amber-900 dark:text-amber-100">
                Stood down for today
              </span>
            </div>
            <button
              onClick={toggleStandDown}
              className="text-xs px-3 py-1 bg-amber-600 text-white rounded hover:bg-amber-700 transition"
            >
              Resume Trading
            </button>
          </div>
        </div>
      )}

      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/dashboard/pulse" className="text-xl font-bold">
              Stock Intelligence
            </Link>
            <div className="flex gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "hover:bg-accent"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted">
              <User className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium">{user?.email}</span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-destructive/10 hover:text-destructive transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
