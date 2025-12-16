#!/usr/bin/env python3
"""
Demo script showing log processing functionality
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from securon.interfaces.core_types import LogSource
from securon.log_processor import LogNormalizer, LogValidator, BatchProcessor


async def demo_log_processing():
    """Demonstrate log processing capabilities"""
    
    print("=== Securon Log Processing Demo ===\n")
    
    # Sample log data for different sources
    vpc_flow_logs = [
        {
            'message': '2 123456789012 eni-1235b8ca 192.168.1.100 10.0.0.50 49152 22 6 20 4249 1418530010 1418530070 ACCEPT OK'
        },
        {
            'srcaddr': '192.168.1.200',
            'dstaddr': '10.0.0.100',
            'dstport': 443,
            'protocol': '6',
            'action': 'ACCEPT',
            'timestamp': '2023-01-01T12:00:00Z'
        }
    ]
    
    cloudtrail_logs = [
        {
            'eventTime': '2023-01-01T12:00:00Z',
            'eventName': 'CreateUser',
            'sourceIPAddress': '203.0.113.1',
            'userIdentity': {
                'type': 'IAMUser',
                'userName': 'admin'
            },
            'resources': [{
                'ARN': 'arn:aws:iam::123456789012:user/newuser'
            }]
        }
    ]
    
    iam_logs = [
        {
            'timestamp': '2023-01-01T12:05:00Z',
            'eventName': 'AssumeRole',
            'sourceIPAddress': '192.168.1.50',
            'userName': 'service-account',
            'resource': 'arn:aws:iam::123456789012:role/ServiceRole'
        }
    ]
    
    # Initialize components
    normalizer = LogNormalizer()
    validator = LogValidator()
    batch_processor = BatchProcessor(batch_size=10)
    
    # Process each log type
    log_types = [
        (vpc_flow_logs, LogSource.VPC_FLOW, "VPC Flow Logs"),
        (cloudtrail_logs, LogSource.CLOUDTRAIL, "CloudTrail Logs"),
        (iam_logs, LogSource.IAM, "IAM Logs")
    ]
    
    for logs, source, name in log_types:
        print(f"Processing {name}:")
        print(f"  Raw logs: {len(logs)}")
        
        # Validate raw logs
        valid_logs, errors = validator.validate_raw_logs(logs, source)
        print(f"  Valid logs after validation: {len(valid_logs)}")
        if errors:
            print(f"  Validation errors: {len(errors)}")
        
        # Normalize logs
        normalized_logs = normalizer.normalize_logs(valid_logs, source)
        print(f"  Normalized logs: {len(normalized_logs)}")
        
        # Show sample normalized log
        if normalized_logs:
            sample = normalized_logs[0]
            print(f"  Sample normalized log:")
            print(f"    Source IP: {sample.normalized_data.source_ip}")
            print(f"    Action: {sample.normalized_data.action}")
            print(f"    Timestamp: {sample.normalized_data.timestamp}")
            if sample.normalized_data.destination_ip:
                print(f"    Destination IP: {sample.normalized_data.destination_ip}")
            if sample.normalized_data.port:
                print(f"    Port: {sample.normalized_data.port}")
            if sample.normalized_data.protocol:
                print(f"    Protocol: {sample.normalized_data.protocol}")
        
        print()
    
    # Demonstrate batch processing
    print("Batch Processing Demo:")
    all_logs = vpc_flow_logs + cloudtrail_logs + iam_logs
    
    def progress_callback(total_processed, batch_size):
        print(f"  Processed {total_processed} logs (batch size: {batch_size})")
    
    # Process all logs using batch processor
    processed_logs = await batch_processor.process_all_logs(
        all_logs, 
        LogSource.VPC_FLOW,  # Using VPC_FLOW as example
        progress_callback
    )
    
    print(f"  Total processed logs: {len(processed_logs)}")
    
    # Show processing stats
    stats = batch_processor.get_processing_stats()
    print(f"  Batch processor stats: {stats}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(demo_log_processing())