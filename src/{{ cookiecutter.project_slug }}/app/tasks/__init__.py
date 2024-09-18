import asyncio
from asyncio import AbstractEventLoop
from threading import Thread
from typing import Any, Optional, TYPE_CHECKING

from celery import current_app
from celery.app.task import Task
from celery.signals import after_task_publish, task_prerun, worker_process_init, worker_process_shutdown

celery_event_loop: AbstractEventLoop = asyncio.new_event_loop()
celery_event_loop_thread: Optional[Thread] = None

if TYPE_CHECKING:
    TaskType = type[Task[Any, Any]]
else:
    TaskType = Task

@worker_process_init.connect
def configure_event_loop(**_kwargs: dict[str, Any]) -> None:
    global celery_event_loop_thread
    celery_event_loop_thread = Thread(target=celery_event_loop.run_forever, daemon=True)
    celery_event_loop_thread.start()


@worker_process_shutdown.connect
def shutdown_event_loop(**_kwargs: dict[str, Any]) -> None:
    if celery_event_loop_thread is not None:
        celery_event_loop.call_soon_threadsafe(lambda ev: ev.stop(), celery_event_loop)
        celery_event_loop_thread.join()


@after_task_publish.connect
def set_sent_state(sender: Optional[str] = None,
                   headers: Optional[dict[str, Any]] = None,
                   **_kwargs: dict[str, Any]) -> None:
    if sender is not None and (task := current_app.tasks.get(sender)) is not None:
        backend = task.backend
    else:
        backend = current_app.backend
    if headers is not None and 'id' in headers:
        backend.store_result(headers['id'], None, "SENT")


@task_prerun.connect
def set_accepted_state(task_id: str, task: TaskType, **_kwargs: dict[str, Any]) -> None:
    backend = current_app.backend if task is None else task.backend
    if store_result := getattr(backend, 'store_result'):  # for mypy checking
        store_result(task_id, None, "ACCEPTED")
