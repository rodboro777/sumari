from typing import Dict, Optional 
from datetime import datetime
from google.cloud import monitoring_v3
from google.api import metric_pb2
from src.config import GCP_PROJECT_ID
import logging
import numpy as np

class MetricsCollector:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(MetricsCollector, cls).__new__(cls)
        return cls.instance

    def __init__(self):

        """Initialize metrics collector."""
        self.user_conversions = []
        self.firestore_metrics = []
        self.cloud_run_metrics = []
        self.tts_metrics = []
        self.processing_metrics = []
        
        # Initialize Cloud Monitoring client
        self.client = monitoring_v3.MetricServiceClient()
        self.project_path = f"projects/{GCP_PROJECT_ID}"
        
        # Create custom metric descriptors if they don't exist
        self._create_metric_descriptors()

    def _create_metric_descriptors(self):
        """Create custom metric descriptors in Cloud Monitoring."""
        descriptors = {
            'custom.googleapis.com/sumari/user_conversions': {
                'metric_kind': metric_pb2.MetricDescriptor.MetricKind.GAUGE,
                'value_type': metric_pb2.MetricDescriptor.ValueType.INT64,
                'description': 'Number of user tier conversions'
            },
            'custom.googleapis.com/sumari/firestore_operations': {
                'metric_kind': metric_pb2.MetricDescriptor.MetricKind.GAUGE,
                'value_type': metric_pb2.MetricDescriptor.ValueType.INT64,
                'description': 'Number of Firestore operations'
            },
            'custom.googleapis.com/sumari/tts_usage': {
                'metric_kind': metric_pb2.MetricDescriptor.MetricKind.GAUGE,
                'value_type': metric_pb2.MetricDescriptor.ValueType.DOUBLE,
                'description': 'Text-to-Speech usage metrics'
            },
            'custom.googleapis.com/sumari/cloud_run_instance_count': {
                'metric_kind': metric_pb2.MetricDescriptor.MetricKind.GAUGE,
                'value_type': metric_pb2.MetricDescriptor.ValueType.DOUBLE,
                'description': 'Cloud Run instance count'
            },
            'custom.googleapis.com/sumari/cloud_run_request_count': {
                'metric_kind': metric_pb2.MetricDescriptor.MetricKind.GAUGE,
                'value_type': metric_pb2.MetricDescriptor.ValueType.DOUBLE,
                'description': 'Cloud Run request count'
            },
            'custom.googleapis.com/sumari/cloud_run_memory_usage': {
                'metric_kind': metric_pb2.MetricDescriptor.MetricKind.GAUGE,
                'value_type': metric_pb2.MetricDescriptor.ValueType.DOUBLE,
                'description': 'Cloud Run memory usage'
            },
            'custom.googleapis.com/sumari/cloud_run_cpu_usage': {
                'metric_kind': metric_pb2.MetricDescriptor.MetricKind.GAUGE,
                'value_type': metric_pb2.MetricDescriptor.ValueType.DOUBLE,
                'description': 'Cloud Run CPU usage'
            },
            'custom.googleapis.com/sumari/cloud_run_latency': {
                'display_name': 'Cloud Run Latency',
                'description': 'Cloud Run request latency',
                'metric_kind': 'GAUGE',
                'value_type': 'DOUBLE',
                'unit': 's'
            },
            'custom.googleapis.com/sumari/processing_time': {
                'display_name': 'Processing Time',
                'description': 'Text processing time by model',
                'metric_kind': 'GAUGE',
                'value_type': 'DOUBLE',
                'unit': 's'
            },
            'custom.googleapis.com/sumari/tts_char_count': {
                'metric_kind': metric_pb2.MetricDescriptor.MetricKind.GAUGE,
                'value_type': metric_pb2.MetricDescriptor.ValueType.DOUBLE,
                'description': 'TTS character count'
            },
            'custom.googleapis.com/sumari/tts_duration': {
                'metric_kind': metric_pb2.MetricDescriptor.MetricKind.GAUGE,
                'value_type': metric_pb2.MetricDescriptor.ValueType.DOUBLE,
                'description': 'TTS duration'
            },
            'custom.googleapis.com/sumari/tts_cost': {
                'metric_kind': metric_pb2.MetricDescriptor.MetricKind.GAUGE,
                'value_type': metric_pb2.MetricDescriptor.ValueType.DOUBLE,
                'description': 'TTS cost'
            }
        }
        
        for path, descriptor in descriptors.items():
            try:
                descriptor_obj = metric_pb2.MetricDescriptor(
                    type=path,
                    metric_kind=descriptor['metric_kind'],
                    value_type=descriptor['value_type'],
                    description=descriptor['description']
                )
                self.client.create_metric_descriptor(
                    name=self.project_path,
                    metric_descriptor=descriptor_obj
                )
            except Exception as e:
                # Ignore if descriptor already exists
                if 'Already exists' not in str(e):
                    print(f"Error creating metric descriptor {path}: {str(e)}")
    
    def _log_metric(self, metric_type: str, value: float, labels: Dict[str, str] = None):
        """Log a metric to Cloud Monitoring."""
        try:
            series = monitoring_v3.TimeSeries()
            series.metric.type = f"custom.googleapis.com/sumari/{metric_type}"
            if labels:
                series.metric.labels.update(labels)
            
            # Add data point
            now = datetime.utcnow()
            point = monitoring_v3.Point({"value": {"double_value": float(value)}})
            point.interval = monitoring_v3.TimeInterval(
                {"end_time": {"seconds": int(now.timestamp())}}
            )
            series.points = [point]
            
            # Write the time series data
            self.client.create_time_series(
                request={
                    "name": self.project_path,
                    "time_series": [series]
                }
            )
        except Exception as e:
            print(f"Error logging metric to Cloud Monitoring: {str(e)}")

    def log_user_conversion(self, user_id: int, from_tier: str, to_tier: str, source: str = "manual"):
        """Log a user tier conversion."""
        conversion = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "from_tier": from_tier,
            "to_tier": to_tier,
            "source": source
        }
        self.user_conversions.append(conversion)
        
        # Log to Cloud Monitoring
        self._log_metric(
            metric_type="user_conversions",
            value=1.0,
            labels={
                "from_tier": from_tier,
                "to_tier": to_tier,
                "source": source
            }
        )

    def log_firestore_operation(self, operation_type: str, collection: str, doc_count: int, success: bool, latency: float):
        """Log a Firestore operation."""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type,
            "collection": collection,
            "doc_count": doc_count,
            "success": success,
            "latency": latency
        }
        self.firestore_metrics.append(metric)
        
        # Log to Cloud Monitoring
        self._log_metric(
            metric_type="firestore_operations",
            value=latency,
            labels={
                "operation_type": operation_type,
                "collection": collection,
                "success": str(success)
            }
        )

    def log_cloud_run_metrics(self, instance_count: int, request_count: int, memory_usage: float, cpu_usage: float, latency: float):
        """Log Cloud Run metrics."""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "instance_count": instance_count,
            "request_count": request_count,
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "latency": latency
        }
        self.cloud_run_metrics.append(metric)
        
        # Log to Cloud Monitoring
        metrics = {
            "instance_count": float(instance_count),
            "request_count": float(request_count),
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "latency": latency
        }
        
        for name, value in metrics.items():
            self._log_metric(
                metric_type=f"cloud_run_{name}",
                value=value
            )

    def log_tts_usage(self, user_id: int, char_count: int, duration: float, success: bool, cost: Optional[float] = None):
        """Log Text-to-Speech usage metrics.
        
        Args:
            user_id: The ID of the user making the request
            char_count: Number of characters in the text
            duration: Duration of the generated audio in seconds
            success: Whether the TTS operation succeeded
            cost: Optional actual cost of the operation. If not provided,
                  only usage metrics will be tracked without cost estimation.
        """
        metric = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "char_count": char_count,
            "duration": duration,
            "success": success
        }
        
        # Only include cost if provided
        if cost is not None:
            metric["cost"] = cost
        
        self.tts_metrics.append(metric)
        
        # Log usage metrics to Cloud Monitoring
        self._log_metric(
            metric_type="tts_char_count",
            value=float(char_count),
            labels={
                "success": str(success),
                "user_id": str(user_id)
            }
        )
        
        self._log_metric(
            metric_type="tts_duration",
            value=duration,
            labels={
                "success": str(success),
                "user_id": str(user_id)
            }
        )
        
        # Only log cost if provided
        if cost is not None:
            self._log_metric(
                metric_type="tts_cost",
                value=cost,
                labels={
                    "success": str(success),
                    "user_id": str(user_id),
                    "cost_type": "actual"  # This was an actual measured cost
                }
            )

    def log_premium_status_change(self, user_id: int, old_tier: str, new_tier: str) -> None:
        """Log a user's premium status change.
        
        Args:
            user_id: The user's ID
            old_tier: The user's previous tier (free, based, pro)
            new_tier: The user's new tier (free, based, pro)
        """
        try:
            # Create time series for user conversion
            series = monitoring_v3.TimeSeries()
            series.metric.type = 'custom.googleapis.com/sumari/user_conversions'
            series.metric.labels.update({
                'user_id': str(user_id),
                'old_tier': old_tier,
                'new_tier': new_tier
            })
            
            # Add the data point
            now = datetime.now()
            point = monitoring_v3.Point({'value': {'int64_value': 1}})
            point.interval = monitoring_v3.TimeInterval({
                'end_time': {'seconds': int(now.timestamp())}
            })
            series.points = [point]
            
            # Write the time series
            self.client.create_time_series(
                request={
                    "name": self.project_path,
                    "time_series": [series]
                }
            )
            
            # Log the conversion
            logging.info(f"User {user_id} converted from {old_tier} to {new_tier}")
            
        except Exception as e:
            logging.error(f"Error logging premium status change: {str(e)}")
            # Don't raise the error since this is non-critical functionality

    def get_api_stats(self) -> Dict:
        """Get comprehensive API and usage statistics"""
        if not any([self.user_conversions, self.firestore_metrics,
                   self.cloud_run_metrics, self.tts_metrics]):
            return {}
        
        stats = {
            "daily": {
                "summaries": self.daily_summaries,
                "audio_minutes": self.daily_audio_minutes,
                "errors": self.daily_errors
            },
            "conversions": self.tier_conversion_counts,
            "api_performance": {},
            "firestore": {},
            "cloud_run": {},
            "tts": {}
        }
        
        # API metrics
        if self.api_metrics:
            for api_name in set(m.api_name for m in self.api_metrics):
                api_calls = [m for m in self.api_metrics if m.api_name == api_name]
                response_times = [m.response_time for m in api_calls]
                costs = [m.cost for m in api_calls]
                
                stats["api_performance"][api_name] = {
                    "calls": len(api_calls),
                    "success_rate": sum(1 for m in api_calls if m.success) / len(api_calls),
                    "response_time": {
                        "mean": np.mean(response_times),
                        "p95": np.percentile(response_times, 95)
                    },
                    "total_cost": sum(costs)
                }
        
        # Firestore metrics
        if self.firestore_metrics:
            for op_type in set(m.operation_type for m in self.firestore_metrics):
                ops = [m for m in self.firestore_metrics if m.operation_type == op_type]
                latencies = [m.latency for m in ops]
                
                stats["firestore"][op_type] = {
                    "operations": len(ops),
                    "success_rate": sum(1 for m in ops if m.success) / len(ops),
                    "latency": {
                        "mean": np.mean(latencies),
                        "p95": np.percentile(latencies, 95)
                    },
                    "total_documents": sum(m.document_count for m in ops)
                }
        
        # Cloud Run metrics
        if self.cloud_run_metrics:
            recent = list(self.cloud_run_metrics)[-1]  # Most recent metrics
            stats["cloud_run"] = {
                "current": {
                    "instances": recent.instance_count,
                    "requests": recent.request_count,
                    "memory_usage": recent.memory_usage,
                    "cpu_usage": recent.cpu_usage,
                    "latency": recent.latency
                }
            }
        
        # TTS metrics
        if self.tts_metrics:
            tts_calls = list(self.tts_metrics)
            stats["tts"] = {
                "total_calls": len(tts_calls),
                "success_rate": sum(1 for m in tts_calls if m.success) / len(tts_calls),
                "total_duration": sum(m.audio_duration for m in tts_calls),
                "total_cost": sum(m.cost for m in tts_calls),
                "average_duration": np.mean([m.audio_duration for m in tts_calls])
            }
        
        return stats

# Create a singleton instance
metrics_collector = MetricsCollector()
