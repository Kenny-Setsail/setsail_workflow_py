import asyncio
from functools import wraps
import inspect
import concurrent.futures
from typing import Callable, Any, Union, Awaitable
from loguru import logger
from setsail_workflow_py.application.services.workflow_monitoring_service import WorkflowMonitoringService
from setsail_workflow_py.shared.utils import get_class_name


def workflow_lifecycle(log_enabled: bool = False) -> Callable:
    def decorator(func: Callable[..., Union[Any, Awaitable[Any]]]) -> Callable:
        is_async_gen_func = inspect.isasyncgenfunction(func)
        is_async_func = inspect.iscoroutinefunction(func)

        async def handle_logic(args, kwargs, operation_name) -> Union[Any, Awaitable[Any]]:
            result = await WorkflowMonitoringService.monitor_execution(func, args, kwargs, operation_name, log_enabled)
            return result

        if is_async_gen_func:
            @wraps(func)
            async def async_gen_wrapper(*args, **kwargs):
                operation_name = get_class_name(func)
                result_gen = await handle_logic(args, kwargs, operation_name)
                async for item in result_gen:
                    yield item

            return async_gen_wrapper

        elif is_async_func:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                operation_name = get_class_name(func)
                return await handle_logic(args, kwargs, operation_name)

            return async_wrapper

        else:
            @wraps(func)
            def wrapper_sync(*args: Any, **kwargs: Any) -> Any:
                operation_name = get_class_name(func)

                def _run_in_thread() -> Any:
                    return asyncio.run(handle_logic(args, kwargs, operation_name))

                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(_run_in_thread)
                            return future.result()
                except RuntimeError:
                    return asyncio.run(handle_logic(args, kwargs, operation_name))
                except Exception as e:
                    if log_enabled:
                        logger.error(f"[{operation_name}] Execution failed in sync: {e}")
                    raise e # Re-raise the exception to propagate it, because this decorator should not handle it.

                try:
                    return asyncio.run(handle_logic(args, kwargs, operation_name))
                except Exception as e:
                    if log_enabled:
                        logger.error(f"[{operation_name}] Execution failed in sync: {e}")
                    return None

        return wrapper_sync

    return decorator
