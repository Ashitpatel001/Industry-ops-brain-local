import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import PrivacyBanner from "@/components/PrivacyBanner";

export const metadata: Metadata = {
  title: "Ops Brain Local | Industrial AI Command Center",
  description: "100% On-Premise & Air-Gapped Industrial RAG Engine for Plant Reliability and Compliance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="flex min-h-screen bg-[#F5F6F8] text-[#0B1F3A] antialiased">
        <Sidebar />
        <div className="flex-1 flex flex-col min-h-screen overflow-x-hidden">
          <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
            <PrivacyBanner />
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
