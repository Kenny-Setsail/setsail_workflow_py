from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, Any, Optional


class WorkflowMonitoringConfig(BaseModel):
    post_url: HttpUrl
    headers: Dict[str, str] = {}
    traceId: str = Field(min_length=32, max_length=32)
    spanId: str = Field(min_length=16, max_length=16)
    prevSpanId: Optional[str] = Field(default=None, min_length=16, max_length=16)
    userId: str = Field(min_length=32, max_length=64)
    projectId: str = Field(min_length=1, max_length=64)
    componentName: str = Field(min_length=1, max_length=64)
    operationName: str = Field(min_length=1, max_length=64)
    log_enabled: bool = Field(default=False)
