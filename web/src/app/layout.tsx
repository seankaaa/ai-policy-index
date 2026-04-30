import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Policy Index",
  description:
    "Interactive global choropleth of AI policy, government readiness, and public opinion across 140+ countries.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
