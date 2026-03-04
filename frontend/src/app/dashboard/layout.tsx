/**
 * Dashboard layout with sidebar navigation.
 */

import { Sidebar } from "@/components/dashboard/Sidebar";
import { DashboardThemeProvider } from "@/components/dashboard/DashboardThemeProvider";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <DashboardThemeProvider>
      <div className="flex min-h-screen bg-gradient-to-br from-[#F5F8F8] via-[#FAFCFC] to-[#F0F6F6] dark:from-[#0F1419] dark:via-[#131920] dark:to-[#0D1117]">
        {/* Sidebar */}
        <Sidebar />

        {/* Main content */}
        <main className="flex-1 ml-[280px] p-8 relative z-10">{children}</main>
      </div>
    </DashboardThemeProvider>
  );
}
