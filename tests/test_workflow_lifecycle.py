import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from setsail_workflow_py import workflow_lifecycle
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

@workflow_lifecycle(log_enabled=True)
async def async_function(x: int, y: int, workflow_trace_data: dict) -> int:
    return x + y

@workflow_lifecycle(log_enabled=True)
async def error_function(x: int, y: int, workflow_trace_data: dict) -> int:
    raise ValueError("Something went wrong")

@workflow_lifecycle(log_enabled=True)
def sync_function(x: int, y: int, workflow_trace_data: dict) -> int:
    return x + y

@workflow_lifecycle(log_enabled=True)
def sync_function_with_error(x: int, y: int, workflow_trace_data: dict) -> int:
    raise ValueError("Something went wrong")

@workflow_lifecycle(log_enabled=True)
async def async_gen_function(n: int, workflow_trace_data: dict):
    for i in range(n):
        yield i

@workflow_lifecycle(log_enabled=True)
async def async_gen_function_with_error(n: int, workflow_trace_data: dict):
    for i in range(n):
        if i == 2:
            raise ValueError("Something went wrong")
        yield i

@pytest.mark.asyncio
@patch("setsail_workflow_py.domain.services.config_factory.ConfigFactory.create_from_trace_data")
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_end_event", new_callable=AsyncMock)
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_start_event", new_callable=AsyncMock)
async def test_async_function(mock_send_start_event, mock_send_end_event, mock_create_from_trace_data):
    mock_create_from_trace_data.return_value = config
    result = await async_function(1, 2, trace_data)
    assert result == 3
    mock_send_start_event.assert_called_once()
    mock_send_end_event.assert_called_once()
    assert isinstance(mock_send_end_event.call_args[0][0], WorkflowMonitoringConfig)
    assert mock_send_end_event.call_args[0][1] == 3
    assert mock_send_end_event.call_args[0][2] == "SUCCESS"

@pytest.mark.asyncio
@patch("setsail_workflow_py.domain.services.config_factory.ConfigFactory.create_from_trace_data")
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_end_event", new_callable=AsyncMock)
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_start_event", new_callable=AsyncMock)
async def test_async_function_with_error(mock_send_start_event, mock_send_end_event, mock_create_from_trace_data):
    mock_create_from_trace_data.return_value = config
    with pytest.raises(ValueError):
        await error_function(1, 2, trace_data)
    mock_send_start_event.assert_called_once()
    mock_send_end_event.assert_called_once()
    assert isinstance(mock_send_end_event.call_args[0][0], WorkflowMonitoringConfig)
    assert mock_send_end_event.call_args[0][1] is None
    assert mock_send_end_event.call_args[0][2] == "FAILURE"
    assert isinstance(mock_send_end_event.call_args[0][3], dict)

@pytest.mark.asyncio
@patch("setsail_workflow_py.domain.services.config_factory.ConfigFactory.create_from_trace_data")
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_end_event", new_callable=AsyncMock)
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_start_event", new_callable=AsyncMock)
async def test_sync_function(mock_send_start_event, mock_send_end_event, mock_create_from_trace_data):
    mock_create_from_trace_data.return_value = config
    result = sync_function(1, 2, trace_data)
    assert result == 3
    mock_send_start_event.assert_called_once()
    mock_send_end_event.assert_called_once()
    assert isinstance(mock_send_end_event.call_args[0][0], WorkflowMonitoringConfig)
    assert mock_send_end_event.call_args[0][1] == 3
    assert mock_send_end_event.call_args[0][2] == "SUCCESS"

@pytest.mark.asyncio
@patch("setsail_workflow_py.domain.services.config_factory.ConfigFactory.create_from_trace_data")
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_end_event", new_callable=AsyncMock)
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_start_event", new_callable=AsyncMock)
async def test_sync_function_with_error(mock_send_start_event, mock_send_end_event, mock_create_from_trace_data):
    mock_create_from_trace_data.return_value = config
    with pytest.raises(ValueError):
        sync_function_with_error(1, 2, trace_data)
    mock_send_start_event.assert_called_once()
    mock_send_end_event.assert_called_once()
    assert isinstance(mock_send_end_event.call_args[0][0], WorkflowMonitoringConfig)
    assert mock_send_end_event.call_args[0][1] is None
    assert mock_send_end_event.call_args[0][2] == "FAILURE"
    assert isinstance(mock_send_end_event.call_args[0][3], dict)

@pytest.mark.asyncio
@patch("setsail_workflow_py.domain.services.config_factory.ConfigFactory.create_from_trace_data")
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_end_event", new_callable=AsyncMock)
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_start_event", new_callable=AsyncMock)
async def test_async_gen_function(mock_send_start_event, mock_send_end_event, mock_create_from_trace_data):
    mock_create_from_trace_data.return_value = config
    async for item in async_gen_function(5, trace_data):
        assert item in range(5)
    mock_send_start_event.assert_called_once()
    mock_send_end_event.assert_called_once()
    assert isinstance(mock_send_end_event.call_args[0][0], WorkflowMonitoringConfig)
    assert mock_send_end_event.call_args[0][1] == 4
    assert mock_send_end_event.call_args[0][2] == "SUCCESS"
    assert mock_send_end_event.call_args[0][3] is None

@pytest.mark.asyncio
@patch("setsail_workflow_py.domain.services.config_factory.ConfigFactory.create_from_trace_data")
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_end_event", new_callable=AsyncMock)
@patch("setsail_workflow_py.application.services.workflow_monitoring_service.WorkflowMonitoringService.send_start_event", new_callable=AsyncMock)
async def test_async_gen_function_with_error(mock_send_start_event, mock_send_end_event, mock_create_from_trace_data):
    mock_create_from_trace_data.return_value = config
    with pytest.raises(ValueError):
        async for item in async_gen_function_with_error(5, trace_data):
            pass
    mock_send_start_event.assert_called_once()
    mock_send_end_event.assert_called_once()
    assert isinstance(mock_send_end_event.call_args[0][0], WorkflowMonitoringConfig)
    assert mock_send_end_event.call_args[0][1] == 1
    assert mock_send_end_event.call_args[0][2] == "FAILURE"
    assert isinstance(mock_send_end_event.call_args[0][3], dict)