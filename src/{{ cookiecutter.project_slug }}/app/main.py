from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from .admin.api import v1 as admin_api_v1
from .dependencies import sessionmanager


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """

    yield

    if sessionmanager.get_engine() is not None:
        await sessionmanager.close()


app = FastAPI(title='EratoAPI', lifespan=lifespan)
app.include_router(admin_api_v1.router, prefix='/admin/api/v1')
