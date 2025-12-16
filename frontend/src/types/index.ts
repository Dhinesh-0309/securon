// Frontend type definitions matching backend interfaces

export enum Severity {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL"
}

export enum LogSource {
  VPC_FLOW = "VPC_FLOW",
  CLOUDTRAIL = "CLOUDTRAIL",
  IAM = "IAM"
}

export enum AnomalyType {
  PORT_SCAN = "PORT_SCAN",
  BRUTE_FORCE = "BRUTE_FORCE",
  SUSPICIOUS_IP = "SUSPICIOUS_IP",
  UNUSUAL_API = "UNUSUAL_API"
}

export enum RuleSource {
  STATIC = "STATIC",
  ML_GENERATED = "ML_GENERATED"
}

export enum RuleStatus {
  ACTIVE = "ACTIVE",
  CANDIDATE = "CANDIDATE",
  REJECTED = "REJECTED"
}

export interface TimeRange {
  start: string;
  end: string;
}

export interface NormalizedLogEntry {
  timestamp: string;
  source_ip: string;
  destination_ip?: string;
  port?: number;
  protocol?: string;
  action: string;
  user?: string;
  resource?: string;
  api_call?: string;
}

export interface CloudLog {
  timestamp: string;
  source: LogSource;
  raw_data: Record<string, any>;
  normalized_data: NormalizedLogEntry;
}

export interface SecurityRule {
  id: string;
  name: string;
  description: string;
  severity: Severity;
  pattern: string;
  remediation: string;
  source: RuleSource;
  status: RuleStatus;
  created_at: string;
}

export interface ScanResult {
  severity: Severity;
  rule_id: string;
  description: string;
  file_path: string;
  line_number: number;
  remediation: string;
}

export interface AnomalyResult {
  id: string;
  type: AnomalyType;
  severity: number;
  confidence: number;
  affected_resources: string[];
  time_window: TimeRange;
}