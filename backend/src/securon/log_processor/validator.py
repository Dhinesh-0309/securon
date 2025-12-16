"""Log validation utilities for ensuring data quality"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..interfaces.core_types import CloudLog, LogSource, NormalizedLogEntry


class ValidationError(Exception):
    """Custom exception for log validation errors"""
    pass


class LogValidator:
    """Validates log data for completeness and correctness"""
    
    def validate_raw_logs(self, logs: List[Dict[str, Any]], source: LogSource) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Validate raw logs before normalization
        Returns: (valid_logs, error_messages)
        """
        valid_logs = []
        errors = []
        
        for i, log in enumerate(logs):
            try:
                self._validate_raw_log(log, source)
                valid_logs.append(log)
            except ValidationError as e:
                errors.append(f"Log {i}: {str(e)}")
        
        return valid_logs, errors
    
    def validate_normalized_logs(self, logs: List[CloudLog]) -> Tuple[List[CloudLog], List[str]]:
        """
        Validate normalized logs for completeness
        Returns: (valid_logs, error_messages)
        """
        valid_logs = []
        errors = []
        
        for i, log in enumerate(logs):
            try:
                self._validate_normalized_log(log)
                valid_logs.append(log)
            except ValidationError as e:
                errors.append(f"Log {i}: {str(e)}")
        
        return valid_logs, errors
    
    def _validate_raw_log(self, log: Dict[str, Any], source: LogSource) -> None:
        """Validate a single raw log based on its source type"""
        if not isinstance(log, dict):
            raise ValidationError("Log must be a dictionary")
        
        if source == LogSource.VPC_FLOW:
            self._validate_vpc_flow_log(log)
        elif source == LogSource.CLOUDTRAIL:
            self._validate_cloudtrail_log(log)
        elif source == LogSource.IAM:
            self._validate_iam_log(log)
        elif source == LogSource.WAF:
            self._validate_waf_log(log)
        elif source == LogSource.ALB:
            self._validate_alb_log(log)
        elif source == LogSource.CLOUDFRONT:
            self._validate_cloudfront_log(log)
        elif source == LogSource.LAMBDA:
            self._validate_lambda_log(log)
        elif source == LogSource.API_GATEWAY:
            self._validate_api_gateway_log(log)
        else:
            raise ValidationError(f"Unknown log source: {source}")
    
    def _validate_vpc_flow_log(self, log: Dict[str, Any]) -> None:
        """Validate VPC Flow Log structure"""
        # Handle nested raw_data structure
        data = log.get('raw_data', log)
        
        # Check for required fields in different formats
        if 'message' in data:
            # Space-separated format
            fields = data['message'].split()
            if len(fields) < 13:
                raise ValidationError("VPC Flow Log message has insufficient fields")
        else:
            # Structured format - check for essential fields
            required_fields = ['srcaddr', 'action']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValidationError(f"Missing required VPC Flow Log fields: {missing_fields}")
        
        # Check for timestamp
        if not any(field in data for field in ['windowstart', 'start']) and 'timestamp' not in log:
            raise ValidationError("VPC Flow Log missing timestamp field")
    
    def _validate_cloudtrail_log(self, log: Dict[str, Any]) -> None:
        """Validate CloudTrail log structure"""
        # Handle nested raw_data structure
        data = log.get('raw_data', log)
        
        required_fields = ['eventName']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required CloudTrail fields: {missing_fields}")
        
        # Validate timestamp field exists
        if not any(field in data for field in ['eventTime']) and 'timestamp' not in log:
            raise ValidationError("CloudTrail log missing timestamp field")
    
    def _validate_iam_log(self, log: Dict[str, Any]) -> None:
        """Validate IAM log structure"""
        # Handle nested raw_data structure
        data = log.get('raw_data', log)
        
        # Check for at least one timestamp field
        if not any(field in data for field in ['eventTime']) and 'timestamp' not in log:
            raise ValidationError("IAM log missing timestamp field")
        
        # Check for at least one action field
        if not any(field in data for field in ['eventName', 'action']):
            raise ValidationError("IAM log missing action field")
    
    def _validate_waf_log(self, log: Dict[str, Any]) -> None:
        """Validate AWS WAF log structure"""
        # Handle nested raw_data structure
        data = log.get('raw_data', log)
        
        # Check for timestamp
        if not any(field in data for field in ['timestamp']) and 'timestamp' not in log:
            raise ValidationError("WAF log missing timestamp field")
        
        # Check for httpRequest structure
        if 'httpRequest' not in data:
            raise ValidationError("WAF log missing httpRequest field")
        
        http_request = data['httpRequest']
        if not isinstance(http_request, dict):
            raise ValidationError("WAF log httpRequest must be a dictionary")
        
        # Check for client IP
        if 'clientIP' not in http_request:
            raise ValidationError("WAF log missing clientIP in httpRequest")
    
    def _validate_alb_log(self, log: Dict[str, Any]) -> None:
        """Validate Application Load Balancer log structure"""
        # Handle nested raw_data structure
        data = log.get('raw_data', log)
        
        # Check for timestamp
        if not any(field in data for field in ['timestamp']) and 'timestamp' not in log:
            raise ValidationError("ALB log missing timestamp field")
        
        # Check for client IP (in various formats)
        if not any(field in data for field in ['client_ip', 'message']):
            raise ValidationError("ALB log missing client IP information")
    
    def _validate_cloudfront_log(self, log: Dict[str, Any]) -> None:
        """Validate CloudFront log structure"""
        # Handle nested raw_data structure
        data = log.get('raw_data', log)
        
        # Check for timestamp
        if not any(field in data for field in ['timestamp']) and 'timestamp' not in log:
            raise ValidationError("CloudFront log missing timestamp field")
        
        # Check for client IP (CloudFront uses c-ip)
        if not any(field in data for field in ['c-ip', 'client_ip']):
            raise ValidationError("CloudFront log missing client IP field")
    
    def _validate_lambda_log(self, log: Dict[str, Any]) -> None:
        """Validate AWS Lambda log structure"""
        # Handle nested raw_data structure
        data = log.get('raw_data', log)
        
        # Check for timestamp
        if not any(field in data for field in ['timestamp']) and 'timestamp' not in log:
            raise ValidationError("Lambda log missing timestamp field")
        
        # Lambda logs should have function name or event name
        if not any(field in data for field in ['functionName', 'eventName', 'resource']):
            raise ValidationError("Lambda log missing function or event identification")
    
    def _validate_api_gateway_log(self, log: Dict[str, Any]) -> None:
        """Validate API Gateway log structure"""
        # Handle nested raw_data structure
        data = log.get('raw_data', log)
        
        # Check for timestamp
        if not any(field in data for field in ['requestTime', 'timestamp']) and 'timestamp' not in log:
            raise ValidationError("API Gateway log missing timestamp field")
        
        # Check for HTTP method or resource path
        if not any(field in data for field in ['httpMethod', 'resourcePath', 'path']):
            raise ValidationError("API Gateway log missing HTTP method or resource path")
    
    def _validate_normalized_log(self, log: CloudLog) -> None:
        """Validate a normalized log entry"""
        if not isinstance(log.timestamp, datetime):
            raise ValidationError("Invalid timestamp in normalized log")
        
        if not log.normalized_data.source_ip:
            raise ValidationError("Missing source IP in normalized log")
        
        if not log.normalized_data.action:
            raise ValidationError("Missing action in normalized log")
        
        # Validate IP address format (basic check)
        if not self._is_valid_ip(log.normalized_data.source_ip):
            raise ValidationError(f"Invalid source IP format: {log.normalized_data.source_ip}")
        
        if log.normalized_data.destination_ip and not self._is_valid_ip(log.normalized_data.destination_ip):
            raise ValidationError(f"Invalid destination IP format: {log.normalized_data.destination_ip}")
        
        # Validate port range
        if log.normalized_data.port is not None:
            if not (0 <= log.normalized_data.port <= 65535):
                raise ValidationError(f"Invalid port number: {log.normalized_data.port}")
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Basic IP address validation"""
        if not ip or ip == '-':
            return False
        
        # Simple IPv4 validation
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        try:
            for part in parts:
                num = int(part)
                if not (0 <= num <= 255):
                    return False
            return True
        except ValueError:
            return False
    
    def get_validation_summary(self, total_logs: int, valid_logs: int, errors: List[str]) -> Dict[str, Any]:
        """Generate a validation summary report"""
        return {
            'total_logs': total_logs,
            'valid_logs': valid_logs,
            'invalid_logs': total_logs - valid_logs,
            'success_rate': (valid_logs / total_logs * 100) if total_logs > 0 else 0,
            'errors': errors[:10],  # Limit to first 10 errors
            'error_count': len(errors)
        }