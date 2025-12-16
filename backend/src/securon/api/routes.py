"""API routes for Securon Platform web interface"""

import os
import tempfile
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Request
from fastapi.responses import JSONResponse

from ..interfaces import *
from ..platform.orchestrator import PlatformOrchestrator

router = APIRouter()


def get_platform(request: Request) -> PlatformOrchestrator:
    """Get platform orchestrator from request state"""
    platform = getattr(request.app.state, 'platform', None)
    if not platform or not platform.initialized:
        raise HTTPException(status_code=503, detail="Platform not initialized")
    return platform


@router.post("/api/logs/upload")
async def upload_logs(request: Request, files: List[UploadFile] = File(...)):
    """Upload and process cloud logs for ML analysis"""
    platform = get_platform(request)
    
    try:
        all_logs = []
        
        for file in files:
            if not file.filename:
                raise HTTPException(status_code=400, detail="File must have a name")
            
            # Read file content
            content = await file.read()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix='.json') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Process logs using batch processor
                log_processor = platform.get_log_processor()
                logs = await log_processor.process_file(temp_file_path)
                all_logs.extend(logs)
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
        
        # Process logs through the complete workflow
        result = await platform.process_logs_workflow(all_logs)
        
        return {
            "message": f"Successfully processed {result['logs_processed']} log entries",
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing logs: {str(e)}")


@router.get("/api/anomalies")
async def get_anomalies():
    """Get all detected anomalies with explanations"""
    try:
        # This would typically come from a database or cache
        # For now, return empty list as anomalies are returned during upload
        return {"anomalies": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving anomalies: {str(e)}")


@router.get("/api/anomalies/{anomaly_id}/explanation")
async def get_anomaly_explanation(anomaly_id: str):
    """Get detailed explanation for a specific anomaly"""
    try:
        # This would typically retrieve the anomaly from storage
        # For now, return a placeholder response
        return {
            "anomaly_id": anomaly_id,
            "explanation": {
                "summary": "Anomaly explanation not available",
                "technical_details": "Detailed analysis not available",
                "risk_level": "MEDIUM",
                "recommended_actions": ["Review the anomaly manually"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving explanation: {str(e)}")


@router.get("/api/rules")
async def get_rules(request: Request):
    """Get all security rules (active and candidate)"""
    platform = get_platform(request)
    
    try:
        rule_engine = platform.get_rule_engine()
        active_rules = await rule_engine.get_active_rules()
        candidate_rules = await rule_engine.get_candidate_rules()
        
        return {
            "active_rules": [rule.dict() for rule in active_rules],
            "candidate_rules": [rule.dict() for rule in candidate_rules]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving rules: {str(e)}")


@router.post("/api/rules/{rule_id}/approve")
async def approve_rule(request: Request, rule_id: str):
    """Approve a candidate security rule"""
    platform = get_platform(request)
    
    try:
        rule_engine = platform.get_rule_engine()
        await rule_engine.approve_candidate_rule(rule_id)
        return {"message": f"Rule {rule_id} approved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving rule: {str(e)}")


@router.post("/api/rules/{rule_id}/reject")
async def reject_rule(request: Request, rule_id: str):
    """Reject a candidate security rule"""
    platform = get_platform(request)
    
    try:
        rule_engine = platform.get_rule_engine()
        await rule_engine.reject_candidate_rule(rule_id)
        return {"message": f"Rule {rule_id} rejected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting rule: {str(e)}")


@router.post("/api/iac/scan")
async def scan_iac_code(request: Request, files: List[UploadFile] = File(...)):
    """Scan uploaded Terraform files for security misconfigurations"""
    platform = get_platform(request)
    
    try:
        all_results = []
        
        for file in files:
            if not file.filename:
                raise HTTPException(status_code=400, detail="File must have a name")
            
            # Read file content
            content = await file.read()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.tf') as temp_file:
                temp_file.write(content.decode('utf-8'))
                temp_file_path = temp_file.name
            
            try:
                # Scan using the platform workflow
                results = await platform.scan_iac_workflow(temp_file_path)
                
                # Add filename to results
                for result in results:
                    result.file_path = file.filename
                
                all_results.extend(results)
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
        
        return {
            "message": f"Successfully scanned {len(files)} files",
            "files_scanned": len(files),
            "issues_found": len(all_results),
            "results": [result.dict() for result in all_results]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning IaC files: {str(e)}")


@router.post("/api/iac/scan-text")
async def scan_iac_text(request: Request, terraform_code: str = Form(...)):
    """Scan Terraform code provided as text"""
    platform = get_platform(request)
    
    try:
        # Create temporary file with the code
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.tf') as temp_file:
            temp_file.write(terraform_code)
            temp_file_path = temp_file.name
        
        try:
            # Scan using the platform workflow
            results = await platform.scan_iac_workflow(temp_file_path)
            
            return {
                "message": "Successfully scanned Terraform code",
                "issues_found": len(results),
                "results": [result.dict() for result in results]
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning Terraform code: {str(e)}")