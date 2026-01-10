"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { Mail, Lock, AlertCircle } from "lucide-react";
import { login as apiLogin } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Header } from "@/components/ui/header";

function LoginContent() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionExpired, setSessionExpired] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();

  useEffect(() => {
    // Check if redirected due to session expiration
    if (searchParams.get('session_expired') === 'true') {
      setSessionExpired(true);
      setError("Your session has expired. Please log in again.");
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSessionExpired(false);
    setIsLoading(true);

    try {
      const response = await apiLogin(email, password);
      login(response.user, response.tokens);
      
      // Check if there's a redirect path stored
      const redirectPath = localStorage.getItem('redirect_after_login');
      if (redirectPath) {
        localStorage.removeItem('redirect_after_login');
        router.push(redirectPath);
      } else {
        router.push("/dashboard/intraday");
      }
    } catch (err: any) {
      setError(err.message || "Login failed. Please check your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-background to-muted/20">
      <Header />
      <div className="flex-1 flex items-center justify-center px-4 py-20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Welcome Back</h1>
          <p className="text-muted-foreground">
            Sign in to access your portfolio
          </p>
        </div>

        <div className="bg-card border border-border rounded-xl p-8 shadow-lg">
          <form onSubmit={handleSubmit} className="space-y-4">
            {sessionExpired && (
              <div className="bg-yellow-500/10 border border-yellow-500/20 text-yellow-700 dark:text-yellow-400 text-sm p-3 rounded-lg flex items-start gap-2">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Session Expired</p>
                  <p className="text-xs mt-1">Your login session has expired. Please sign in again to continue.</p>
                </div>
              </div>
            )}
            
            {error && !sessionExpired && (
              <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg flex items-start gap-2">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p>{error}</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-primary text-primary-foreground py-2 rounded-lg font-semibold hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="mt-6 text-center text-sm">
            <span className="text-muted-foreground">Don't have an account? </span>
            <Link href="/register" className="text-primary font-semibold hover:underline">
              Create one
            </Link>
          </div>
        </div>
      </motion.div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LoginContent />
    </Suspense>
  );
}
