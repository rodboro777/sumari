from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Dict, Optional
from datetime import datetime, timedelta
import json
import time
import psutil

from .metrics_collector import metrics_collector

metrics_router = APIRouter(prefix="/metrics", tags=["metrics"])

# Middleware function to track Cloud Run metrics
async def track_cloud_run_metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time
    
    # Get instance metrics
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    # Track metrics
    metrics_collector.log_cloud_run_metrics(
        instance_count=1,  # Single instance for now
        request_count=1,
        memory_usage=memory_usage,
        cpu_usage=cpu_usage,
        latency=latency
    )
    
    return response

@metrics_router.get("/performance")
async def get_performance_metrics() -> Dict:
    """Get current performance metrics including DistilBERT and processing stats"""
    # Get Cloud Run metrics
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    stats = metrics_collector.get_performance_stats()
    stats["cloud_run"] = {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "instance_count": 1  # Single instance for now
    }
    
    return stats

@metrics_router.get("/api")
async def get_api_metrics(
    include_conversions: bool = Query(True, description="Include user conversion metrics"),
    include_firestore: bool = Query(True, description="Include Firestore metrics"),
    include_cloud_run: bool = Query(True, description="Include Cloud Run metrics"),
    include_tts: bool = Query(True, description="Include TTS metrics")
) -> Dict:
    """Get comprehensive API and usage metrics"""
    stats = metrics_collector.get_api_stats()
    
    # Filter metrics based on query parameters
    if not include_conversions and "conversions" in stats:
        del stats["conversions"]
    if not include_firestore and "firestore" in stats:
        del stats["firestore"]
    if not include_cloud_run and "cloud_run" in stats:
        del stats["cloud_run"]
    if not include_tts and "tts" in stats:
        del stats["tts"]
    
    return stats

@metrics_router.get("/logs")
async def get_recent_logs(
    limit: int = Query(100, description="Number of log entries to return"),
    type: Optional[str] = Query(None, description="Filter logs by type (e.g., 'conversion', 'firestore', 'tts')"),
    hours: Optional[int] = Query(None, description="Filter logs from last N hours")
) -> Dict:
    """Get recent log entries with optional filtering"""
    try:
        with open("data/metrics.jsonl", "r") as f:
            logs = [json.loads(line) for line in f.readlines()]
        
        # Apply time filter if specified
        if hours:
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            logs = [log for log in logs if log.get("timestamp", "") >= cutoff]
        
        # Apply type filter if specified
        if type:
            logs = [log for log in logs if type in log.get("message", "").lower()]
        
        # Apply limit after filtering
        logs = logs[-limit:]
        
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@metrics_router.get("/conversions")
async def get_conversion_metrics(
    days: int = Query(30, description="Number of days to analyze")
) -> Dict:
    """Get detailed user conversion metrics"""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    try:
        with open("data/metrics.jsonl", "r") as f:
            logs = [json.loads(line) for line in f.readlines()]
        
        # Filter conversion logs
        conversion_logs = [
            log for log in logs 
            if "conversion" in log.get("message", "").lower() 
            and log.get("timestamp", "") >= cutoff
        ]
        
        # Calculate conversion rates
        conversions = {
            "free_to_basic": 0,
            "free_to_pro": 0,
            "basic_to_pro": 0
        }
        
        for log in conversion_logs:
            msg = log.get("message", {})
            if isinstance(msg, str):
                msg = json.loads(msg)
            
            conversion_type = f"{msg.get('from_tier', '')}_to_{msg.get('to_tier', '')}"
            if conversion_type in conversions:
                conversions[conversion_type] += 1
        
        return {
            "period_days": days,
            "total_conversions": sum(conversions.values()),
            "conversion_breakdown": conversions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
