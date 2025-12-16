"""Core data structures and types"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class LogSource(str, Enum):
    VPC_FLOW = "VPC_FLOW"
    CLOUDTRAIL = "CLOUDTRAIL"
    IAM = "IAM"
    WAF = "WAF"
    ALB = "ALB"
    CLOUDFRONT = "CLOUDFRONT"
    LAMBDA = "LAMBDA"
    API_GATEWAY = "API_GATEWAY"


class AnomalyType(str, Enum):
    PORT_SCAN = "PORT_SCAN"
    BRUTE_FORCE = "BRUTE_FORCE"
    SUSPICIOUS_IP = "SUSPICIOUS_IP"
    UNUSUAL_API = "UNUSUAL_API"


class RuleSource(str, Enum):
    STATIC = "STATIC"
    ML_GENERATED = "ML_GENERATED"


class RuleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CANDIDATE = "CANDIDATE"
    REJECTED = "REJECTED"


class TimeRange(BaseModel):
    start: datetime
    end: datetime


class NormalizedLogEntry(BaseModel):
    timestamp: datetime
    source_ip: str
    destination_ip: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    action: str
    user: Optional[str] = None
    resource: Optional[str] = None
    api_call: Optional[str] = None


class CloudLog(BaseModel):
    timestamp: datetime
    source: LogSource
    raw_data: Dict[str, Any]
    normalized_data: NormalizedLogEntry


class AnomalyPattern(BaseModel):
    feature: str
    expected_range: tuple[float, float]
    actual_value: float
    deviation: float


class Explanation(BaseModel):
    summary: str
    technical_details: str
    risk_level: Severity
    recommended_actions: List[str]


class TerraformResource(BaseModel):
    type: str
    name: str
    configuration: Dict[str, Any]
    file_path: str
    line_number: int