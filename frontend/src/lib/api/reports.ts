/**
 * API client for report endpoints.
 */

import { env } from "@/lib/env";
import type { ReportResponse } from "@/types/reports";

const API_BASE_URL = env.apiUrl;

export async function generateReport(
  reportType: string,
  startDate: string,
  endDate: string
): Promise<ReportResponse> {
  const params = new URLSearchParams({
    report_type: reportType,
    start_date: startDate,
    end_date: endDate,
  });

  const response = await fetch(
    `${API_BASE_URL}/api/v1/reports/generate?${params}`,
    {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to generate report: ${response.statusText}`);
  }

  return response.json();
}

export function getExportUrl(
  reportType: string,
  startDate: string,
  endDate: string
): string {
  const params = new URLSearchParams({
    report_type: reportType,
    start_date: startDate,
    end_date: endDate,
  });

  return `${API_BASE_URL}/api/v1/reports/export?${params}`;
}
