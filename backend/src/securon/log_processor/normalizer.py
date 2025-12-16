"""Log normalization functionality for different cloud log types"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..interfaces.core_types import CloudLog, LogSource, NormalizedLogEntry


class LogNormalizer:
    """Normalizes different types of cloud logs into a standard format"""
    
    def normalize_logs(self, logs: List[Dict[str, Any]], source: LogSource) -> List[CloudLog]:
        """Normalize a list of raw logs based on their source type"""
        normalized_logs = []
        
        for raw_log in logs:
            try:
                if source == LogSource.VPC_FLOW:
                    normalized = self._normalize_vpc_flow_log(raw_log)
                elif source == LogSource.CLOUDTRAIL:
                    normalized = self._normalize_cloudtrail_log(raw_log)
                elif source == LogSource.IAM:
                    normalized = self._normalize_iam_log(raw_log)
                elif source == LogSource.WAF:
                    normalized = self._normalize_waf_log(raw_log)
                elif source == LogSource.ALB:
                    normalized = self._normalize_alb_log(raw_log)
                elif source == LogSource.CLOUDFRONT:
                    normalized = self._normalize_cloudfront_log(raw_log)
                elif source == LogSource.LAMBDA:
                    normalized = self._normalize_lambda_log(raw_log)
                elif source == LogSource.API_GATEWAY:
                    normalized = self._normalize_api_gateway_log(raw_log)
                else:
                    raise ValueError(f"Unsupported log source: {source}")
                
                cloud_log = CloudLog(
                    timestamp=normalized.timestamp,
                    source=source,
                    raw_data=raw_log,
                    normalized_data=normalized
                )
                normalized_logs.append(cloud_log)
                
            except Exception as e:
                # Log the error but continue processing other logs
                print(f"Error normalizing log: {e}")
                continue
                
        return normalized_logs
    
    def _normalize_vpc_flow_log(self, raw_log: Dict[str, Any]) -> NormalizedLogEntry:
        """Normalize VPC Flow Log format"""
        # VPC Flow Log format: version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes windowstart windowend action flowlogstatus
        
        # Handle both space-separated string format and dict format
        if isinstance(raw_log.get('message'), str):
            fields = raw_log['message'].split()
            if len(fields) >= 13:
                return NormalizedLogEntry(
                    timestamp=self._parse_timestamp(fields[9]),  # windowstart
                    source_ip=fields[3],  # srcaddr
                    destination_ip=fields[4],  # dstaddr
                    port=int(fields[6]) if fields[6] != '-' else None,  # dstport
                    protocol=self._protocol_number_to_name(fields[7]),  # protocol
                    action=fields[12].upper(),  # action (ACCEPT/REJECT)
                )
        
        # Handle nested raw_data structure
        data = raw_log.get('raw_data', raw_log)
        
        # Handle structured format
        return NormalizedLogEntry(
            timestamp=self._parse_timestamp(raw_log.get('timestamp', data.get('windowstart', data.get('start')))),
            source_ip=data.get('srcaddr', raw_log.get('source_ip', '')),
            destination_ip=data.get('dstaddr', data.get('destination_ip')),
            port=self._safe_int(data.get('dstport', data.get('port'))),
            protocol=self._protocol_number_to_name(data.get('protocol')),
            action=str(data.get('action', 'UNKNOWN')).upper(),
        )
    
    def _normalize_cloudtrail_log(self, raw_log: Dict[str, Any]) -> NormalizedLogEntry:
        """Normalize CloudTrail log format"""
        # Handle nested raw_data structure
        data = raw_log.get('raw_data', raw_log)
        
        # Extract from CloudTrail event structure
        event_time = data.get('eventTime', raw_log.get('timestamp'))
        source_ip = data.get('sourceIPAddress', '')
        
        # Handle nested user identity
        user_identity = data.get('userIdentity', {})
        user = user_identity.get('userName') or user_identity.get('type', '')
        
        return NormalizedLogEntry(
            timestamp=self._parse_timestamp(event_time),
            source_ip=source_ip,
            action=data.get('eventName', 'UNKNOWN'),
            user=user,
            resource=data.get('resources', [{}])[0].get('ARN') if data.get('resources') else None,
            api_call=data.get('eventName'),
        )
    
    def _normalize_iam_log(self, raw_log: Dict[str, Any]) -> NormalizedLogEntry:
        """Normalize IAM activity log format"""
        # Handle nested raw_data structure
        data = raw_log.get('raw_data', raw_log)
        
        # Handle nested user identity for IAM logs
        user_identity = data.get('userIdentity', {})
        user = user_identity.get('userName') or user_identity.get('type', '')
        
        return NormalizedLogEntry(
            timestamp=self._parse_timestamp(raw_log.get('timestamp', data.get('eventTime'))),
            source_ip=data.get('sourceIPAddress', raw_log.get('source_ip', '')),
            action=data.get('eventName', raw_log.get('action', 'UNKNOWN')),
            user=user,
            resource=data.get('resource', data.get('arn')),
            api_call=data.get('eventName', raw_log.get('api_call')),
        )
    
    def _parse_timestamp(self, timestamp_value: Any) -> datetime:
        """Parse various timestamp formats into datetime object"""
        if isinstance(timestamp_value, datetime):
            return timestamp_value
        
        if isinstance(timestamp_value, (int, float)):
            return datetime.fromtimestamp(timestamp_value)
        
        if isinstance(timestamp_value, str):
            # Try common timestamp formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO format with microseconds
                '%Y-%m-%dT%H:%M:%SZ',     # ISO format
                '%Y-%m-%d %H:%M:%S',      # Simple format
                '%Y-%m-%dT%H:%M:%S.%f',   # ISO without Z
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_value, fmt)
                except ValueError:
                    continue
            
            # Try parsing as Unix timestamp string
            try:
                return datetime.fromtimestamp(float(timestamp_value))
            except (ValueError, TypeError):
                pass
        
        # Default to current time if parsing fails
        return datetime.now()
    
    def _protocol_number_to_name(self, protocol: Any) -> Optional[str]:
        """Convert protocol number to name"""
        if protocol is None or protocol == '-':
            return None
        
        protocol_map = {
            '1': 'ICMP',
            '6': 'TCP',
            '17': 'UDP',
            '47': 'GRE',
            '50': 'ESP',
            '51': 'AH',
        }
        
        return protocol_map.get(str(protocol), str(protocol))
    
    def _normalize_waf_log(self, raw_log: Dict[str, Any]) -> NormalizedLogEntry:
        """Normalize AWS WAF log format"""
        data = raw_log.get('raw_data', raw_log)
        
        return NormalizedLogEntry(
            timestamp=self._parse_timestamp(raw_log.get('timestamp', data.get('timestamp'))),
            source_ip=data.get('httpRequest', {}).get('clientIP', ''),
            destination_ip=None,
            port=None,
            protocol=data.get('httpRequest', {}).get('httpMethod', 'HTTP'),
            action=data.get('action', 'UNKNOWN').upper(),
            user=None,
            resource=data.get('httpRequest', {}).get('uri', ''),
            api_call=f"{data.get('httpRequest', {}).get('httpMethod', '')} {data.get('httpRequest', {}).get('uri', '')}",
        )
    
    def _normalize_alb_log(self, raw_log: Dict[str, Any]) -> NormalizedLogEntry:
        """Normalize Application Load Balancer log format"""
        data = raw_log.get('raw_data', raw_log)
        
        # ALB logs are typically space-separated
        if isinstance(data.get('message'), str):
            fields = data['message'].split()
            if len(fields) >= 12:
                return NormalizedLogEntry(
                    timestamp=self._parse_timestamp(fields[1]),
                    source_ip=fields[3].split(':')[0] if ':' in fields[3] else fields[3],
                    destination_ip=fields[4].split(':')[0] if ':' in fields[4] else fields[4],
                    port=int(fields[4].split(':')[1]) if ':' in fields[4] else None,
                    protocol='HTTP',
                    action=f"HTTP {fields[8]}",  # response code
                    resource=fields[12] if len(fields) > 12 else None,
                )
        
        return NormalizedLogEntry(
            timestamp=self._parse_timestamp(raw_log.get('timestamp', data.get('timestamp'))),
            source_ip=data.get('client_ip', ''),
            destination_ip=data.get('target_ip'),
            port=data.get('target_port'),
            protocol='HTTP',
            action=f"HTTP {data.get('response_code', 'UNKNOWN')}",
            resource=data.get('request_url'),
        )
    
    def _normalize_cloudfront_log(self, raw_log: Dict[str, Any]) -> NormalizedLogEntry:
        """Normalize CloudFront log format"""
        data = raw_log.get('raw_data', raw_log)
        
        return NormalizedLogEntry(
            timestamp=self._parse_timestamp(raw_log.get('timestamp', data.get('timestamp'))),
            source_ip=data.get('c-ip', data.get('client_ip', '')),
            destination_ip=None,
            port=None,
            protocol='HTTP',
            action=f"HTTP {data.get('sc-status', 'UNKNOWN')}",
            resource=data.get('cs-uri-stem', data.get('uri')),
            api_call=f"{data.get('cs-method', '')} {data.get('cs-uri-stem', '')}",
        )
    
    def _normalize_lambda_log(self, raw_log: Dict[str, Any]) -> NormalizedLogEntry:
        """Normalize AWS Lambda log format"""
        data = raw_log.get('raw_data', raw_log)
        
        return NormalizedLogEntry(
            timestamp=self._parse_timestamp(raw_log.get('timestamp', data.get('timestamp'))),
            source_ip=data.get('sourceIPAddress', ''),
            action=data.get('eventName', 'LAMBDA_EXECUTION'),
            user=data.get('userIdentity', {}).get('userName') if isinstance(data.get('userIdentity'), dict) else None,
            resource=data.get('functionName', data.get('resource')),
            api_call=data.get('eventName'),
        )
    
    def _normalize_api_gateway_log(self, raw_log: Dict[str, Any]) -> NormalizedLogEntry:
        """Normalize API Gateway log format"""
        data = raw_log.get('raw_data', raw_log)
        
        return NormalizedLogEntry(
            timestamp=self._parse_timestamp(raw_log.get('timestamp', data.get('requestTime'))),
            source_ip=data.get('sourceIp', data.get('identity', {}).get('sourceIp', '')),
            action=f"{data.get('httpMethod', 'UNKNOWN')} {data.get('status', '')}",
            user=data.get('identity', {}).get('user') if isinstance(data.get('identity'), dict) else None,
            resource=data.get('resourcePath', data.get('path')),
            api_call=f"{data.get('httpMethod', '')} {data.get('resourcePath', '')}",
        )

    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to int, return None if not possible"""
        if value is None or value == '-':
            return None
        
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def create_basic_normalized_entry(self, raw_data: Dict[str, Any]) -> NormalizedLogEntry:
        """Create a basic normalized entry for fallback processing"""
        return NormalizedLogEntry(
            timestamp=self._parse_timestamp(raw_data.get('timestamp')),
            source_ip=raw_data.get('source_ip', raw_data.get('srcaddr', '')),
            destination_ip=raw_data.get('destination_ip', raw_data.get('dstaddr')),
            port=self._safe_int(raw_data.get('port', raw_data.get('dstport'))),
            protocol=raw_data.get('protocol'),
            action=str(raw_data.get('action', 'UNKNOWN')).upper(),
            user=raw_data.get('user', raw_data.get('userName')),
            resource=raw_data.get('resource'),
            api_call=raw_data.get('api_call', raw_data.get('eventName')),
        )