import asyncio
import traceback
from typing import AsyncGenerator, Callable, Optional, Any, Awaitable
from setsail_workflow_py.domain.models.workflow_monitoring_config import WorkflowMonitoringConfig
from loguru import logger

class MonitoredAsyncGenerator:
    def __init__(self, gen: AsyncGenerator, config: WorkflowMonitoringConfig | None, on_close: Callable[[Any, Any, str, Optional[dict]], Awaitable[None]] | None = None):
        self.gen = gen
        self.config = config
        self.on_close = on_close
        self.status = "SUCCESS"
        self.error_details = None
        self.last_value = None

    async def __aiter__(self):
        try:
            async for item in self.gen:
                self.last_value = item
                yield item
        except Exception as ex:
            self.status = "FAILURE"
            self.error_details = {
                "message": str(ex),
                "stack": traceback.format_exc(),
                "errorCode": type(ex).__name__
            }
            if self.config and self.config.log_enabled:
                logger.error(f"Error in async generator: {self.error_details['message']}")
                logger.debug(f"Stack trace: {self.error_details['stack']}")
            raise
        finally:
            if self.config and self.config.log_enabled:
                logger.info(f"Closing async generator for {self.config.operationName}, traceId: {self.config.traceId}, spanId: {self.config.spanId}")
            if self.on_close:
                await self.on_close(self.config, self.last_value, self.status, self.error_details)

