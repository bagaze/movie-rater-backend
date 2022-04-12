from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.api.v1.api import api_router
from app.proxy.deps import client_session
from app.core.config import settings


def get_application():
    app = FastAPI(title=settings.PROJECT_NAME)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = get_application()


@app.on_event("startup")
async def startup_event():
    client_session.start()


@app.on_event("shutdown")
async def shutdown_event():
    await client_session.stop()


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs/")
