# src/domain/services/config_factory.py
import os
from typing import Optional
from pydantic import HttpUrl
from setsail_workflow_py.domain.models.workflow_monitoring_config import WorkflowMonitoringConfig
from setsail_workflow_py.shared.utils import generate_span_id
from loguru import logger

class ConfigFactory:

    @staticmethod
    def create_from_trace_data(trace_data: dict, operation_name: str, log_enabled: bool = False) -> Optional[WorkflowMonitoringConfig]:
        env = os.getenv("ENV", "local")
        try:
            if env == "local":
                raw_post_url = os.getenv("WORKFLOW_MONITORING_URL", trace_data.get("post_url", "http://localhost:8000"))
            elif env == "dev":
                raw_post_url = os.getenv("WORKFLOW_MONITORING_URL", trace_data.get("post_url", "UNKNOWN"))
            elif env == "prod":
                raw_post_url = os.getenv("WORKFLOW_MONITORING_URL", trace_data.get("post_url", "UNKNOWN"))
            else:
                return None

            headers = {
                "Content-Type": "application/json",
                "x-api-key": os.getenv("WORKFLOW_MONITORING_API_KEY", trace_data.get("x-api-key", "UNKNOWN"))
            }

            if not trace_data.get("traceId") or raw_post_url == "UNKNOWN" or headers.get("x-api-key") == "UNKNOWN":
                return None

            return WorkflowMonitoringConfig(
                post_url=HttpUrl(raw_post_url),
                headers=headers,
                spanId=generate_span_id(),
                traceId=trace_data["traceId"],
                prevSpanId=trace_data.get("prevSpanId"),
                userId=trace_data.get("userId", os.getenv("WORKFLOW_USER_ID", "UNKNOWN")),
                projectId=trace_data.get("projectId", os.getenv("WORKFLOW_PROJECT_ID", "UNKNOWN")),
                componentName=operation_name,
                operationName=operation_name,
                log_enabled=trace_data.get("log_enabled", log_enabled),
            )
        except Exception as e:
            if log_enabled:
                logger.error(f"Error creating WorkflowMonitoringConfig: {e}")
            return None
