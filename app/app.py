from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core import deps


def get_application():
    app = FastAPI(title=settings.PROJECT_NAME)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_event_handler("startup", deps.create_start_app_handler())
    app.add_event_handler("shutdown", deps.create_stop_app_handler())

    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = get_application()


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs/")
