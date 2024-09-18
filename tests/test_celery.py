import asyncio
from typing import Any, TYPE_CHECKING, TypeAlias

import anyio
import pytest
from celery import Celery
from celery.result import AsyncResult
from celery.worker import WorkController

from {{ cookiecutter.project_slug }}.app.tasks import celery_event_loop

if TYPE_CHECKING:
    AsyncResultType: TypeAlias = AsyncResult[Any]
else:
    AsyncResultType: TypeAlias = AsyncResult


async def wait_for_state(result: AsyncResultType, state: str, num_retries: int = 10) -> bool:
    if result.state == state:
        return True
    elif num_retries < 1:
        return False
    else:
        await anyio.sleep(0.5)
        return await wait_for_state(result, state, num_retries - 1)


@pytest.mark.anyio
async def test_async_celery_state_transition(celery_session_app: Celery, celery_session_worker: WorkController) -> None:

    async def _mul(x: int, y: int) -> int:
        await anyio.sleep(1)
        return x * y

    @celery_session_app.task(queue='default')
    def mul(x: int, y: int) -> int:
        assert celery_event_loop.is_running()
        future = asyncio.run_coroutine_threadsafe(_mul(x, y), celery_event_loop)
        return future.result()
    if reload_worker := getattr(celery_session_worker, 'reload'):  # for mypy checking
        reload_worker()
    task = mul.delay(4, 4)
    result: AsyncResult[int] = AsyncResult(task.id, app=celery_session_app)
    await wait_for_state(result, 'SENT')
    assert str(result.state) == 'SENT'

    await wait_for_state(result, 'ACCEPTED')
    assert str(result.state) == 'ACCEPTED'

    await wait_for_state(result, 'SUCCESS')
    assert result.state == 'SUCCESS'

    assert result.result == 16


@pytest.mark.anyio
async def test_async_celery_exception(celery_session_app: Celery, celery_session_worker: WorkController) -> None:

    async def _div(x: float, y: float) -> float:
        await anyio.sleep(1)
        return x / y

    @celery_session_app.task(queue='default')
    def div(x: float, y: float) -> float:
        assert celery_event_loop.is_running()
        future = asyncio.run_coroutine_threadsafe(_div(x, y), celery_event_loop)
        return future.result()

    if reload_worker := getattr(celery_session_worker, 'reload'):  # for mypy checking
        reload_worker()

    task = div.delay(4.0, 0.0)
    result: AsyncResult[int] = AsyncResult(task.id, app=celery_session_app)

    await wait_for_state(result, 'FAILURE')
    assert result.state == 'FAILURE'

    assert isinstance(result.result, ZeroDivisionError)
