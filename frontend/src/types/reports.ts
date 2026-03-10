/**
 * Report types for the reports feature.
 */

export interface ReportResponse {
  report_type: string;
  title: string;
  start_date: string;
  end_date: string;
  generated_at: string;
  columns: string[];
  rows: Record<string, string | number>[];
  summary: Record<string, number>;
}
