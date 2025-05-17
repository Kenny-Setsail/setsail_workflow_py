import aiohttp
from loguru import logger
from setsail_workflow_py.domain.events.value_object.workflow_event import WorkflowPayload
from setsail_workflow_py.domain.models.workflow_monitoring_config import WorkflowMonitoringConfig


class PostClient:

    @staticmethod
    async def post_event(config: WorkflowMonitoringConfig, payload: WorkflowPayload) -> None:
        if not isinstance(config, WorkflowMonitoringConfig) or not isinstance(payload, WorkflowPayload):
            if config.log_enabled:
                logger.warning("Invalid config or payload. Skipping post event.")
            return

        try:
            timeout = aiohttp.ClientTimeout(total=3)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                        url=str(config.post_url),
                        json=payload.model_dump(mode="json", exclude_none=True),
                        headers=config.headers
                ) as response:
                    if response.status == 200:
                        if config.log_enabled:
                            logger.success(f"Posted event successfully: {payload.event.eventType}, traceId: {config.traceId}, spanId: {config.spanId}")
                    else:
                        if config.log_enabled:
                            logger.error(f"Failed to post event: {payload.event.eventType}, traceId: {config.traceId}, spanId: {config.spanId}, status: {response.status}")
        except Exception as e:
            if config.log_enabled:
                logger.error(f"Error posting event: {payload.eventType}, traceId: {config.traceId}, spanId: {config.spanId}, error: {str(e)}")
                logger.debug(f"Error details: {e}")
                logger.debug(f"Payload: {payload.model_dump(mode='json', exclude_none=True)}")
