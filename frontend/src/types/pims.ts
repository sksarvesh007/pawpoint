/**
 * PIMS integration types matching backend schemas.
 */

export interface PIMSConnectionStatus {
  pims_type: string;
  connection_status: string;
  last_sync_at: string | null;
  message?: string;
}

export interface PIMSTestConnectionResponse {
  connected: boolean;
  message: string;
  details?: Record<string, unknown>;
}

export interface PIMSSyncTriggerResponse {
  task_id: string;
  entity_type: string;
  status: string;
}

export interface PIMSSyncLog {
  id: string;
  sync_type: string;
  entity_type: string;
  status: string;
  triggered_by: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  records_processed: number;
  records_created: number;
  records_updated: number;
  records_failed: number;
  conflicts_detected: number;
  error_message: string | null;
  created_at: string;
}
