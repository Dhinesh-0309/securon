"""Batch processing functionality for handling large log datasets"""

import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
import json

from ..interfaces.core_types import CloudLog, LogSource
from .normalizer import LogNormalizer
from .validator import LogValidator


class BatchProcessor:
    """Handles batch processing of large log datasets with memory management"""
    
    def __init__(self, batch_size: int = 1000, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.normalizer = LogNormalizer()
        self.validator = LogValidator()
    
    async def process_logs_from_file(
        self, 
        file_path: str, 
        source: LogSource,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> AsyncGenerator[List[CloudLog], None]:
        """
        Process logs from a file in batches
        Yields batches of processed CloudLog objects
        """
        total_processed = 0
        
        async for batch in self._read_file_in_batches(file_path):
            processed_batch = await self._process_batch(batch, source)
            total_processed += len(processed_batch)
            
            if progress_callback:
                progress_callback(total_processed, len(processed_batch))
            
            yield processed_batch
    
    async def process_logs_from_data(
        self,
        logs: List[Dict[str, Any]],
        source: LogSource,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> AsyncGenerator[List[CloudLog], None]:
        """
        Process logs from in-memory data in batches
        Yields batches of processed CloudLog objects
        """
        total_processed = 0
        
        for i in range(0, len(logs), self.batch_size):
            batch = logs[i:i + self.batch_size]
            processed_batch = await self._process_batch(batch, source)
            total_processed += len(processed_batch)
            
            if progress_callback:
                progress_callback(total_processed, len(processed_batch))
            
            yield processed_batch
    
    async def _process_batch(self, batch: List[Dict[str, Any]], source: LogSource) -> List[CloudLog]:
        """Process a single batch of logs"""
        # Run validation and normalization in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Validate logs
            valid_logs, validation_errors = await loop.run_in_executor(
                executor, self.validator.validate_raw_logs, batch, source
            )
            
            if validation_errors:
                print(f"Validation errors in batch: {len(validation_errors)} errors")
            
            # Normalize valid logs
            if valid_logs:
                normalized_logs = await loop.run_in_executor(
                    executor, self.normalizer.normalize_logs, valid_logs, source
                )
                
                # Final validation of normalized logs
                final_logs, final_errors = await loop.run_in_executor(
                    executor, self.validator.validate_normalized_logs, normalized_logs
                )
                
                if final_errors:
                    print(f"Final validation errors: {len(final_errors)} errors")
                
                return final_logs
            
            return []
    
    async def _read_file_in_batches(self, file_path: str) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """Read a file in batches to manage memory usage"""
        batch = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                
                # Try to parse entire content as JSON first (for JSON arrays)
                try:
                    json_data = json.loads(content)
                    
                    # Handle JSON array
                    if isinstance(json_data, list):
                        for log_entry in json_data:
                            batch.append(log_entry)
                            if len(batch) >= self.batch_size:
                                yield batch
                                batch = []
                    # Handle single JSON object
                    elif isinstance(json_data, dict):
                        batch.append(json_data)
                    
                except json.JSONDecodeError:
                    # Handle line-by-line format (JSONL or plain text)
                    for line_num, line in enumerate(content.split('\n'), 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            # Try to parse as JSON line
                            log_entry = json.loads(line)
                            batch.append(log_entry)
                            
                        except json.JSONDecodeError:
                            # Handle non-JSON formats (like VPC Flow Logs)
                            log_entry = {'message': line, 'line_number': line_num}
                            batch.append(log_entry)
                        
                        if len(batch) >= self.batch_size:
                            yield batch
                            batch = []
                        
                        if len(batch) >= self.batch_size:
                            yield batch
                            batch = []
                
                # Yield remaining logs
                if batch:
                    yield batch
                    
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading log file {file_path}: {str(e)}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            'batch_size': self.batch_size,
            'max_workers': self.max_workers,
        }
    
    async def process_all_logs(
        self,
        logs: List[Dict[str, Any]],
        source: LogSource,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[CloudLog]:
        """
        Process all logs and return complete result list
        Use with caution for large datasets as it loads everything into memory
        """
        all_processed_logs = []
        
        async for batch in self.process_logs_from_data(logs, source, progress_callback):
            all_processed_logs.extend(batch)
        
        return all_processed_logs


class BatchLogProcessor:
    """Simplified interface for log processing in API"""
    
    def __init__(self):
        self.processor = BatchProcessor()
        self.normalizer = LogNormalizer()
    
    async def process_file(self, file_path: str) -> List[CloudLog]:
        """Process a log file and return all processed logs"""
        try:
            # Try to detect log source from file content
            source = await self._detect_log_source(file_path)
            
            all_logs = []
            async for batch in self.processor.process_logs_from_file(file_path, source):
                all_logs.extend(batch)
            
            return all_logs
        except Exception as e:
            # Fallback: create basic CloudLog entries
            return await self._create_fallback_logs(file_path)
    
    async def _detect_log_source(self, file_path: str) -> LogSource:
        """Detect log source from file content"""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                
                # Try to parse as JSON first
                if content.startswith('[') or content.startswith('{'):
                    try:
                        data = json.loads(content)
                        if isinstance(data, list) and len(data) > 0:
                            first_entry = data[0]
                        else:
                            first_entry = data
                        
                        # Check the source field or content
                        if isinstance(first_entry, dict):
                            source = first_entry.get('source', '').upper()
                            if source in ['VPC_FLOW', 'CLOUDTRAIL', 'IAM', 'WAF', 'ALB', 'CLOUDFRONT', 'LAMBDA', 'API_GATEWAY']:
                                return LogSource[source]
                            
                            # Check raw_data for indicators
                            raw_data = first_entry.get('raw_data', {})
                            if 'srcaddr' in raw_data or 'dstaddr' in raw_data:
                                return LogSource.VPC_FLOW
                            elif 'eventName' in raw_data or 'eventSource' in raw_data:
                                return LogSource.CLOUDTRAIL
                            elif 'userIdentity' in raw_data:
                                return LogSource.IAM
                            elif 'httpRequest' in raw_data or 'action' in raw_data:
                                return LogSource.WAF
                            elif 'client_ip' in raw_data or 'target_ip' in raw_data:
                                return LogSource.ALB
                            elif 'c-ip' in raw_data or 'cs-method' in raw_data:
                                return LogSource.CLOUDFRONT
                            elif 'functionName' in raw_data:
                                return LogSource.LAMBDA
                            elif 'httpMethod' in raw_data or 'resourcePath' in raw_data:
                                return LogSource.API_GATEWAY
                    except json.JSONDecodeError:
                        pass
                
                # Fallback to text-based detection
                if 'vpc-flow' in content.lower() or 'srcaddr' in content.lower():
                    return LogSource.VPC_FLOW
                elif 'cloudtrail' in content.lower() or 'eventName' in content.lower():
                    return LogSource.CLOUDTRAIL
                elif 'iam' in content.lower() or 'userIdentity' in content.lower():
                    return LogSource.IAM
                else:
                    return LogSource.VPC_FLOW  # Default
        except:
            return LogSource.VPC_FLOW  # Default fallback
    
    async def _create_fallback_logs(self, file_path: str) -> List[CloudLog]:
        """Create basic CloudLog entries as fallback"""
        logs = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        # Try to parse as JSON
                        raw_data = json.loads(line)
                    except json.JSONDecodeError:
                        # Create basic structure for non-JSON
                        raw_data = {'message': line, 'line_number': line_num}
                    
                    # Create normalized entry
                    normalized_data = self.normalizer.create_basic_normalized_entry(raw_data)
                    
                    log = CloudLog(
                        timestamp=normalized_data.timestamp,
                        source=LogSource.VPC_FLOW,  # Default
                        raw_data=raw_data,
                        normalized_data=normalized_data
                    )
                    logs.append(log)
        except Exception as e:
            print(f"Error creating fallback logs: {e}")
        
        return logs