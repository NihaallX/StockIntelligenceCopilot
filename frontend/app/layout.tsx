import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import ExperimentalModeToggle from "@/components/experimental/ExperimentalModeToggle";

export const metadata: Metadata = {
  title: "Stock Intelligence Copilot",
  description: "AI-powered stock analysis and portfolio management",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <AuthProvider>
          {children}
          {/* Persistent experimental mode toggle on all pages */}
          <ExperimentalModeToggle />
        </AuthProvider>
      </body>
    </html>
  );
}
