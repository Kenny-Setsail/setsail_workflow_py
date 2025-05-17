import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from setsail_workflow_py import workflow_entry
from setsail_workflow_py.domain.services.config_factory import ConfigFactory
from setsail_workflow_py.domain.models.workflow_monitoring_config import WorkflowMonitoringConfig
from setsail_workflow_py.application.services.workflow_monitoring_service import WorkflowMonitoringService

from pydantic import Field, HttpUrl


trace_data = {
    "enable": True,
    "traceId": "592225192fb1ac17022e80c85fb8a749",
    "prevSpanId": "3f7decc34dc8d03a",
    "userId": "202505125600020250512145500563QSLVDGS96F",
    "projectId": "mtr-kiosk-pquzibd",
    "componentName": "async_test",
    "operationName": "async_test",
    "post_url": "https://dev.setsailapi.com/workflow/v1/event",
    "log_enabled": True
}

config = WorkflowMonitoringConfig(
    post_url=HttpUrl("https://dev.setsailapi.com/workflow/v1/event"),
    headers={"Content-Type": "application/json"},
    spanId="3f7decc34dc8d03a",
    traceId="592225192fb1ac17022e80c85fb8a749",
    prevSpanId="3f7decc34dc8d03a",
    userId="202505125600020250512145500563QSLVDGS96F",
    projectId="mtr-kiosk-pquzibd",
    componentName="async_test",
    operationName="async_test",
    log_enabled=True
)

@workflow_entry(name="async_test", log_enabled=True)
async def async_function(x: int, y: int, workflow_trace_data: dict) -> int:
    return x + y

@workflow_entry(name="error_test", log_enabled=True)
async def error_function(x: int, y: int, workflow_trace_data: dict) -> int:
    raise ValueError("Something went wrong")

@workflow_entry(name="sync_test", log_enabled=True)
def sync_function(x: int, y: int, workflow_trace_data: dict) -> int:
    return x + y

@workflow_entry(name="sync_test", log_enabled=True)
def sync_function_with_error(x: int, y: int, workflow_trace_data: dict) -> int:
    raise ValueError("Something went wrong")

@workflow_entry(name="async_gen_test", log_enabled=True)
async def async_gen_function(n: int, workflow_trace_data: dict):
    for i in range(n):
        yield i

@patch("setsail_workflow_py.domain.services.config_factory.ConfigFactory.create_from_trace_data")
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_end_event", new_callable=AsyncMock)
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_start_event", new_callable=AsyncMock)
def test_workflow_entry_sync(mock_send_start, mock_send_end, mock_create_from_trace_data):
    mock_create_from_trace_data.return_value = config

    result = sync_function(2, 3, workflow_trace_data=trace_data)

    assert result == 5

    mock_send_start.assert_called_once_with(config, dict(workflow_trace_data=trace_data))
    mock_send_end.assert_called_once_with(config, 5, "SUCCESS", {})

@pytest.mark.asyncio
@patch("setsail_workflow_py.domain.services.config_factory.ConfigFactory.create_from_trace_data")
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_end_event", new_callable=AsyncMock)
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_start_event", new_callable=AsyncMock)
def test_workflow_entry_sync_error(mock_send_start, mock_send_end, mock_create_from_trace_data):
    mock_create_from_trace_data.return_value = config

    with pytest.raises(ValueError, match="Something went wrong"):
        sync_function_with_error(2, 3, workflow_trace_data=trace_data)

    mock_send_start.assert_called_once_with(config, dict(workflow_trace_data=trace_data))

    mock_send_end.assert_not_called()

@pytest.mark.asyncio
@patch("setsail_workflow_py.domain.services.config_factory.ConfigFactory.create_from_trace_data")
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_end_event", new_callable=AsyncMock)
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_start_event", new_callable=AsyncMock)
async def test_workflow_entry_async(mock_send_start, mock_send_end, mock_create_from_trace_data):
    mock_create_from_trace_data.return_value = config

    result = await async_function(2, 3, workflow_trace_data=trace_data)

    assert result == 5

    mock_send_start.assert_awaited_once_with(config, dict(workflow_trace_data=trace_data))
    mock_send_end.assert_awaited_once_with(config, 5, "SUCCESS", {})


@pytest.mark.asyncio
@patch("setsail_workflow_py.domain.services.config_factory.ConfigFactory.create_from_trace_data")
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_start_event", new_callable=AsyncMock)
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_end_event", new_callable=AsyncMock)
async def test_workflow_entry_async_error(mock_send_end, mock_send_start, mock_create_from_trace_data):
    mock_create_from_trace_data.return_value = config

    with pytest.raises(ValueError, match="Something went wrong"):
        await error_function(2, 3, workflow_trace_data=trace_data)

    mock_send_start.assert_awaited_once_with(config, dict(workflow_trace_data=trace_data))

    mock_send_end.assert_not_called()
