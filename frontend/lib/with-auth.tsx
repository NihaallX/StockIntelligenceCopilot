"use client";

import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { LoadingPage } from "@/components/ui/loading";

export function withAuth<P extends object>(
  Component: React.ComponentType<P>
) {
  return function ProtectedRoute(props: P) {
    const { user, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!isLoading && !user) {
        router.push("/login");
      }
    }, [user, isLoading, router]);

    if (isLoading) {
      return <LoadingPage message="Authenticating..." />;
    }

    if (!user) {
      return null;
    }

    return <Component {...props} />;
  };
}
