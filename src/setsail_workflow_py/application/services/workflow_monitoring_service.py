import traceback
import inspect
from typing import Callable, Any, Awaitable, Union
from setsail_workflow_py.domain.events.value_object.workflow_event import WorkflowEvent, WorkflowEventPayload, WorkflowPayload
from setsail_workflow_py.domain.models.workflow_monitoring_config import WorkflowMonitoringConfig
from setsail_workflow_py.domain.services.config_factory import ConfigFactory
from setsail_workflow_py.infrastructure.http.post_client import PostClient
from setsail_workflow_py.application.services.async_gen_wrapper import MonitoredAsyncGenerator
from setsail_workflow_py.shared.utils import current_timestamp
from loguru import logger

class WorkflowMonitoringService:

    @staticmethod
    async def monitor_execution(func: Callable[..., Union[Any, Awaitable[Any]]], args: tuple, kwargs: dict, operation_name: str, log_enabled: bool) -> Union[Any, Awaitable[Any]]:
        trace_data = kwargs.get("state", {}).get("workflow_trace_data", {}) or kwargs.get("workflow_trace_data", {})
        config: WorkflowMonitoringConfig = ConfigFactory.create_from_trace_data(trace_data, operation_name, log_enabled)

        is_async_gen = inspect.isasyncgenfunction(func)
        print(f"is_async_gen: {is_async_gen}")

        if not config:
            if log_enabled:
                logger.warning("Workflow monitoring config is not available. Skipping monitoring.")

            if is_async_gen:
                async_gen = func(*args, **kwargs)
                return MonitoredAsyncGenerator(async_gen, config, on_close=None)

            return await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)

        if kwargs.get("state", {}).get("workflow_trace_data", {}):
            kwargs["state"]["workflow_trace_data"]["prevSpanId"] = config.spanId

        if kwargs.get("workflow_trace_data", {}):
            kwargs["workflow_trace_data"]["prevSpanId"] = config.spanId

        await WorkflowMonitoringService.send_start_event(config, kwargs)
        status = "SUCCESS"
        error_details = None
        result = None

        if is_async_gen:
            async_gen = func(*args, **kwargs)
            return MonitoredAsyncGenerator(async_gen, config, on_close=WorkflowMonitoringService.send_end_event)

        try:
            result = await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)
        except Exception as ex:
            status = "FAILURE"
            error_details = {
                "message": str(ex),
                "stack": traceback.format_exc(),
                "errorCode": type(ex).__name__
            }
            if log_enabled:
                logger.error(f"Error in {operation_name}: {error_details['message']}")
                logger.debug(f"Stack trace: {error_details['stack']}")

            raise ex  # Re-raise the exception to propagate it,  because this decorator should not handle it.
        finally:
            await WorkflowMonitoringService.send_end_event(config, result, status, error_details)

        return result

    @staticmethod
    async def send_start_event(config: WorkflowMonitoringConfig, kwargs):
        if config.log_enabled:
            logger.info(f"Sending start event for {config.operationName}, traceId: {config.traceId}, spanId: {config.spanId}")
        event = WorkflowEvent(
            traceId=config.traceId,
            spanId=config.spanId,
            parentSpanId=config.prevSpanId,
            componentName=config.componentName,
            operationName=config.operationName,
            timestamp=current_timestamp(),
            eventType="STEP_START",
            # data=WorkflowEventPayload(input={"kwargs": str(kwargs)}),
            data=WorkflowEventPayload(
                input={
                    "Me just": "testing"
                }
            )
        )

        payload = WorkflowPayload(
            userId=config.userId,
            projectId=config.projectId,
            event=event
        )

        await PostClient.post_event(config, payload)

    @staticmethod
    async def send_end_event(config: WorkflowMonitoringConfig, result, status, error_details):
        if config.log_enabled:
            logger.info(f"Sending end event for {config.operationName}, traceId: {config.traceId}, spanId: {config.spanId}")
        event = WorkflowEvent(
            traceId=config.traceId,
            spanId=config.spanId,
            parentSpanId=config.prevSpanId,
            componentName=config.componentName,
            operationName=config.operationName,
            timestamp=current_timestamp(),
            eventType="STEP_END",
            status=status,
            # data=WorkflowEventPayload(output=result, errorDetails=error_details),
            data=WorkflowEventPayload(
                output={
                    "Me just": "testing"
                }
            )
        )

        payload = WorkflowPayload(
            userId=config.userId,
            projectId=config.projectId,
            event=event
        )

        await PostClient.post_event(config, payload)
