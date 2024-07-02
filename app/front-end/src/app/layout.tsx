import * as React from "react";
import { Metadata } from "next";
import ClientLayout from "@/components/ClientLayout";

export const metadata: Metadata = {
  title: "R&D Virtual Expert",
  description: "GenAI-powered knowledge tool for R&D",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <ClientLayout>{children}</ClientLayout>
    </>
  );
}
