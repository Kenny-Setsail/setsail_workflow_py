from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Literal, Union

WorkflowEventType = Literal["STEP_START", "STEP_END", "LOG", "ERROR"]
WorkflowStatus = Literal["SUCCESS", "FAILURE"]


class ErrorDetails(BaseModel):
    message: str
    stack: Optional[str] = None
    errorCode: Optional[str] = None

class WorkflowEventPayload(BaseModel):
    input: Optional[Any] = None
    output: Optional[Any] = None
    logMessage: Optional[str] = None
    errorDetails: Optional[ErrorDetails] = None

class WorkflowEvent(BaseModel):
    traceId: str = Field(min_length=32, max_length=32)
    spanId: str = Field(min_length=16, max_length=16)
    parentSpanId: Optional[str] = Field(default=None, min_length=16, max_length=16)
    componentName: str
    operationName: str
    timestamp: int
    eventType: WorkflowEventType
    status: Optional[WorkflowStatus] = None
    data: WorkflowEventPayload
    customAttributes: Optional[Dict[str, Any]] = None

class WorkflowPayload(BaseModel):
    userId: str = Field(min_length=32, max_length=64)
    projectId: str = Field(min_length=1, max_length=64)
    event: WorkflowEvent

