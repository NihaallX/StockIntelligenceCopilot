import type { Metadata } from "next";
import { Space_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "Stock Intelligence Copilot",
  description: "High-frequency stock analysis and portfolio management",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${spaceGrotesk.variable} ${jetbrainsMono.variable} font-sans antialiased bg-background text-foreground selection:bg-primary selection:text-primary-foreground flex min-h-screen flex-col`}>
        <AuthProvider>
          <div className="flex-1">
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
