"""Integration tests for ML Engine with other components"""

import pytest
from datetime import datetime
from typing import List

from src.securon.ml_engine import create_ml_engine
from src.securon.log_processor import BatchProcessor
from src.securon.interfaces.core_types import CloudLog, LogSource


class TestMLIntegration:
    """Test ML Engine integration with other components"""
    
    @pytest.mark.asyncio
    async def test_ml_engine_with_batch_processor(self):
        """Test ML Engine working with batch processed logs"""
        # Create batch processor
        batch_processor = BatchProcessor()
        
        # Sample log data that would come from batch processing
        log_data = [
            {
                "timestamp": "2024-01-01T10:00:00Z",
                "source": "VPC_FLOW",
                "srcaddr": "192.168.1.1",
                "dstaddr": "10.0.0.1",
                "srcport": "80",
                "dstport": "443",
                "protocol": "6",
                "action": "ACCEPT"
            },
            {
                "timestamp": "2024-01-01T10:01:00Z", 
                "source": "VPC_FLOW",
                "srcaddr": "192.168.1.2",
                "dstaddr": "10.0.0.2",
                "srcport": "22",  # SSH - potentially anomalous
                "dstport": "22",
                "protocol": "6",
                "action": "REJECT"
            }
        ]
        
        # Process logs through batch processor
        processed_logs = []
        async for batch in batch_processor.process_logs_from_data(log_data, LogSource.VPC_FLOW):
            processed_logs.extend(batch)
        
        # Verify we got CloudLog objects
        assert len(processed_logs) == 2
        assert all(isinstance(log, CloudLog) for log in processed_logs)
        
        # Create ML Engine and process the logs
        ml_engine = create_ml_engine(contamination=0.3)  # Higher contamination for small dataset
        anomalies = await ml_engine.process_logs(processed_logs)
        
        # Should be able to process without errors
        assert isinstance(anomalies, list)
        # With only 2 logs, anomaly detection might not find anything, but should not error
        
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow from log processing to rule generation"""
        # Create components
        batch_processor = BatchProcessor()
        ml_engine = create_ml_engine(contamination=0.2)
        
        # Simulate larger dataset for better anomaly detection
        log_data = []
        base_timestamp = "2024-01-01T10:00:00Z"
        
        # Normal logs
        for i in range(15):
            log_data.append({
                "timestamp": f"2024-01-01T10:{i:02d}:00Z",
                "source": "VPC_FLOW",
                "srcaddr": f"192.168.1.{i % 5 + 1}",
                "dstaddr": f"10.0.0.{i % 3 + 1}",
                "srcport": str(80 + (i % 3)),
                "dstport": "443",
                "protocol": "6",
                "action": "ACCEPT"
            })
            
        # Anomalous logs
        log_data.extend([
            {
                "timestamp": "2024-01-01T03:00:00Z",  # Unusual time
                "source": "VPC_FLOW",
                "srcaddr": "192.168.1.100",
                "dstaddr": "10.0.0.100",
                "srcport": "22",  # SSH
                "dstport": "22",
                "protocol": "6",
                "action": "REJECT"
            },
            {
                "timestamp": "2024-01-01T02:30:00Z",  # Unusual time
                "source": "CLOUDTRAIL",
                "eventName": "DeleteUser",
                "sourceIPAddress": "192.168.1.200",
                "userIdentity": {"type": "IAMUser", "userName": "admin"}
            }
        ])
        
        # Step 1: Process logs
        processed_logs = []
        async for batch in batch_processor.process_logs_from_data(log_data, LogSource.VPC_FLOW):
            processed_logs.extend(batch)
        assert len(processed_logs) > 0
        
        # Step 2: Detect anomalies
        anomalies = await ml_engine.process_logs(processed_logs)
        
        # Step 3: Generate candidate rules (if anomalies found)
        if anomalies:
            candidate_rules = ml_engine.generate_candidate_rules(anomalies)
            assert isinstance(candidate_rules, list)
            
            # Step 4: Generate explanations
            for anomaly in anomalies[:2]:  # Test first 2
                explanation = ml_engine.explain_anomaly(anomaly)
                assert explanation.summary is not None
                assert explanation.risk_level is not None
                assert len(explanation.recommended_actions) > 0
        
        # Workflow should complete without errors
        assert True