/**
 * Dashboard layout with sidebar navigation.
 */

import { Sidebar } from "@/components/dashboard/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-gradient-to-br from-[#F5F8F8] via-[#FAFCFC] to-[#F0F6F6]">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <main className="flex-1 ml-[280px] p-8 relative z-10">{children}</main>
    </div>
  );
}
