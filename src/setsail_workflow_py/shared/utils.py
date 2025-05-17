import uuid
import time
import inspect
from pathlib import Path
from typing import Callable, Optional


def generate_trace_id() -> str:
    return uuid.uuid4().hex


def generate_span_id() -> str:
    return uuid.uuid4().hex[:16]


def current_timestamp() -> int:
    return int(time.time() * 1000)


EXCLUDE_CLASSES = {"ProactorEventLoop", "Handle", "BaseEventLoop", "Runner"}


def get_class_name(func: Callable) -> Optional[str]:
    if hasattr(func, '__self__') and func.__self__ is not None:
        class_name = type(func.__self__).__name__
        if class_name not in EXCLUDE_CLASSES:
            return class_name

    project_root = Path.cwd().resolve()
    stack = inspect.stack()

    for frame_info in stack:
        frame = frame_info.frame
        filename = Path(frame.f_code.co_filename).resolve()

        if project_root in filename.parents:
            locals_snapshot = frame.f_locals
            instance = locals_snapshot.get('self')

            if instance is None:
                args = locals_snapshot.get('args', [])
                if args and not isinstance(args[0], (str, int, float, dict, list)):
                    instance = args[0]

            # for llm-graph
            processor = locals_snapshot.get('processor')
            if processor and hasattr(processor, '__class__'):
                return processor.__class__.__name__

            if instance:
                class_name = type(instance).__name__
                if class_name not in EXCLUDE_CLASSES:
                    return class_name

    return None
