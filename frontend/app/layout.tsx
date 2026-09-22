import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "leaflet/dist/leaflet.css";
import "./globals.css";

import { AppShell } from "@/components/layout/AppShell";
import { MosaicProvider } from "@/components/providers/MosaicProvider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "MOSAIC | Monsoon Intelligence System",
  description:
    "Probabilistic monsoon onset, break, revival and heavy-rain intelligence for agricultural planning.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} antialiased`}>
        <MosaicProvider>
          <AppShell>{children}</AppShell>
        </MosaicProvider>
      </body>
    </html>
  );
}
