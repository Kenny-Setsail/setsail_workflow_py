from typing import Callable, Any, Coroutine, Optional, TypeVar
import functools
import asyncio
import inspect
from setsail_workflow_py.domain.services.config_factory import ConfigFactory, WorkflowMonitoringConfig
from setsail_workflow_py.application.services.workflow_monitoring_service import WorkflowMonitoringService
from loguru import logger

T = TypeVar("T")
STATUS_SUCCESS = "SUCCESS"

def workflow_entry(name: str, log_enabled: bool = False) -> Callable[[Callable[..., Coroutine[Any, Any, T]]], Callable[..., Any]]:
    if not isinstance(name, str):
        raise TypeError(f"name must be str, got {type(name).__name__}")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if not callable(func):
            raise TypeError(f"object must Callable, got {type(func).__name__}")

        @functools.wraps(func)
        async def async_wrapper(
                *args: Any,
                config: Optional[WorkflowMonitoringConfig] = None,
                **kwargs: Any
        ) -> Any:
            if config:
                try:
                    await WorkflowMonitoringService.send_start_event(config, kwargs)
                except Exception as e:
                    if config.log_enabled:
                        logger.exception(f"send start event failed: {e}")

            result = await func(*args, **kwargs)  # type: ignore

            if config:
                try:
                    await WorkflowMonitoringService.send_end_event(
                        config, result, STATUS_SUCCESS, {}
                    )
                except Exception as e:
                    if config.log_enabled:
                        logger.exception(f"send end event failed: {e}")

            return result

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            config: Optional[WorkflowMonitoringConfig] = None
            trace_data = kwargs.get("workflow_trace_data")
            if isinstance(trace_data, dict) and trace_data.get("enable", False):
                config = ConfigFactory.create_from_trace_data(trace_data, name, log_enabled)
                trace_data["prevSpanId"] = config.prevSpanId

            loop = asyncio.get_event_loop()

            if inspect.iscoroutinefunction(func):
                if loop.is_running():
                    return async_wrapper(*args, config=config, **kwargs)
                else:
                    return asyncio.run(async_wrapper(*args, config=config, **kwargs))

            if config:
                if loop.is_running():
                    asyncio.create_task(_send_start_event(config, kwargs))
                else:
                    asyncio.run(_send_start_event(config, kwargs))

            result = func(*args, **kwargs)

            # 再送 end event
            if config:
                if loop.is_running():
                    asyncio.create_task(_send_end_event(config, result))
                else:
                    asyncio.run(_send_end_event(config, result))

            return result

        return wrapper

    return decorator

async def _send_start_event(config: WorkflowMonitoringConfig, context: dict[str, Any]) -> None:
    try:
        await WorkflowMonitoringService.send_start_event(config, context)
    except Exception as e:
        logger.exception("send start event failed: %s", e)

async def _send_end_event(config: WorkflowMonitoringConfig, result: Any) -> None:
    try:
        print("send end event")
        await WorkflowMonitoringService.send_end_event(config, result, STATUS_SUCCESS, {})
        print("send end event success")
    except Exception as e:
        logger.exception("send end event failed: %s", e)