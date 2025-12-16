"""ML Engine demonstration script"""

import asyncio
from datetime import datetime, timedelta
from typing import List

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from securon.ml_engine import create_ml_engine
from securon.interfaces.core_types import (
    CloudLog, LogSource, NormalizedLogEntry
)


def create_demo_logs() -> List[CloudLog]:
    """Create demonstration logs with normal and anomalous patterns"""
    logs = []
    base_time = datetime.now()
    
    # Normal VPC Flow logs
    for i in range(20):
        log = CloudLog(
            timestamp=base_time + timedelta(minutes=i),
            source=LogSource.VPC_FLOW,
            raw_data={"message": f"Normal traffic {i}"},
            normalized_data=NormalizedLogEntry(
                timestamp=base_time + timedelta(minutes=i),
                source_ip=f"192.168.1.{i % 10 + 1}",
                destination_ip=f"10.0.0.{i % 5 + 1}",
                port=80 + (i % 3),  # Ports 80, 81, 82
                protocol="TCP",
                action="ACCEPT",
                user=f"user_{i % 3}",
                resource=f"web_server_{i % 2}",
                api_call="GET"
            )
        )
        logs.append(log)
    
    # Anomalous logs - Port scan
    port_scan_log = CloudLog(
        timestamp=base_time + timedelta(hours=3),  # Unusual time
        source=LogSource.VPC_FLOW,
        raw_data={"message": "Suspicious port access"},
        normalized_data=NormalizedLogEntry(
            timestamp=base_time + timedelta(hours=3),
            source_ip="192.168.1.100",
            destination_ip="10.0.0.100",
            port=22,  # SSH port - unusual
            protocol="TCP",
            action="REJECT",
            user="unknown_user",
            resource="critical_server",
            api_call="SSH_CONNECT"
        )
    )
    logs.append(port_scan_log)
    
    # Anomalous logs - Brute force
    brute_force_log = CloudLog(
        timestamp=base_time + timedelta(hours=2, minutes=30),
        source=LogSource.IAM,
        raw_data={"message": "Authentication failure"},
        normalized_data=NormalizedLogEntry(
            timestamp=base_time + timedelta(hours=2, minutes=30),
            source_ip="192.168.1.200",
            port=443,
            protocol="HTTPS",
            action="failed_login",
            user="admin",
            resource="auth_service",
            api_call="authenticate"
        )
    )
    logs.append(brute_force_log)
    
    # Anomalous logs - Unusual API
    unusual_api_log = CloudLog(
        timestamp=base_time + timedelta(hours=1),
        source=LogSource.CLOUDTRAIL,
        raw_data={"message": "Administrative action"},
        normalized_data=NormalizedLogEntry(
            timestamp=base_time + timedelta(hours=1),
            source_ip="192.168.1.150",
            port=443,
            protocol="HTTPS",
            action="API_CALL",
            user="service_account",
            resource="user_management",
            api_call="DeleteUser"
        )
    )
    logs.append(unusual_api_log)
    
    return logs


async def main():
    """Main demonstration function"""
    print("=== Securon ML Engine Demonstration ===\n")
    
    # Create ML Engine
    print("1. Creating ML Engine with Isolation Forest...")
    ml_engine = create_ml_engine(contamination=0.15, random_state=42)
    print("   ✓ ML Engine created successfully\n")
    
    # Create demo logs
    print("2. Creating demonstration logs...")
    logs = create_demo_logs()
    print(f"   ✓ Created {len(logs)} logs ({len(logs)-3} normal, 3 anomalous)\n")
    
    # Process logs for anomalies
    print("3. Processing logs for anomaly detection...")
    anomalies = await ml_engine.process_logs(logs)
    print(f"   ✓ Detected {len(anomalies)} anomalies\n")
    
    # Display anomaly details
    if anomalies:
        print("4. Anomaly Analysis:")
        for i, anomaly in enumerate(anomalies, 1):
            print(f"\n   Anomaly {i}:")
            print(f"   - ID: {anomaly.id}")
            print(f"   - Type: {anomaly.type.value}")
            print(f"   - Severity: {anomaly.severity:.3f}")
            print(f"   - Confidence: {anomaly.confidence:.3f}")
            print(f"   - Affected Resources: {', '.join(anomaly.affected_resources)}")
            print(f"   - Time Window: {anomaly.time_window.start.strftime('%H:%M:%S')} - {anomaly.time_window.end.strftime('%H:%M:%S')}")
            
            # Show patterns
            print(f"   - Detected Patterns:")
            for pattern in anomaly.patterns:
                print(f"     * {pattern.feature}: Expected {pattern.expected_range}, Got {pattern.actual_value:.2f}")
    
    # Generate candidate rules
    if anomalies:
        print("\n5. Generating candidate security rules...")
        candidate_rules = ml_engine.generate_candidate_rules(anomalies)
        print(f"   ✓ Generated {len(candidate_rules)} candidate rules\n")
        
        print("   Candidate Rules:")
        for i, rule in enumerate(candidate_rules, 1):
            print(f"\n   Rule {i}:")
            print(f"   - Name: {rule.name}")
            print(f"   - Description: {rule.description}")
            print(f"   - Severity: {rule.severity.value}")
            print(f"   - Pattern: {rule.pattern}")
            print(f"   - Status: {rule.status.value}")
            print(f"   - Remediation: {rule.remediation}")
    
    # Generate explanations
    if anomalies:
        print("\n6. Generating anomaly explanations...")
        for i, anomaly in enumerate(anomalies[:2], 1):  # Show first 2 explanations
            explanation = ml_engine.explain_anomaly(anomaly)
            print(f"\n   Explanation for Anomaly {i}:")
            print(f"   - Summary: {explanation.summary}")
            print(f"   - Risk Level: {explanation.risk_level.value}")
            print(f"   - Recommended Actions:")
            for action in explanation.recommended_actions[:3]:  # Show first 3 actions
                print(f"     * {action}")
    
    print("\n=== Demonstration Complete ===")


if __name__ == "__main__":
    asyncio.run(main())