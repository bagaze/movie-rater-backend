import uvicorn

from .app import app  # noqa: F401


def __main__():
    ''' Run the application using `poetry run start` '''
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
